import PyPDF2
import pytesseract
from pdf2image import convert_from_path
import os
import chardet
import pdfplumber
from docx import Document
from pdfminer.high_level import extract_text
from docx import Document
from pdfminer.high_level import extract_text
import win32com.client
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
from girikonocr.imagetotext  import ImageToText as img
from app.models.database import sessionmanager
import logging

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Users\ShikharSrivastava\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
)
def check_extension(file_location,document_file):
    file_extension = os.path.splitext(document_file.filename)[1].lower()


    # Check the file type and handle accordingly
    if file_extension == ".pdf":
        extract_text_from_pdf(file_location)
    elif file_extension == ".docx":
        extract_document_text(file_location)
    elif file_extension == ".doc":
        extract_text_from_doc(file_location)
    elif file_extension in (".jpg", ".png","jpeg"):
        extract_text_from_image(file_location)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only .pdf, .docx, and .doc are allowed."
        )
def extract_text_from_pdf_pdfminer(pdf_path):
    text = extract_text(pdf_path)
    page_texts = text.split('\f')  
    return page_texts

def is_digitized_pdf(file_path):
    
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                return True
    return False
            
def extract_text_from_digitized_pdf(file_path):
    try:
        with open(file_path, "rb") as file:
            reader = PyPDF2.PdfReader(file)
            text_data = []
            for page_num, page in enumerate(reader.pages, start=1):
                text = page.extract_text()
                if text:
                    text_data.append((page_num, text.strip()))
        return text_data
    except Exception as e:
        try:
            return extract_text_from_pdf_pdfminer(file_path)
        except Exception as e:
            try:
                return extract_text_from_pdf_using_plumber(file_path)
            except Exception as e:
                return extract_text_from_scanned_pdf(file_path)
            
def extract_text_from_scanned_pdf(file_path):
    images = convert_from_path(
        file_path, 500, poppler_path = r"C:\Program Files\poppler-24.08.0\Library\bin"
    )
    text_data = []
    for page_num, image in enumerate(images, start=1):
        text = pytesseract.image_to_string(image)
        if text:
            text_data.append((page_num, text.strip()))
    return text_data

def extract_text_from_pdf(file_path):
    try:
        if is_digitized_pdf(file_path):
            text_data = extract_text_from_digitized_pdf(file_path)
        else:
            text_data = extract_text_from_scanned_pdf(file_path)        
    except Exception as e:
        text_data = extract_text_from_scanned_pdf(file_path)
    
    sessionmanager.insert_extracted_text(file_path, text_data)
    
    



def fix_encoding_text(text_content):
    text_content = text_content.encode('ISO-8859-1', errors='ignore').decode('ISO-8859-1', errors='replace')
    text_content = text_content.encode('Windows-1252', errors='ignore').decode('Windows-1252', errors='replace')
    text_content = text_content.encode('GB2312', errors='ignore').decode('GB2312', errors='replace')
    text_content = text_content.encode('Shift-JIS', errors='ignore').decode('Shift-JIS', errors='replace')
    text_content = text_content.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
    text_content = text_content.encode('latin-1', errors='ignore').decode('latin-1', errors='replace')
    return text_content


def fix_encoding_text_chardet(text_content):
    result = chardet.detect(text_content.encode('utf-8', errors='replace'))
    encoding = result['encoding']
    if encoding:
        try:
            text_content = text_content.encode('utf-8', errors='replace').decode(encoding, errors='replace')
        except Exception as e:
            return(f"Error decoding text: {e}")
    return text_content

def extract_text_from_pdf_using_plumber(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages
        text_list = []
        for page in pages:
            text = page.extract_text()
            text_list.append(text)
    return text_list


def extract_document_text(file_path):
    doc = Document(file_path)
    paragraphs = []
    for para_num, para in enumerate(doc.paragraphs, 1):  
        paragraph_text = para.text.strip()  
        if paragraph_text:
            paragraphs.append(para_num)
            paragraphs.append(paragraph_text)
    sessionmanager.insert_extracted_text(file_path, paragraphs)


def extract_text_from_doc(file_path):
    text = ""
    word = win32com.client.Dispatch("Word.Application")
    doc = word.Documents.Open(file_path)
    text = doc.Content.Text
    doc.Close()
    word.Quit()
    sessionmanager.insert_extracted_text(file_path, text.strip())
    
def extract_text_from_image(file_location):
    print("inside extract_text_from_image")
    logging.basicConfig(level=logging.WARNING)

    img_to_text = img(file_location)
    extracted_text = img_to_text.extract_text_from_image()
    sessionmanager.insert_extracted_text(file_location, extracted_text)