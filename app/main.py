import os

from rsa import verify
print(f'Dir of current script {os.path.dirname(__file__)}')
print(f'the package is {__package__}')
print(f'the name is {__name__}') # main

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# from routers import post, user, auth, vote # looks ok
from .routers import post, user, auth, vote # from sj github repo
# from config import settings

# Access settings from config file like this
# print(settings.database_password)
# print(settings.database_hostname)

# import models
# from database import engine
# tell sqlalchemy to run create statement to generate all tables
# don't need if have alembic

# models.Base.metadata.create_all(bind=engine)

# print("File __name__ is set to: {}" .format(__name__))

app = FastAPI()

# Who can talk to our api?
# origins = ["https://www.google.com"]
origins = ["*"] # anyone 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # for limiting http methods
    allow_headers=["*"],
)

# Make use of the routers to access the paths
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# path operation or route ##########
# decorator = instance of fastapi with http get method
@app.get("/")  # path to url
def root():  # function
    return {"message": "Deployed from CI/CD pipeline"}
    # Test in Postman with a GET request to http://127.0.0.1:8000/