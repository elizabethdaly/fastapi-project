
# https://fastapi.tiangolo.com/tutorial/sql-databases/

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

print("In database.py: next liine imports config.settings")
# from .config import settings # DB credentials he has .config
from config import settings # alembic gave error but server runs
# from app.config import settings # alembic ok but server error
import sys, os
sys.path.insert(0, os.getcwd()) # 'path_to_your_module') # or: sys.path.insert(0, os.getcwd())
from config import settings # server runs with this one

# import psycopg2  # PostgreSQL 
# from psycopg2.extras import RealDictCursor # To get column names from DB
# import time

# Format of cnxn to db
# SQLALCHEMY_DATABASE_URL = 'postgreslq://<username>:<password>@<ip-address/hostname>/<database_name>'
# default user is postgres NNB not good to hard code this info.
SQLALCHEMY_DATABASE_URL = (
    f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
)

# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# We will be extending this base class
Base = declarative_base()

# create dependency from fast api site wrt sql dbs
# Get a session every time we get a request to any of our api endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# while True:
#     try:
#         conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', password='lizFastAp1', cursor_factory=RealDictCursor)
#         cursor = conn.cursor()
#         print("Database connection was successful")
#         break  # break out of loop if cnxn made and move on to start server
#     except Exception as error:
#         print("Connecting to database failed")
#         print("Error: ", error)
#         time.sleep(2) # wait few s before trying again