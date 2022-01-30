from passlib.context import CryptContext # password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") # password hashing alg

# Fn to hash a pwd
def hash(password: str):
    return pwd_context.hash(password)

# Function to compare hased password from DB against passwaord the user provides (and we hash)
def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
