import io
import re
import os
import json
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
# from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
import pdfplumber
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

# Set up logger using Python's logging module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("functions")


# Middleware class to handle CORS settings
class DynamicCORSMiddleware(CORSMiddleware):
    def is_allowed_origin(self, origin: str) -> bool:
        return self.is_allowed_origin(origin)


# Function to handle CORS configurations
def handle_cors(app: FastAPI):
    new_origins = [
        "http://127.0.0.1:5500"
    ]

    app.add_middleware(
        DynamicCORSMiddleware,
        allow_credentials=True,
        allow_origins=new_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, master_api_key: str):
        super().__init__(app)
        self.master_api_key = master_api_key

    async def dispatch(self, request: Request, call_next):
        print("INSIDE APIKeyMiddleware")  # Ensure middleware is working
        api_key = request.headers.get("X_API_KEY_UUID")

        if api_key is None or api_key != self.master_api_key:
            logger.info(
                "Invalid API key: %s != %s",
                api_key,
                self.master_api_key,
            )
            return JSONResponse(status_code=403, content="Forbidden: Invalid API Key")
        else:
            response = await call_next(request)
            return response
