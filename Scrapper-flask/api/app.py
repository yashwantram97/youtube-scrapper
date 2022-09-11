import os
import time
from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from model import db, ChannelSearch, VideoDetails
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import pymongo
from pymongo import MongoClient
from pytube import YouTube
import boto3
import json
import requests

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = app.config['SQLALCHEMY_DATABASE_URI']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = app.config['SQLALCHEMY_TRACK_MODIFICATIONS']

s3_client = boto3.client('s3', aws_access_key_id=app.config['AWS_ACCESS_KEY_ID'],aws_secret_access_key=app.config['AWS_SECRET_ACCESS_KEY'])
bucketName = app.config['BUCKETNAME']

db.init_app(app)
migrate = Migrate(app, db)

options = webdriver.ChromeOptions()
options.add_argument('--headless') 

def get_mongo_db():

    CONNECTION_STRING = app.config['MONGO_DB_URI']
    client = MongoClient(CONNECTION_STRING)
    return client[app.config['MONGO_DB_NAME']]

def fetch_youtube_video_details(channelName, wd, videoCount, channel_search_id):

    def mapYoutubeObjects(link):
        link = link.get_attribute("href")
        yt = YouTube(link)
        tmp = {}
        tmp["video_link"] = link
        tmp["title"], tmp["thumbnail_url"], tmp["description"], tmp["views"], tmp["published_date"], tmp["channel_search_id"] = yt.title, yt.thumbnail_url, yt.description, yt.views, yt.publish_date, channel_search_id
        return VideoDetails(**tmp)

    result = []
    search_url = f"https://www.youtube.com/c/{channelName}/videos?view=0"
    if requests.get(search_url).status_code == 404:
        search_url = f"https://www.youtube.com/user/{channelName}/videos?view=0"

    wd.get(search_url)
    prevContentLength = 0
    while True:
        scroll_height = 1000
        document_height_before = wd.execute_script("return document.documentElement.scrollHeight")
        wd.execute_script(f"window.scrollTo(0, {document_height_before + scroll_height});")
        time.sleep(1.5)
        document_height_after = wd.execute_script("return document.documentElement.scrollHeight")
        acontents = wd.find_elements(By.ID, 'thumbnail')
        if document_height_after == document_height_before or len(acontents) > videoCount or prevContentLength == len(acontents):
            break
        prevContentLength = len(acontents)
    
    result = list(map(mapYoutubeObjects, acontents[1:videoCount]))
    return result

def row2dict(row,collection):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))

    myquery = {"id": int(d["id"])}
    obj = collection.find_one(myquery)
    if obj is not None and len(obj) > 0:
        if "queueStatus" in obj:
            d["video_status"] = obj["queueStatus"]
        else:
            d["video_status"] = -1
    else:
        d["video_status"] = -1
    return d

def call_comment_queue(payload):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    payload = json.dumps(payload)
    r = requests.post(app.config['QUEUE_URL_COMMENT'], data=payload, headers=headers)
    print(r)

    
@app.route('/scrap', methods=['POST'])
def scrap():
    result = {}

    try:
        json = request.json
        channel_name = json["channelName"]
        video_count = json["videoCount"] + 1
        wd = None
        #wd = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
        wd = webdriver.Remote("http://selenium:4444/wd/hub", options=options)
        channel_search = ChannelSearch(channel_name = channel_name)
        db.session.add(channel_search)
        db.session.commit()
        db.session.refresh(channel_search)
        video_links = fetch_youtube_video_details(channel_name, wd, video_count, channel_search.id)
        db.session.add_all(video_links)
        db.session.commit()
        wd.quit()
        queue_link = []
        for video_link in video_links:
            db.session.refresh(video_link)
            tmp = {}
            tmp["id"]=video_link.id
            tmp["link"]=video_link.video_link
            queue_link.append(tmp)
        # Queue should happen here
        if len(queue_link) > 0:
            call_comment_queue(queue_link)
        result["id"] = channel_search.id
        result["message"] = "Successfully scrapped data"
        result["status"] = True
        result["length"] = len(video_links)

    except Exception as e:
        if wd is not None:
            wd.quit()
        result["message"] = f"Something went wrong. Please try later.{e}"
        result["status"] = False

    return make_response(jsonify(result),200)
    
@app.route('/queue/data',methods=["GET"])
def get_comment_by_video_id():
    mongo = get_mongo_db()
    args = request.args
    collection = mongo["videoAndComments"]
    myquery = {"id": int(args.get('id'))}
    obj = collection.find_one(myquery)
    result = {}
    if args.get('data') == 'comment':
        if obj is not None:
            comment = obj["comments"]
            result["data"] = comment
            result["status"] = True
            result["message"] = "Successfully fetched comments"
        else:
            result["message"] = "No comments for the video"
            result["status"] = False
    else:
        if "videoFileName" in obj:
            s3_key_name = obj["videoFileName"]
            response = s3_client.generate_presigned_url('get_object',Params={'Bucket': bucketName,'Key': s3_key_name},ExpiresIn='120')
            result["data"] = response
            result["status"] = True
        else:
            result["message"] = "Download in queue. Please try later."
            result["status"] = False
    
    return make_response(jsonify(result),200)

@app.route('/fetch/video_details',methods=["GET"])
def get_scrapped_details():

    mongo = get_mongo_db()
    args = request.args
    collection = mongo["videoAndComments"]
    args = request.args
    channel_search_id = args.get('channel_id')
    scrapped_datas = VideoDetails.query.filter_by(channel_search_id=int(channel_search_id)).all()
    result_data = []
    for row in scrapped_datas:
        result_data.append(row2dict(row,collection))
    result = {}
    if len(result_data) > 0:
        result["data"] = result_data
        result["status"] = True
        result["message"] = "Successfully fetched scrapped data"
    else:
        result["message"] = "Something went wrong"
        result["status"] = False

    return make_response(jsonify(result),200)

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=8000)