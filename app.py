#app.py
from fastapi import FastAPI, Depends, HTTPException, status
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from models.models import user_pydantic, User
from jose import jwt, JWTError
from logger.request_logger import AppLogger

#auth
from utils.auth import get_hashed_password, token_generator, config_credential, authenticate_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


#middleware
from middleware.middleware import AuthenticationMiddleware
from middleware.request_logger import RequestLoggerMiddleware

app = FastAPI()

oath2_scheme = OAuth2PasswordBearer(tokenUrl='token')


# Geschützte Endpunkte
protected_endpoints = {"/profile", "/login", "/signup"}

# Middleware registrieren
app.add_middleware(RequestLoggerMiddleware)
app.middleware("http")(AuthenticationMiddleware(app, protected_endpoints))

# Configure the App-Logger
app_logger = AppLogger()
app_logger.get_logger().info("This log message uses the configured logger.")

@app.post('/token')
async def generate_token(request_from: OAuth2PasswordRequestForm = Depends()):
    app_logger.get_logger().info("route token")
    token = await token_generator(request_from.username, request_from.password)
    return {'access_token': token, 'token_type': 'bearer'}

'''
async def get_current_user(token: str = Depends(oath2_scheme)):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user_id = payload.get('id')
        username = payload.get('username')

        app_logger.get_logger().info(f"passwordddd get_current_user: {token}")
        user = await authenticate_user(username, token)

        if user and user.id == user_id:
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username or password',
                headers={'WWW-Authenticate': 'Bearer'}
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
'''
async def get_current_user(token: str = Depends(oath2_scheme)):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return await user

@app.post('/login')
async def user_login(user: user_pydantic = Depends(get_current_user)):
    app_logger.get_logger().info("route login")
    return {
        'status': 'ok',
        'data': {
            'username': user.username,
            'email': user.email,
        }
    }
@app.get("/profile", response_model=user_pydantic)
async def read_user_profile(current_user: User = Depends(get_current_user)):
    """
    Get the profile of the currently logged-in user.
    """
    app_logger.get_logger().info("route profile.")
    return current_user
@app.post("/signup", response_model=user_pydantic)
async def signup(user: user_pydantic):
    app_logger.get_logger().info("route signup.")
    hashed_password = get_hashed_password(user.password)
    async with in_transaction() as conn:
        db_user = await User.create(
            username=user.username,
            email=user.email,
            password=hashed_password
        )
    return db_user

@app.get("/")
def index():
    app_logger.get_logger().info("route index.")
    return {"Message": "Hello World!"}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

