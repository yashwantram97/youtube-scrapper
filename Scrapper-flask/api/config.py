class Config:
    SQLALCHEMY_DATABASE_URI = 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MONGO_DB_URI = 
    MONGO_DB_NAME = 
    AWS_ACCESS_KEY_ID = 
    AWS_SECRET_ACCESS_KEY = 
    BUCKETNAME = 
    QUEUE_URL_COMMENT = '{your ip}/queue/scrap/comment'
    QUEUE_URL_VIDEO = '{your ip}/queue/scrap/video'

    # docker run -p 4444:4444 selenium/standalone-chrome
