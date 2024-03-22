#middleware
from fastapi import HTTPException, Request
from utils.auth import very_token
from typing import Callable
from fastapi.responses import RedirectResponse

class AuthMiddleware:
    def __init__(self, app, protected_endpoints):
        self.app = app
        self.protected_endpoints = set(protected_endpoints)

    async def __call__(self, request: Request, call_next: Callable):
        path = request.url.path
        if path in self.protected_endpoints:
            token = request.cookies.get("token")
            if not token or not token.startswith("Bearer"):

                return RedirectResponse(url="/login")

            token = token.split(" ")[1]
            if not await very_token(token):
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        response = await call_next(request)
        return response
