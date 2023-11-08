from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models
from .routers import post, user, vote
from . import auth

# Creates all tables. Commented after implementing alembic
# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# origins = ["https://www.google.com"]
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router)
app.include_router(post.router)
app.include_router(vote.router)
app.include_router(auth.router)

@app.get('/test')
def test(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts



