from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime
from pydantic.types import conint

from sqlalchemy import orm

# Extend BaseModel class Schema for data that's sent or received.
# Used to validate that data from client matches this model.i.e.
# Front end is sending what we expect from the pydantic models (the request).
# Could do same for the responses

# User to us; the request
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True # default=T if not provided, else whatever user supplies.

class PostCreate(PostBase):
    pass # Accept what's inherited

# User will get back ORM - convert to pydantic model using config
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config: 
        orm_mode = True
        
# Us to user; the response
class Post(PostBase):
    id: int # Send back these fields as well as what's inherited from 
    created_at: datetime # PostBase class above
    owner_id: int
    owner: UserOut # ref to UserOut class pydantic model

    # pydantic expects a dict not a sqlalchemy schema
    class Config: 
        orm_mode = True

# For when we start doing joins in get_posts route
class PostOut(BaseModel):
    Post: Post  # all fields in Post under a field=Post returned by query
    votes: int

    class Config: 
        orm_mode = True

# Schema for the information the user must supply, a pydantic model
class UserCreate(BaseModel):
    email: EmailStr
    password: str

# Schema for user login post request (user sends email & password)
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for the token
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the data that goes into the token
class TokenData(BaseModel):
    id: Optional[str] = None

# Schema for voting
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # only 0,1 allowed (negatives too but will do for now)