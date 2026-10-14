from fastapi import FastAPI
from sqlalchemy import text
from database import Base, engine
import models  # noqa: F401

app = FastAPI(title="Adyson API")

from routers import auth
app.include_router(auth.router)

from routers import songs
app.include_router(songs.router)

from routers import plays, home
app.include_router(plays.router)
app.include_router(home.router)

Base.metadata.create_all(bind=engine)


@app.get("/")
def health():
    return {"status": "ok", "app": "Adyson"}


@app.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("select 1"))
    return {"db": "ok"}