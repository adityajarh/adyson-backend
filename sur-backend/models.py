from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    name = Column(String(200))
    picture = Column(String(500))
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AllowedEmail(Base):
    __tablename__ = "allowed_emails"
    email = Column(String(200), primary_key=True)

class Song(Base):
    __tablename__ = "songs"
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    artist = Column(String(200), default="Unknown Artist")
    genre = Column(String(100))
    duration = Column(Float, default=0)
    audio_path = Column(String(300), nullable=False)
    cover_path = Column(String(300))
    created_at = Column(DateTime, default=datetime.utcnow)


class Play(Base):
    __tablename__ = "plays"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    song_id = Column(Integer, ForeignKey("songs.id"), index=True)
    played_at = Column(DateTime, default=datetime.utcnow)