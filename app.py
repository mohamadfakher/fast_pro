#app.py
from fastapi import FastAPI, Depends, HTTPException, status, Request
from tortoise.contrib.fastapi import register_tortoise
from tortoise.transactions import in_transaction
from models.models import user_pydantic, User
from jose import jwt, JWTError
from logger.request_logger import AppLogger
from fastapi import Form
from fastapi.staticfiles import StaticFiles
from fastapi import Cookie

#temlating
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

#auth
from utils.auth import get_hashed_password, token_generator, config_credential, authenticate_user, very_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

#middleware
from middleware.middleware import AuthMiddleware
from middleware.request_logger import RequestLoggerMiddleware

app = FastAPI()

o2_scheme = OAuth2PasswordBearer(tokenUrl='token')

templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

# Geschützte Endpunkte
protected_endpoints = {"/profile"}

# Middleware registrieren
app.add_middleware(RequestLoggerMiddleware)
app.middleware("http")(AuthMiddleware(app, protected_endpoints))

# Configure the App-Logger
app_logger = AppLogger()
app_logger.get_logger().info("This log message is using the configurated logger.")

@app.post('/token')
async def generate_token(request_from: OAuth2PasswordRequestForm = Depends()):
    app_logger.get_logger().info("Route token")
    token = await token_generator(request_from.username, request_from.password)
    return {'access_token': token, 'token_type': 'bearer'}

async def get_current_user(token: str = Depends(o2_scheme)):
    try:
        pay_load = jwt.decode(token, config_credential['SECRET'], algorithms=['HS256'])
        user = await User.get(id=pay_load.get('id'))
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
            headers={'WWW-Authenticate': 'Bearer'}
        )
    return await user

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post('/login', response_model=user_pydantic)
async def login(email: str = Form(...), password: str = Form(...)):
    app_logger.get_logger().info("Route login")
    user = await authenticate_user(email, password)
    if user:
        token = await token_generator(email, password)
        bearer_token = f"Bearer {token}"
        app_logger.get_logger().info(f"Generated token: {token}")
        response = RedirectResponse("/profile")
        response.set_cookie(key="token", value=bearer_token)
        return response
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
            headers={'WWW-Authenticate': 'Bearer'}
        )


# Route für die Signup-Seite
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_model=user_pydantic)
async def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    app_logger.get_logger().info("Route signup")
    hashed_password = get_hashed_password(password)
    async with in_transaction():
        db_user = await User.create(
            username=username,
            email=email,
            password=hashed_password
        )
    return db_user


@app.post("/profile")
async def profile_page(token: str = Cookie(None)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found",
        )
    if token.startswith("Bearer "):
        token = token.split("Bearer ")[1]

    user = await very_token(token)

    try:
        html_content = open("templates/profile.html").read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Route profile.html file not found",
        )

    html_content = html_content.replace("{username}", user.username)
    html_content = html_content.replace("{token_payload}", str(user))

    return HTMLResponse(content=html_content, status_code=200)

@app.get("/profile")
async def profile(request: Request, token: str = Cookie(None)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token not found",
        )
    if token.startswith("Bearer "):
        token = token.split("Bearer ")[1]

    user = await very_token(token)

    try:
        html_content = open("templates/profile.html").read()
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="profile.html file not found",
        )

    html_content = html_content.replace("{username}", user.username)
    html_content = html_content.replace("{email}", user.email)

    image_url = str(request.url_for("static", path="profile_image.png"))
    html_content = html_content.replace("{profile_image_url}", image_url)

    return HTMLResponse(content=html_content, status_code=200)


@app.middleware("http")
async def delete_cookie(request: Request, call_next):
    response = await call_next(request)
    if request.url.path == "/logout":
        response.delete_cookie("token")
    return response

@app.get("/logout")
async def logout():
    return RedirectResponse(url="/login")

products = [
    {"id": 1, "name": "Produkt 1", "description": "Beschreibung 1", "price": 10.99, "image_path": "product1.jpg"},
    {"id": 2, "name": "Produkt 2", "description": "Beschreibung 2", "price": 19.99, "image_path": "product2.jpg"},
    {"id": 3, "name": "Produkt 3", "description": "Beschreibung 3", "price": 14.99, "image_path": "product3.jpg"},
]

@app.get("/home", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request, "products": products})

@app.get("/product/{product_id}", response_class=HTMLResponse)
async def product_detail(request: Request, product_id: int):
    product = next((pro for pro in products if pro["id"] == product_id), None)
    if product:
        return templates.TemplateResponse("view.html", {"request": request, "product": product})
    else:
        return HTMLResponse(content="Product not found", status_code=404)


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models.models"]},
    generate_schemas=True,
    add_exception_handlers=True
)

