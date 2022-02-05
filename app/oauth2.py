# https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/

from jose import JWTError, jwt
from datetime import datetime, timedelta
# import schemas, database, models
from . import schemas, database, models
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
# from config import settings
from .config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login") # login endpoint

# Token is made from 3 things: set as env vars in .env file
# SECRET_KEY
# Algorithm
# data + Expiration time

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Fn to create the token
def create_access_token(data: dict):
    to_encode = data.copy() # make a copy

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # set token expiry
    to_encode.update({"exp": expire}) # add expiry time to our data

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # encode the token

    return encoded_jwt

# Fn to verify the token. Pass in token and credential exception
def verify_access_token(token: str, credentials_exception):

    try:
        payload =  jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # decode the token
        id: str = payload.get("user_id") # extract the id = field we decided to use in the payload

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id = id) # validate token against of schema (very simple here)

    except JWTError: # from jose library
        raise credentials_exception
    
    return token_data

# Fn to get the current user by verfifying token, extracting id from token, 
# fetch user from DB is you want, and add it as a variable in any path operation
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                            detail=f'Could not validate credentials', 
                                            headers={"WWW-Authentication": "Bearer"})

    token = verify_access_token(token, credentials_exception)

    # Get user from db (using id extracted from token)
    user = db.query(models.User).filter(models.User.id == token.id).first()
    return user
