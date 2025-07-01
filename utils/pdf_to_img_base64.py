import base64
import io
from pdf2image import convert_from_bytes
from typing import List


def convert_pdf_base64_to_image_base64s(pdf_base64: str) -> List[str]:
    try:
        # Decode the base64 PDF
        pdf_bytes = base64.b64decode(pdf_base64)

        # Convert PDF pages to images
        images = convert_from_bytes(pdf_bytes)

        base64_images = []
        for img in images:
            buffered = io.BytesIO()
            img.save(buffered, format="PNG")
            img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
            base64_images.append(f"data:image/png;base64,{img_base64}")

        return base64_images

    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return []