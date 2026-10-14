from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from routers.songs import song_out
from security import get_current_user
from services import recommend

router = APIRouter(tags=["home"])


@router.get("/home")
def home(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    def out(songs):
        return [song_out(s) for s in songs]

    return {
        "user": {"name": user.name, "picture": user.picture},
        "recently_played": out(recommend.recently_played(db, user.id)),
        "for_you": out(recommend.for_you(db, user.id)),
        "most_played": out(recommend.most_played(db, user.id)),
        "trending": out(recommend.trending(db)),
    }