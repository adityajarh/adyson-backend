from datetime import datetime, timedelta
from sqlalchemy import desc, func
from sqlalchemy.orm import Session
from models import Play, Song


def _songs_by_ids(db: Session, ids: list) -> list:
    if not ids:
        return []
    found = {s.id: s for s in db.query(Song).filter(Song.id.in_(ids)).all()}
    return [found[i] for i in ids if i in found]


def recently_played(db: Session, user_id: int, limit: int = 10) -> list:
    rows = (
        db.query(Play.song_id, func.max(Play.played_at).label("last"))
        .filter(Play.user_id == user_id)
        .group_by(Play.song_id)
        .order_by(desc("last"))
        .limit(limit)
        .all()
    )
    return _songs_by_ids(db, [r[0] for r in rows])


def most_played(db: Session, user_id: int, limit: int = 10) -> list:
    rows = (
        db.query(Play.song_id, func.count(Play.id).label("n"))
        .filter(Play.user_id == user_id)
        .group_by(Play.song_id)
        .order_by(desc("n"))
        .limit(limit)
        .all()
    )
    return _songs_by_ids(db, [r[0] for r in rows])


def trending(db: Session, days: int = 7, limit: int = 10) -> list:
    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Play.song_id, func.count(Play.id).label("n"))
        .filter(Play.played_at >= since)
        .group_by(Play.song_id)
        .order_by(desc("n"))
        .limit(limit)
        .all()
    )
    return _songs_by_ids(db, [r[0] for r in rows])


def for_you(db: Session, user_id: int, limit: int = 10) -> list:
    stats = (
        db.query(Song.artist, Song.genre, func.count(Play.id))
        .join(Play, Play.song_id == Song.id)
        .filter(Play.user_id == user_id)
        .group_by(Song.artist, Song.genre)
        .all()
    )
    artist_w, genre_w = {}, {}
    for artist, genre, count in stats:
        artist_w[artist] = artist_w.get(artist, 0) + count
        if genre:
            genre_w[genre] = genre_w.get(genre, 0) + count

    played = [r[0] for r in db.query(Play.song_id).filter(Play.user_id == user_id).distinct().all()]
    candidates = db.query(Song).filter(Song.id.notin_(played)).all()
    candidates.sort(
        key=lambda s: (artist_w.get(s.artist, 0) * 2 + genre_w.get(s.genre, 0), s.id),
        reverse=True,
    )
    return candidates[:limit]