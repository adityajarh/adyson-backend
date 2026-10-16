from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests as g_requests
from config import GOOGLE_CLIENT_ID, ADMIN_EMAIL
from database import get_db
from models import User, AllowedEmail
from security import create_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class GoogleIn(BaseModel):
    id_token: str


def user_out(u: User) -> dict:
    return {
        "id": u.id,
        "email": u.email,
        "name": u.name,
        "picture": u.picture,
        "is_admin": u.is_admin,
    }


@router.post("/google")
def google_login(body: GoogleIn, db: Session = Depends(get_db)):
    try:
        info = id_token.verify_oauth2_token(
            body.id_token,
            g_requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10,
        )
    except ValueError:
        raise HTTPException(401, "Google token invalid hai")
    if not info.get("email_verified"):
        raise HTTPException(401, "Email verified nahi hai")

    email = info["email"].strip().lower()
    is_admin = email == ADMIN_EMAIL

    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(email=email)
        db.add(user)
    user.name = info.get("name")
    user.picture = info.get("picture")
    user.is_admin = is_admin
    db.commit()
    db.refresh(user)
    return {"token": create_token(user.id), "user": user_out(user)}


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return user_out(user)