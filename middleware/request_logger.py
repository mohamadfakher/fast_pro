# request_logger.py
from loguru import logger
from time import time
from fastapi import Request

class RequestLoggerMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            request = Request(scope, receive)
            start_time = time()

            async def send_wrapper(message):
                await send(message)

            response = await self.app(scope, receive, send_wrapper)

            end_time = time()
            logger.info(
                f"Request received: {request.method} {request.url.path} | Execution time: {end_time - start_time:.5f}s"
            )

            return response
        else:
            return await self.app(scope, receive, send)

