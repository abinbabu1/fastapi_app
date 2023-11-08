from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List, Optional
from .. import schemas, models, oauth2
from ..database import get_db

router = APIRouter(prefix='/posts', tags=['Posts'])

# @router.get('/latest')
# def get_latest_post():
#     cursor.execute("""SELECT * FROM posts ORDER BY created_at DESC LIMIT 1;""")
#     latest_post = cursor.fetchone()
#     return {
#         "data": latest_post
#     }

# Get post with id by currently logged in user
@router.get('/me/{id}', response_model=schemas.PostResponse)
def post_user(id: int, db: Session = Depends(get_db), 
         current_user: str = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id, 
                                        models.Post.owner_id == current_user.id).first() # type: ignore
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} by user {current_user.id} not found") # type: ignore
    return post
    # Or use similar code in delete logic

# Get all posts by currently logged in user
@router.get('/me', response_model=List[schemas.PostResponse])
def get_posts_user(db: Session = Depends(get_db), 
              current_user: str = Depends(oauth2.get_current_user)):
    all_posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # type: ignore
    return all_posts

@router.get('/{id}', response_model=schemas.PostVoteResponse)
def post(id: int, db: Session = Depends(get_db), 
         current_user: str = Depends(oauth2.get_current_user)):
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    return post

@router.get('/', response_model=List[schemas.PostVoteResponse])
# @router.get('/')
def get_posts(db: Session = Depends(get_db), limit: int = 10, 
              skip: int = 0, search: Optional[str] = ''):
    # Validation for limit -> shouldn't be 0 or negative
    # all_posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all() 
    # all_posts = db.query(models.Post).all() 
    
    # Add vote of posts -> join
    all_posts = db.query(models.Post, func.count(models.Vote.post_id).label('votes')).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
        models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # all_posts = list ( map (lambda x : x._mapping, all_posts) )
    return all_posts


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: str = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id = current_user.id, **post.model_dump()) # type: ignore
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db), 
                current_user: str = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
        
    if not post.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    if post.first().owner_id != current_user.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"You are not authorized to delete this post")
    post.delete(synchronize_session=False)
    db.commit()
        
@router.put('/{id}', status_code=status.HTTP_204_NO_CONTENT)
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user: str = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    result = post_query.first()
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id {id} not found")
    if result.owner_id != current_user.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, 
                            detail=f"You are not authorized to update this post")
    post_query.update(post.model_dump(), synchronize_session=False) # type: ignore
    db.commit()