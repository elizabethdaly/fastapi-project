from urllib import response
import pytest
from jose import jwt
from app import schemas
# from .database import client, session # in conftest.py instead
from app.config import settings
# although we don't called session directly
# client fixture calls session first

# # Test root url first
# def test_root(client):
#     res = client.get("/")
#     # print(res) # response object
#     # print(res.json()) # {'message': 'welcome to my docker api again!!!!'}
#     print(res.json().get('message')) # welcome to my docker api again!!!!
#     assert res.json().get('message') == 'welcome to my docker api again!!!!'
#     assert res.status_code == 200

# Test create user
def test_create_user(client):
    # /users/ vs /users to get status code we expect below
    res = client.post("/users/", json={"email": "hello123@gmail.com", "password": "password123"})

    # UserOut expects id, email, created_at so some validation performed
    new_user = schemas.UserOut(**res.json()) # unpack dict to fit model
    # print(res.json())
    assert new_user.email == "hello123@gmail.com"
    assert res.status_code == 201

# Test user login with out test_user from fixture above
def test_login_user(client, test_user):
    # don't send as json, instead formdata
    res = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
    # Do some validation
    login_res = schemas.Token(**res.json())
    # Decode and verify token
    payload =  jwt.decode(login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]) # decode the token
    id = payload.get("user_id") # extract the id = field we decided to use in the payload
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [
    ('wrongemail@gmail.com', 'password123', 403),
    ('hello123@gmail.com', 'wrongPassword', 403),
    ('wrongemail@gmail.com', 'wrongPassword', 403),
    (None, 'password123', 422),
    ('hello123@gmail.com', None, 422)
])
# Test for failed login due to invalid credentials
def test_incorrect_login(test_user, client, email, password, status_code): # pass in properties from parametrize
    res = client.post("/login", data={"username": email, "password": password})
    assert res.status_code == status_code
    # assert res.json().get('detail') == 'Invalid credentials' # case sensitive see auth.py

