import os
from typing import List
from fastapi import (
    APIRouter,
    status,
    Request,
    File,
    UploadFile,
    Security,
    BackgroundTasks,
    HTTPException,
)
from fastapi.security import APIKeyHeader
from dotenv import load_dotenv
from app.controllers.pdftotext import check_extension

import shutil

load_dotenv()

VALID_API_KEY = os.getenv("X_API_KEY_UUID")

api_key_header = APIKeyHeader(name="X_API_KEY_UUID")

router = APIRouter(
    prefix="/api/v1",  
    tags=["GirikOcr"],
    responses={404: {"description": "Not found"}},
)

def delete_directory_if_exists(directory_path):
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)
        print(f"Deleted directory: {directory_path}")
    else:
        print(f"Directory does not exist: {directory_path}")


@router.post("/uploads", status_code=status.HTTP_201_CREATED)
async def upload_document_file(
    background_tasks: BackgroundTasks,
    api_key: str = Security(api_key_header),
    document_file: UploadFile = File(...),  
):
    print("INSIDE ROUTER")
    if api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API Key"
        )

    upload_folder = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    file_location = os.path.join(upload_folder, document_file.filename)

    if os.path.exists(file_location):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File already exists"
        )

    file_content = await document_file.read()

    
    await save_document_file(file_content, file_location)

    # file_extension = os.path.splitext(document_file.filename)[1].lower()
    
    check_extension(file_location,document_file)

async def save_document_file(file_content: bytes, file_location: str):
    print(f"Saving file: {file_location}")
    try:
        with open(file_location, "wb") as f:
            f.write(file_content)  
        print(f"File saved at {file_location}")
    except Exception as e:
        print(f"Error saving file: {e}")
