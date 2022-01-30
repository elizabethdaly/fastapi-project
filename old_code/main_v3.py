from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body, Depends
from pydantic import BaseModel
from random import randrange
import time

from starlette.status import HTTP_204_NO_CONTENT
import psycopg2  # PostgreSQL 
from psycopg2.extras import RealDictCursor # To get column names from DB

# sqlalchemy stuff & fast api wrt sql dbs
from sqlalchemy.orm import Session

# from . import models # Relative imports not working
import models as models
# from .database import engine, SessionLocal # Relative imports not working
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

# print("File __name__ is set to: {}" .format(__name__))

app = FastAPI()

# Extend BaseModel class Schema for data that's sent or received.
# Used to validate that data from client matches this model.i.e.
# Front end is sending what we expect from the pydantic models.
class Post(BaseModel):
    title: str
    content: str
    published: bool = True # default=T if not provided, else whatever user supplies.
    rating: Optional[int] = None

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

# path operation or route
# decorator = instance of fastapi with http get method
@app.get("/")  # path to url
def root():  # function
    return {"message": "welcome to my api"}

# For testing sqlalchemy
# import Session from sqlalchemy.orm and Depends from fastapi.params
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)): # create a session to db for every query
    posts = db.query(models.Post) # the bare query object, no methods yet
    print(posts) # returns this
    return {"data": "successful"}

    # posts = db.query(models.Post).all() # Access Post model in models, get all entries in table
    # return {"data": posts}

# Path operation to Get posts
@app.get("/posts")
def get_posts():
    cursor.execute("""SELECT * FROM posts""") # SQL to retrieve all posts from fastapi DB, posts table
    posts = cursor.fetchall()
    return {"data": posts}

# Path operation to Create a post
@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # post_dict = post.dict() # post pydantic model converted to a dict
    # post_dict['id'] = randrange(0, 1000000) # assign a randon id
    # my_posts.append(post_dict)

    # Not good to do string interpretation on the fly, as are vulnerable to SQL injection attack
    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """, (post.title, post.content, post.published))
    new_post = cursor.fetchone() # gets the created post from RETURNING above
    # Changes above are Staged changes, now need to commit them to DB
    conn.commit()
    return {"data": new_post}

# Path operation to Get a post by ID
@app.get("/posts/{id}") # id field is a path parameter fastapi checks for int and converts if need be
def get_post(id: int): # fastapi does the validation for us, informative error message
    cursor.execute("""SELECT * FROM posts WHERE id = %s""", (str(id),))  # id needs to be a str here
    post = cursor.fetchone() # Will always be one

    # If post not found return proper http status code and error
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Post with id: {id} not found')
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {'message': f'post with id: {id} was not found'}
    return {"post_detail":  post}

# Path operation to Delete a post by ID
# When you delete something (http 204) you should not return anything, so fastapi will generate an error
@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))

    deleted_post = cursor.fetchone()
    conn.commit() # Commit that change to DB

    # If index does not exist, raise exception error
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')

    return Response(status_code=status.HTTP_204_NO_CONTENT)

# Path operation for put method/request
@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""", (post.title, post.content, post.published, str(id),))
    
    updated_post = cursor.fetchone()
    conn.commit()

    # If index does not exist, raise exception error
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'post with id: {id} does not exist')

    return {"data": updated_post}