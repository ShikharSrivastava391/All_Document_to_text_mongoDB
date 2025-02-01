from dotenv import load_dotenv
load_dotenv()
import os
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException

# Import your MongoDB session manager (DatabaseSessionManager from previous code)
from app.models.database import sessionmanager
from app.routes import pdftotext_route
from app.utils.functions import handle_cors, APIKeyMiddleware

# Debugging output
print("inside driver.py")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    # MongoDB doesn't need to create tables, but we can ensure proper closing of connections
    if sessionmanager.client is not None:
        await sessionmanager.close()

def start_application():
    __app = FastAPI(
        lifespan=lifespan,
        title=os.getenv("APP_NAME", "GirikOCR"),
        version=os.getenv("APP_VERSION", "1.0.0"),
        debug=bool(os.getenv("FAST_API_DEBUG", False)),
        swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"},
        log_level=None,
    )
    return __app

app = start_application()

handle_cors(app)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    print("inside add_process_time_header")  
    start_time = time.time()
    headers = dict(request.scope["headers"])
    headers[b"custom-header"] = b"my custom header"
    request.scope["headers"] = [(k, v) for k, v in headers.items()]
    request.state.t = f"z{str(round(time.time() * 1000))}"
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["x-Process-Time"] = str(process_time)
    return response

app.add_middleware(APIKeyMiddleware, master_api_key=os.getenv("X_API_KEY_UUID"))

app.include_router(pdftotext_route.router)

print("FastAPI app configured and middleware added.")
