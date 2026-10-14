import io
import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile
from mutagen import File as MutagenFile
from sqlalchemy.orm import Session
from database import get_db
from models import Song, User
from security import get_current_user, require_admin
from services import storage

router = APIRouter(prefix="/songs", tags=["songs"])

AUDIO_TYPES = {
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
}
MAX_BYTES = 50 * 1024 * 1024


def song_out(s: Song) -> dict:
    return {
        "id": s.id,
        "title": s.title,
        "artist": s.artist,
        "genre": s.genre,
        "duration": s.duration,
        "url": storage.public_url("songs", s.audio_path),
        "cover": storage.public_url("covers", s.cover_path) if s.cover_path else None,
    }


def read_meta(data: bytes, fallback_title: str):
    title, artist, genre, duration, cover = fallback_title, "Unknown Artist", None, 0.0, None
    try:
        easy = MutagenFile(io.BytesIO(data), easy=True)
        if easy is not None:
            duration = float(easy.info.length or 0)
            title = (easy.get("title") or [title])[0]
            artist = (easy.get("artist") or [artist])[0]
            genre = (easy.get("genre") or [None])[0]
    except Exception:
        pass
    try:
        raw = MutagenFile(io.BytesIO(data))
        if raw is not None:
            if getattr(raw, "pictures", None):
                cover = raw.pictures[0].data
            elif raw.tags:
                for k in raw.tags.keys():
                    if str(k).startswith("APIC"):
                        cover = raw.tags[k].data
                        break
                if cover is None and "covr" in raw.tags:
                    cover = bytes(raw.tags["covr"][0])
    except Exception:
        pass
    return title, artist, genre, duration, cover


@router.get("")
def list_songs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    songs = db.query(Song).order_by(Song.id.desc()).all()
    return [song_out(s) for s in songs]


@router.post("/upload")
def upload_songs(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin),
):
    added, skipped = [], []
    for f in files:
        name = f.filename or ""
        ext = os.path.splitext(name)[1].lower()
        if ext not in AUDIO_TYPES:
            skipped.append({"file": name, "reason": "format supported nahi hai"})
            continue
        data = f.file.read()
        if len(data) > MAX_BYTES:
            skipped.append({"file": name, "reason": "50MB se badi hai"})
            continue

        title, artist, genre, duration, cover = read_meta(data, os.path.splitext(name)[0])
        audio_path = f"{uuid.uuid4().hex}{ext}"
        cover_path = None
        try:
            storage.upload("songs", audio_path, data, AUDIO_TYPES[ext])
            if cover:
                is_png = cover[:8] == b"\x89PNG\r\n\x1a\n"
                cover_path = f"{uuid.uuid4().hex}{'.png' if is_png else '.jpg'}"
                storage.upload("covers", cover_path, cover, "image/png" if is_png else "image/jpeg")
        except RuntimeError as e:
            skipped.append({"file": name, "reason": str(e)})
            continue

        song = Song(
            title=title, artist=artist, genre=genre, duration=duration,
            audio_path=audio_path, cover_path=cover_path,
        )
        db.add(song)
        db.commit()
        db.refresh(song)
        added.append(song_out(song))
    return {"added": added, "skipped": skipped}