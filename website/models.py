from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy.types import JSON

class Anime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer, unique=True, nullable=False)
    mean = db.Column(db.Float)
    studio = db.Column(db.String(150))
    related_anime = db.Column(JSON)
    num_list_users = db.Column(db.Integer)
    genres = db.Column(JSON)
    synopsis = db.Column(db.String(1000))
    start_date = db.Column(db.String(150))
    media_type = db.Column(db.String(150))

    title = db.Column(db.String(150))
    picture = db.Column(db.String(150))
    
    user_ratings = db.relationship('UserAnime', back_populates='anime', cascade='all, delete-orphan')

class Manga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mal_id = db.Column(db.Integer, unique=True, nullable=False)
    mean = db.Column(db.Float)
    related_manga = db.Column(JSON)
    num_list_users = db.Column(db.Integer)
    genres = db.Column(JSON)
    synopsis = db.Column(db.String(1000))
    title = db.Column(db.String(150))
    picture = db.Column(db.String(150))
    start_date = db.Column(db.String(150))
    
    user_ratings = db.relationship('UserManga', back_populates='manga', cascade='all, delete-orphan')

class UserAnime(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(150))
    score = db.Column(db.Integer)
    updated_at = db.Column(db.String(300))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    anime_id = db.Column(db.Integer, db.ForeignKey('anime.id'), nullable=False)

    user = db.relationship('User', back_populates='anime_list')
    anime = db.relationship('Anime', back_populates='user_ratings')

    __table_args__ = (db.UniqueConstraint('user_id', 'anime_id'),)


class UserManga(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150))
    picture = db.Column(db.String(150))
    status = db.Column(db.String(150))
    score = db.Column(db.Integer)
    updated_at = db.Column(db.String(300))
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    manga_id = db.Column(db.Integer, db.ForeignKey('manga.id'), nullable=False)

    user = db.relationship('User', back_populates='manga_list')
    manga = db.relationship('Manga', back_populates='user_ratings')

    __table_args__ = (db.UniqueConstraint('user_id', 'manga_id'),)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, unique=True)
    mal_username = db.Column(db.String(150), unique=True)
    mal_access_token = db.Column(db.String(500))
    mal_refresh_token = db.Column(db.String(500))
    picture = db.Column(db.String(500))
    mal_joined_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    mean_score = db.Column(db.Integer)
    num_days = db.Column(db.Float)

    
    anime_list = db.relationship('UserAnime', back_populates='user', cascade='all, delete-orphan')
    manga_list = db.relationship('UserManga', back_populates='user', cascade='all, delete-orphan')