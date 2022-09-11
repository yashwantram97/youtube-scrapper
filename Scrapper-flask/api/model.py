from sqlalchemy.dialects.postgresql import BIGINT, TEXT
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChannelSearch(db.Model):

    id = db.Column(BIGINT, primary_key=True)
    channel_name = db.Column(db.String, nullable=False)
    channel_subscribers = db.Column(db.String)
    author_profile = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=db.func.now())

    video_details = db.relationship('VideoDetails', backref='channel_search')

class VideoDetails(db.Model):

    id = db.Column(BIGINT, primary_key=True)
    video_link = db.Column(db.String)
    title = db.Column(db.String, nullable=False)
    thumbnail_url = db.Column(db.String, nullable=False)
    description = db.Column(db.TEXT, nullable=False)
    views = db.Column(BIGINT, nullable=False)
    published_date = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now())

    channel_search_id = db.Column(BIGINT, db.ForeignKey('channel_search.id', ondelete="CASCADE"))
