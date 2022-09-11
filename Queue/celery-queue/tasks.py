import os
import time
from celery import Celery
from pytube import YouTube
from flask import Flask
import boto3
import pymongo
from pymongo import MongoClient
import googleapiclient.discovery

cel = Flask(__name__)
cel.config.from_object('config.Config')

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
SAVE_PATH = "/video"
bucketName = cel.config['BUCKETNAME']

s3 = boto3.resource(
    service_name='s3',
    region_name=cel.config['AWS_REGION'],
    aws_access_key_id=cel.config['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=cel.config['AWS_SECRET_ACCESS_KEY']
)
youtubeAPIKey = cel.config['YOUTUBE_API_KEY']

def get_mongo_collection():
    CONNECTION_STRING = cel.config['MONGO_DB_URI']
    client = MongoClient(CONNECTION_STRING)
    return client[cel.config['MONGO_DB_NAME']]

def build_youtube(API_KEY):
    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=API_KEY)
    return youtube

def search_comments(youtube, video_id, page_token):
    request = youtube.commentThreads().list(
        part="id,snippet,replies",
        videoId=video_id,
        pageToken=page_token
    )

    response = request.execute()
    return response

def process_comments_response(response, video):
    next_page_token = response.get('nextPageToken')
    result = []
    for i, item in enumerate(response["items"]):
        video_id = video
        comment = item["snippet"]["topLevelComment"]
        comment_id = comment["id"]
        author = comment["snippet"]["authorDisplayName"]
        comment_text = comment["snippet"]["textDisplay"]
        comment_likes = comment["snippet"]["likeCount"]
        created_at = comment["snippet"]["publishedAt"]
        updated_at = comment["snippet"]["updatedAt"]
        reply_count = item["snippet"]["totalReplyCount"]
        reply_comments = []
        if reply_count > 0 and "replies" in item:
            replies = item["replies"]["comments"]
            for reply in replies:
                tmp = {}
                tmp["id"] = reply["id"]
                tmp["authorDisplayName"] = reply["snippet"]["authorDisplayName"]
                tmp["replyText"] = reply["snippet"]["textDisplay"]
                tmp["likeCount"] = reply["snippet"]["likeCount"]
                tmp["created_at"] = reply["snippet"]["publishedAt"]
                tmp["updated_at"] = reply["snippet"]["updatedAt"]

                reply_comments.append(tmp)
        result.append(
            {
                'comment_id':comment_id,
                'author': author,
                'comment_text': comment_text,
                'comment_likes': comment_likes,
                'reply_count':reply_count,
                'created_at':created_at,
                'updated_at':updated_at,
                'replies': reply_comments
            }
        )

    return next_page_token, result

def fetchAllComments(link):

    video_id = link.split("/")[-1] if "shorts" in link else link.split("?v=")[-1]
    next_page = None
    youtube = build_youtube(youtubeAPIKey)
    comments = []
    while True:
        response = search_comments(youtube, video_id, next_page)
        next_page, result = process_comments_response(response, video_id)
        comments += result
        if not next_page:
            break

    return comments

def downloadVideoAndSaveTos3(link):

    yt = YouTube(link)
    stream = yt.streams.first()
    file_path = stream.download(SAVE_PATH)
    file_name = file_path.split("/")[-1]

    data = open(f"{SAVE_PATH}/{file_name}", 'rb')
    s3.Bucket(bucketName).put_object(Key=file_name, Body=data)
    data.close()

    if os.path.exists(f"{SAVE_PATH}/{file_name}"):
        os.remove(f"{SAVE_PATH}/{file_name}")
    else:
        print("File not present")
        
    return file_name    

@celery.task(name='tasks.downloadAndUploadYoutubeVideoToS3')
def downloadAndUploadYoutubeVideoToS3(videoLinks):
    
    collection = get_mongo_collection()
    collection = collection["videoAndComments"]
    myquery = {"id": videoLinks["id"]}
    if collection.find_one(myquery) is not None:
        s3FileName = downloadVideoAndSaveTos3(videoLinks["link"])
        newvalues = {"$set": {"videoFileName": s3FileName,"queueStatus":1}}
        collection.update_one(myquery, newvalues)
    else:
        tmp = {}
        tmp["id"] = videoLinks["id"]
        tmp["videoFileName"] = s3FileName
        collection.insert_one(tmp)

@celery.task(name='tasks.downloadCommentsFromYoutube')
def downloadCommentsFromYoutube(videoLinks):
    
    collection = get_mongo_collection()
    collection = collection["videoAndComments"]

    for link in videoLinks:
        tmp = {}
        tmp["id"] = link["id"]
        tmp["comments"] = fetchAllComments(link["link"])
        collection.insert_one(tmp)