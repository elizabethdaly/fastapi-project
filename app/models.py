from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import False_
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import TIMESTAMP

# from .database import Base # rel import not working

print("In models.py: next line imports Base from database")
# from .database import Base # rel import not working
# from database import Base # alembic error but server runs
# from app.database import Base # alembic ok but server error
import sys, os
sys.path.insert(0, os.getcwd()) # 'path_to_your_module') # or: sys.path.insert(0, os.getcwd())
# from database import Base # server runs with this one
from .database import Base # ST github

# Creaet a ORM model for posts table by extending the Base class from database.py
class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    published = Column(Boolean, server_default='TRUE', nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    #Set up Foreign Key to ref id col of users table (so users.id) not the class
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Set up relationship between a post and the user who created it
    # Return the sqlalchemy class of another model
    owner = relationship("User")

# Create a ORM model for our users table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    email = Column(String, nullable=False, unique=True) # no email can register twice
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text('now()'))
    phone_number = Column(String)

# Create ORM model for votes table
class Vote(Base):
    __tablename__ = "votes"
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)