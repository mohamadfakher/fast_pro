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
        pay_load = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])

        user = await User.get(id=pay_load.get('id'))

    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    except User.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    return user
async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(email, password):
    user = await User.get(email=email)

    if user and await verify_password(password, user.password):
        auth_logger.get_logger().info(f"Successfully authenticated")
        return user

    auth_logger.get_logger().error("Invalid user data!")
    return False

async def token_generator(email: str, password:str):
    auth_logger.get_logger().info("Token is successfully generated.")
    user = await authenticate_user(email, password)

    if not user:
        auth_logger.get_logger().error("Authentication error: Invalid user name or password.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )

    token_data = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }
    token = jwt.encode(token_data, config_credential['SECRET'])
    return token
