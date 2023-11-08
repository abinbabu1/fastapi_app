from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(prefix='/vote', tags=['Vote'])

@router.post('/', status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), 
         current_user: str = Depends(oauth2.get_current_user)):
        
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id) # type: ignore
    vote_found = vote_query.first()
    if vote.dir == 1:
        if vote_found:
            # User has already voted for this post, Raising exception
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, 
                                detail=f"User {current_user.id} has already voted on post {vote.post_id}") # type: ignore
        # No vote found for the post,
        # Check whether the post exists
        post_query = db.query(models.Post).filter(models.Post.id == vote.post_id)
        post_found = post_query.first()
        if not post_found:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                                detail=f"Post {vote.post_id} doesn't exist")
        #  add to vote table
        new_vote = models.Vote(post_id = vote.post_id, user_id = current_user.id) # type: ignore
        db.add(new_vote)
        db.commit()
    else:
        # User wants to delete an existing vote
        if not vote_found:
            # Cannot delete a vote that does not exist
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Vote does not exist for post {vote.post_id}")
        # Vote exists, delete
        vote_query.delete(synchronize_session=False)
        db.commit()