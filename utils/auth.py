#auth/auth.py
from passlib.context import CryptContext
from fastapi import HTTPException, status
from jose import jwt
from models.models import User
from dotenv import dotenv_values
from logger.request_logger import AppLogger


config_credential = dotenv_values(".env")
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Instantiation of the App-Logger
auth_logger = AppLogger(log_file="auth.log")

def get_hashed_password(password):
    return pwd_context.hash(password)

async def very_token(token: str):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return user

async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(username, password):
    user = await User.get(username=username)

    if user and await verify_password(password, user.password):
        auth_logger.get_logger().info(f"Successful")
        return user

    auth_logger.get_logger().error("invalid user data")
    return False

async def token_generator(username: str, password:str):
    auth_logger.get_logger().info("Token is generated.")
    user = await authenticate_user(username, password)

    if not user:
        auth_logger.get_logger().error("Authentication error: Invalid user name or password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    token_data = {
        'id': user.id,
        'username': user.username
    }
    token = jwt.encode(token_data, config_credential['SECRET'])
    return token
