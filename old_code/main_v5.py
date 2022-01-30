# before clean up at 8.50 hr
import os
print(f'Dir of current script {os.path.dirname(__file__)}')
print(f'the package is {__package__}')
print(f'the name is {__name__}') # main

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
# from .database import engine, SessionLocal # Relative imports not working
#from .routers import post, user
import models, schemas, utils
from database import engine, get_db
from routers import post, user, auth # looks ok

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

# Make use of the routers to access the paths
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

# path operation or route ##########
# decorator = instance of fastapi with http get method
@app.get("/")  # path to url
def root():  # function
    return {"message": "welcome to my api"}
    # Test in Postman with a GET request to http://127.0.0.1:8000/
