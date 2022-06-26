from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db, engine

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/posts")
def get_all_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/")
def create_post(post: schemas.PostBase, db: Session = Depends(get_db)):
    print(post)
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post
