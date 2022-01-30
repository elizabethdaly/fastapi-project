from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from fastapi.security import oauth2
from sqlalchemy import func  # for count functions etc

# sqlalchemy stuff & fast api wrt sql dbs
from sqlalchemy.orm import Session

# from .. import models, schemas
# from ..database import get_db
import models, schemas, oauth2
from database import get_db

from typing import List, Optional
# import oauth2

router = APIRouter(
    prefix="/posts", # as all the routes start with this
    tags=['Posts']
)

# Path operation to Get all posts ##########
# @router.get("/", response_model=List[schemas.Post])  # with a response model from pydantic
@router.get("/", response_model=List[schemas.PostOut])
# @router.get("/")  # without RM
def get_posts(db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user),
    limit: int = 10, skip: int = 0, search: Optional[str] = ""): # How many to return? default=10 if user does not specify

    # # SQL to retrieve all posts from fastapi DB, posts table
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

     # retrieve all posts, without .all() it's just a query, not yet run
    # .all() actually performs the query
    # posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all() # retrieve posts belonging only to current user
   
    # Joins with sqlalchemy
    posts = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
        .filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # return posts
    return posts
 
# Path operation to Create a post ##########
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, 
    db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)):
    # post_dict = post.dict() # post pydantic model converted to a dict
    # post_dict['id'] = randrange(0, 1000000) # assign a randon id
    # my_posts.append(post_dict)

    # # Not good to do string interpretation on the fly, as are vulnerable to SQL injection attack
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone() # gets the created post from RETURNING above
    # conn.commit() # Changes above are Staged changes, now need to commit them to DB

    # print(post.dict()) # convert post to Python dict
    # new_post = models.Post(title=post.title, content=post.content, published=post.published) # onerous
    # print(current_user.id) # returned from oauth2.get_current_user
    new_post = models.Post(owner_id=current_user.id, **post.dict()) # ** to unpack dict and add id of logged in user
    db.add(new_post) # must add this new post to DB
    db.commit() # and commit changes as in code above
    db.refresh(new_post) # like RETURNING, retrieve new post from DB after commit and store it again

    return new_post

# Path operation to Get a post by ID ##########
@router.get("/{id}", response_model=schemas.PostOut) # id field is a path parameter fastapi checks for int and converts if need be
def get_post(id: int, db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)): # fastapi does the validation for us, informative error message
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))  # id needs to be a str here
    # post = cursor.fetchone() # Will always be one

    # post = db.query(models.Post).filter(models.Post.id == id).first() # filter all posts to find first one with id passed
    # print(post) # To see equivalent SQL in terminal

    # table joins
    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id)\
        .filter(models.Post.id == id).first()

    # If post not found return proper http status code and error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'post with id: {id} was not found'}

    # # Only retrieve a post if it belongs to current user
    # if post.owner_id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    return post

# Path operation to Delete a post by ID ##########
# When you delete something (http 204) you should not return anything, so fastapi will generate an error
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit() # Commit that change to DB

    post_query = db.query(models.Post).filter(models.Post.id == id) # Find post with id we want
    post = post_query.first()

    # If index does not exist, raise exception error
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')

    # User can only delete their own posts
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    post_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Path operation for put method/request ##########
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db), 
    current_user: int = Depends(oauth2.get_current_user)):
    # cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", 
    #     (post.title, post.content, post.published, str(id),))
    # updated_post = cursor.fetchone()
    # conn.commit()

    post_query = db.query(models.Post).filter(models.Post.id == id) # the query
    post = post_query.first() # the first post
    
    # If index does not exist, raise exception error
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f'post with id: {id} does not exist')

    # User can only update their own posts
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform requested action")

    # post_query.update({'title': 'hey this is my updated title', 'content': 'updated content'}, synchronize_session=False)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()