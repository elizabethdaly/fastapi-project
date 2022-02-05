from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter

# sqlalchemy stuff & fast api wrt sql dbs
from sqlalchemy.orm import Session

from .. import models, schemas, utils
from ..database import get_db
# import models, schemas, utils
# from database import get_db

# Create a router object
router = APIRouter(
    prefix="/users",
    tags=['Users']
)

# Path operation to make a user, who must supply email & pwd so need a schema for the data sent
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
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
@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    print(user.id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'User with id: {id} does not exist')
    
    return user
