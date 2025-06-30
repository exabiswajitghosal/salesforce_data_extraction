import json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from uuid import uuid4
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import your functions
from utils.data_extraction_openAI import (
    convert_pdf_base64_to_image_base64s,
    match_extracted_with_template_from_images
)

# Create FastAPI instance
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Limit this to your frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic model for request body
class PDFBase64Request(BaseModel):
    form_type: str
    pdf_base64: str


# Root endpoint
@app.get("/", response_model=Dict[str, str])
def index():
    return {"message": "You're connected successfully."}


# POST endpoint for PDF extraction
# @app.post("/api/extract_from_pdf_base64")
# async def extract_from_pdf_base64(request: PDFBase64Request):
#     pdf_base64 = request.pdf_base64
#     form_type = request.form_type
#
#     if not pdf_base64:
#         raise HTTPException(status_code=400, detail="PDF base64 data is required.")
#
#     if not form_type:
#         raise HTTPException(status_code=400, detail="Form type is required.")
#
#     if form_type not in ["125"]:
#         raise HTTPException(status_code=400, detail="Invalid form type. Supported types: 125, 127a, 137")
#
#     logger.info("Received PDF base64 data.")
#     submission_id = str(uuid4())
#
#     try:
#         base64_images = convert_pdf_base64_to_image_base64s(pdf_base64)
#         logger.info(f"Base64 images extracted: {len(base64_images)}")
#     except Exception as e:
#         logger.error(f"Error converting PDF to images: {e}")
#         raise HTTPException(status_code=400, detail="Failed to convert PDF to images.")
#
#     if not base64_images:
#         raise HTTPException(status_code=400, detail="Could not convert PDF to image base64s.")
#
#     try:
#         result = match_extracted_with_template_from_images(base64_images=base64_images, submission_id=submission_id,
#                                                            form_type=form_type)
#     except Exception as e:
#         logger.error(f"Error extracting structured data: {e}")
#         raise HTTPException(status_code=500, detail="Failed to extract structured data.")
#
#     if not result:
#         raise HTTPException(status_code=500, detail="Extraction returned no result.")
#
#     return {
#         "message": "Data extracted successfully.",
#         "response": result
#     }


@app.post("/api/extract_from_pdf_base64")
async def read_output(request: PDFBase64Request):
    pdf_base64 = request.pdf_base64
    form_type = request.form_type

    if not pdf_base64:
        raise HTTPException(status_code=400, detail="PDF base64 data is required.")

    if not form_type:
        raise HTTPException(status_code=400, detail="Form type is required.")

    if form_type not in ["125"]:
        raise HTTPException(status_code=400, detail="Invalid form type. Supported types: 125, 127a, 137")

    with open('utils/template/Commercial_auto_application_data.json') as f:
        output = f.read()
        response = json.loads(output)
    return response


# Uvicorn server (when running directly)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
