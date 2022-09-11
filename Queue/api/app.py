import celery.states as states
from flask import Flask, Response
from flask import jsonify,request,make_response
from worker import celery
from flask_cors import CORS
from celery import Celery
import os
import pymongo
from pymongo import MongoClient

dev_mode = True
app = Flask(__name__)
app.config.from_object('config.Config')
CORS(app)

def get_mongo_collection():
    CONNECTION_STRING = app.config['MONGO_DB_URI']
    client = MongoClient(CONNECTION_STRING)
    return client[app.config['MONGO_DB_NAME']]

@app.route('/queue/scrap/video',methods=["POST"])
def queueForScrapVideo():
    result = {}
    try:
        json = request.json
        videoLinks = json
        mongo = get_mongo_collection()
        collection = mongo["videoAndComments"]
        myquery = {"id": int(json["id"])}

        if collection.find_one(myquery) is not None:
            newvalues = {"$set": {"queueStatus": 0}}
            collection.update_one(myquery, newvalues)
        else:
            tmp = {}
            tmp["id"] = int(json["id"])
            tmp["queueStatus"] = 0
            collection.insert_one(tmp)

        task = celery.send_task('tasks.downloadAndUploadYoutubeVideoToS3', args=[videoLinks], kwargs={})

        result["status"] = True
        result["message"] = f"Successfully triggered queue"
        return make_response(jsonify(result),200)

    except Exception as e:
        result["status"] = False
        result["message"] = f"Something went wrong while video queue e-{e}"
        return make_response(jsonify(result),500)


@app.route('/queue/scrap/comment',methods=["POST"])
def queueForScrapComment():
    result = {}
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            json = request.json
            videoLinks = json["videoLinks"]
        
        task = celery.send_task('tasks.downloadCommentsFromYoutube', args=[videoLinks], kwargs={})
        
        result["status"] = True
        result["message"] = f"Successfully triggered queue"
        return make_response(jsonify(result),200)

    except Exception as e:
        result["status"] = False
        result["message"] = f"Something went wrong while video queue e-{e}"
        return make_response(jsonify(result),500)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
