from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytest
from alembic import command # for drop/create tables before running tests

from app.main import app # so that we can test it
from app.database import get_db
from app.database import Base

from app.config import settings

# Want a completely seperate db for testing
# Could hard code it
# SQLALCHEMY_DATABASE_URL ='postgresql://postgres:lizFastAp1@localhost:5432/fastapi_test'

# or pull it from environment variables _test at end of fstring
SQLALCHEMY_DATABASE_URL = (f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test')


# Create engine
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Session object which allows us to query db
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the tables
# do within fixtures instead
# Base.metadata.create_all(bind=engine)

# Get a session every time we get a request to any of our api endpoints
# do within fixtures instead
# def override_get_db():
#     db = TestingSessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# Override get_db dependency with override_get_db for testing app routes
# app.dependency_overrides[get_db] = override_get_db

# client = TestClient(app)

# Run this fn before each test to give us our testing client
@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine) # drop tables
    Base.metadata.create_all(bind=engine) # create tables

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    # Run code before we run test
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    # # Create tables via alembic
    # command.upgrade("head")
    # command.downgrade("base")
    yield TestClient(app)
    
    # Run code after out test finishes