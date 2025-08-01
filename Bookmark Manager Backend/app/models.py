from app.database import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    bookmarks = db.relationship('Bookmark', backref='owner', lazy=True)

class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(512), nullable=False)
    title = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    visits = db.Column(db.Integer, default=0)
    tags = db.relationship('Tag', secondary='bookmark_tags', backref=db.backref('bookmarks', lazy=True), viewonly=True)
     
    bookmark_tags = db.relationship("BookmarkTag", cascade="all, delete-orphan", backref="bookmark")
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
class BookmarkTag(db.Model):
    __tablename__ = 'bookmark_tags'
    bookmark_id = db.Column(db.Integer, db.ForeignKey('bookmark.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
    order = db.Column(db.Integer, default=0)  
    
    tag = db.relationship(Tag, backref=db.backref('bookmark_tags', lazy=True))