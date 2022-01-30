from pydantic import BaseSettings

print("In config.py")

# Set env variables we need for app to run using pydantic model, case insensitive
class Settings(BaseSettings):
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # Tell pydantic where to get these values
    class Config:
        env_file = "../.env" # for server ok but alembic error
        # env_file = ".env" # alembic ok but server error

# Create an instance of Settings class
settings = Settings()