from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import user
# import models, schemas, oauth2, database
from .. import models, schemas, oauth2, database

# Create a router object
router = APIRouter(
    prefix="/vote",
    tags=['Vote']
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, # the vote
    db: Session = Depends(database.get_db), # the db session
    current_user: int = Depends(oauth2.get_current_user)): # logged in user

    # User should not be able to vote on a post that does not exist
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with is: {vote.post_id} does not exist')

    # Construct a query to check if this post already has a vote from the current user
    vote_query = db.query(models.Vote).filter(models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
    # Perform the query
    found_vote = vote_query.first()

    # To vote
    if (vote.dir == 1):
        # If user has already voted for this post, raise error
        if (found_vote):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'user {current_user.id} has already voted on post {vote.post_id}')
        # If not, vote for the post
        new_vote = models.Vote(post_id = vote.post_id, user_id =current_user.id) # set two properties
        # Make the change to db
        db.add(new_vote)
        db.commit()
        return{"message": "successfully added vote"} # don't need to send anything back to user
    
    # to remove a vote
    else:
        # If vote doesn't exist, raise error
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist for this user")
        # If it does, delete it
        vote_query.delete(synchronize_session=False)
        db.commit()
        return{"message": "successfully deleted vote"} # don't need to send anything back to user