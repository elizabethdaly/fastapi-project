from fastapi import APIRouter, Depends, status, HTTPException, Response
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
# from starlette.status import HTTP_404_NOT_FOUND

# import database # from database import get_db
# import schemas, models, utils, oauth2
from .. import database, schemas, models, utils, oauth2

router = APIRouter(
    # prefix="/login", # as all the routes start with this
    tags=['Authentication'])

# user_cedentials is what user sends on attempting to login 
@router.post("/login", response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):

    # OAuth2PasswordRequestForm returns 2 fields
    # {
    #     "username": "whatever", # in our case this happens to be an email
    #     "password": "meh"
    # }

    # Make a request to DB to check for that user.email (or username) from db 
    user = db.query(models.User).filter(models.User.email == user_credentials.username).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid credentials')

    # if email exists in db, Verify that passwords are equal
    if not utils.verify(user_credentials.password, user.password): # check(plain, hashed)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f'Invalid credentials')

    # create a token
    # return token

    access_token = oauth2.create_access_token(data = {"user_id": user.id}) # payload can be anything, here its just id
    return {"access_token": access_token, "token_type": "bearer"}