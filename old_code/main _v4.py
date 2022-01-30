from typing import Optional, List
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body, Depends

from random import randrange
import time

from starlette.status import HTTP_204_NO_CONTENT
import psycopg2  # PostgreSQL 
from psycopg2.extras import RealDictCursor # To get column names from DB

# sqlalchemy stuff & fast api wrt sql dbs
from sqlalchemy.orm import Session

# from . import models # Relative imports not working
import models, schemas, utils

# from .database import engine, SessionLocal # Relative imports not working
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

# print("File __name__ is set to: {}" .format(__name__))

app = FastAPI()

while True:

    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='lizFastAp1', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful")
        break  # break out of loop if cnxn made and move on to start server
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2) # wait few s before trying again

# Store posts in memory (DB eventually)
my_posts = [
    {"title": "title of post 1", "content": "content of post 1", "id": 1},
    {"title": "favourite foods", "content": "pizza", "id": 2}
    ]

# Make a simple function to find a post with given id - not good programming
def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p

# Find post by id return index
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

# path operation or route ##########
# decorator = instance of fastapi with http get method
@app.get("/")  # path to url
def root():  # function
    return {"message": "welcome to my api"}
    # Test in Postman with a GET request to http://127.0.0.1:8000/

# Path operation to Get all posts ##########
@app.get("/posts", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db)):
    # # SQL to retrieve all posts from fastapi DB, posts table
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts

# Path operation to Create a post ##########
@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    # post_dict = post.dict() # post pydantic model converted to a dict
    # post_dict['id'] = randrange(0, 1000000) # assign a randon id
    # my_posts.append(post_dict)

    # # Not good to do string interpretation on the fly, as are vulnerable to SQL injection attack
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    # new_post = cursor.fetchone() # gets the created post from RETURNING above
    # conn.commit() # Changes above are Staged changes, now need to commit them to DB

    # print(post.dict()) # convert post to Python dict
    # new_post = models.Post(title=post.title, content=post.content, published=post.published) # onerous
    new_post = models.Post(**post.dict()) # ** to unpack dict
    db.add(new_post) # must add this new post to DB
    db.commit() # and commit changes as in code above
    db.refresh(new_post) # like RETURNING, retrieve new post from DB after commit and store it again

    return new_post

# Path operation to Get a post by ID ##########
@app.get("/posts/{id}", response_model=schemas.Post) # id field is a path parameter fastapi checks for int and converts if need be
def get_post(id: int, db: Session = Depends(get_db)): # fastapi does the validation for us, informative error message
    # cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))  # id needs to be a str here
    # post = cursor.fetchone() # Will always be one

    post = db.query(models.Post).filter(models.Post.id == id).first() # filter all posts to find first one with id passed
    # print(post) # To see equivalent SQL in terminal


    # If post not found return proper http status code and error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'post with id: {id} was not found'}
    return post

# Path operation to Delete a post by ID ##########
# When you delete something (http 204) you should not return anything, so fastapi will generate an error
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db)):
    # cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    # deleted_post = cursor.fetchone()
    # conn.commit() # Commit that change to DB

    post = db.query(models.Post).filter(models.Post.id == id) # Find post with id we want
    # If index does not exist, raise exception error
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Path operation for put method/request ##########
@app.put("/posts/{id}", response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):
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
    # post_query.update({'title': 'hey this is my updated title', 'content': 'updated content'}, synchronize_session=False)
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()

# Path operation to make a user, who must supply email & pwd so need a schema for the data sent
@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    # hash the password from user.password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password # update pwd to hashed version


    new_user = models.User(**user.dict()) # ** to unpack dict we get in schemas.UserCreate
    db.add(new_user) # must add this new post to DB
    db.commit() # and commit changes as in code above
    db.refresh(new_user) # like RETURNING, retrieve new post from DB after commit and store it again
    return new_user

# Path operation/route to get a user from id
@app.get("/users/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {id} does not exist')
    
    return user
