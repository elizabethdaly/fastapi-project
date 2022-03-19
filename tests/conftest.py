from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pytest
from alembic import command # for drop/create tables before running tests

from app.main import app # so that we can test it
from app.database import get_db
from app.database import Base
from app.oauth2 import create_access_token
from app.config import settings
from app import models

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

# use a fixture to create a test user so that we can test login
@pytest.fixture
def test_user(client):
    user_data = {"email": "hello123@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    # want to return this user so that later tests have access to it
    # print(res.json())
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

# create another test user
@pytest.fixture
def test_user2(client):
    user_data = {"email": "hello456@gmail.com", "password": "password123"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

# use a fixture to create an access token
@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

# Fixture for an authorized client = regular client + header with token
@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

# Fixture to create some test posts
@pytest.fixture
def test_posts(test_user, session, test_user2):
    posts_data = [{
        "title": "first title",
        "content": "first content",
        "owner_id": test_user['id']
    },{
        "title": "second title",
        "content": "second content",
        "owner_id": test_user['id'] 
    },{
        "title": "third title",
        "content": "third content",
        "owner_id": test_user['id'] 
    },{
        "title": "4th title",
        "content": "4th content by 2nd user",
        "owner_id": test_user2['id'] 
    }]

    # convert these dicts into post models using map
    def create_post_model(post):
        return models.Post(**post) # spread the dict
    # apply map
    posts_map = map(create_post_model, posts_data)
    # convery to list
    posts = list(posts_map)
    # add these posts to db
    session.add_all(posts)

    # session.add_all([models.Post(title="first title", content="first content", owner_id=test_user['id']), 
    #     models.Post(title="second title", content="second content", owner_id=test_user['id']), 
    #     models.Post(title="third title", content="third content", owner_id=test_user['id'])
    #     ])
    session.commit()
    posts = session.query(models.Post).all()
    return posts





