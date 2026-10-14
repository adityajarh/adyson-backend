from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Play, Song, User
from security import get_current_user

router = APIRouter(prefix="/plays", tags=["plays"])


@router.post("/{song_id}")
def log_play(song_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.get(Song, song_id):
        raise HTTPException(404, "Song nahi mila")
    db.add(Play(user_id=user.id, song_id=song_id))
    db.commit()
    return {"ok": True}