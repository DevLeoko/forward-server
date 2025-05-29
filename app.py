from fastapi import FastAPI, HTTPException, Header, Request, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os
import time

load_dotenv()

DATABASE_URL = "sqlite:///./redirects.db"
API_KEY = os.getenv("API_KEY")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class Redirect(Base):
    __tablename__ = "redirects"
    path = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    # Unix timestamp; None means permanent
    expires_at = Column(Integer, nullable=True)


Base.metadata.create_all(bind=engine)

app = FastAPI()


class CreateRequest(BaseModel):
    path: str
    url: str
    ttlSeconds: int  # -1 for no expiration


class DeleteRequest(BaseModel):
    path: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def authorize(authorization: Optional[str] = Header(None)):
    if authorization != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.post("/create", dependencies=[Depends(authorize)])
def create_redirect(req: CreateRequest, db: Session = Depends(get_db)):
    expires_at = int(time.time()) + \
        req.ttlSeconds if req.ttlSeconds > 0 else None
    redirect = db.query(Redirect).filter(Redirect.path == req.path).first()
    if redirect:
        redirect.url = req.url
        redirect.expires_at = expires_at
    else:
        redirect = Redirect(path=req.path, url=req.url, expires_at=expires_at)
        db.add(redirect)
    db.commit()
    return {"message": f"Redirect for '{req.path}' set to '{req.url}'"}


@app.post("/delete", dependencies=[Depends(authorize)])
def delete_redirect(req: DeleteRequest, db: Session = Depends(get_db)):
    redirect = db.query(Redirect).filter(Redirect.path == req.path).first()
    if redirect:
        db.delete(redirect)
        db.commit()
        return {"message": f"Redirect for '{req.path}' deleted"}
    raise HTTPException(status_code=404, detail="Redirect not found")


@app.get("/{path:path}")
def handle_redirect(path: str, db: Session = Depends(get_db)):
    if path == "favicon.ico":
        raise HTTPException(status_code=404)
    redirect = db.query(Redirect).filter(Redirect.path == path).first()
    current_time = int(time.time())
    if redirect and (redirect.expires_at is None or redirect.expires_at > current_time):
        return RedirectResponse(redirect.url)
    with open("static/not_found.html", encoding="utf-8") as f:
        return HTMLResponse(content=f.read(), status_code=404)
