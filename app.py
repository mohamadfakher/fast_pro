#app.py
from fastapi import FastAPI, Depends, HTTPException, status
from tortoise import models
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from models.models import user_pydantic, User, Role, Product
from jose import jwt, JWTError

#auth
from utils.auth import get_hashed_password, token_generator, config_credential, authenticate_user
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI()

oath2_scheme = OAuth2PasswordBearer(tokenUrl='token')


@app.post('/token')
async def generate_token(request_from: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_from.username, request_from.password)
    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: str = Depends(oath2_scheme)):
    try:
        payload = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user_id = payload.get('id')
        username = payload.get('username')
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

@app.post('/login')
async def user_login(user: user_pydantic = Depends(get_current_user)):

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
    return current_user
@app.post("/signup", response_model=user_pydantic)
async def signup(user: user_pydantic):
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
    return {"Message": "Hello World!"}

register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
