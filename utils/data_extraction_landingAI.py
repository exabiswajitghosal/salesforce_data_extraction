import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment
api_key = os.getenv("LANDINGAI_API_KEY")
if not api_key:
    raise ValueError("Missing API key. Make sure LANDINGAI_API_KEY is set in your .env file.")

url = "https://api.va.landing.ai/v1/tools/agentic-document-analysis"

headers = {
    "Authorization": f"Bearer {api_key}"
}

data = {
    "include_marginalia": "true",
    "include_metadata_in_markdown": "true"
}

file_path = "../docs/Acord-125.pdf (1).pdf"
with open(file_path, "rb") as f:
    files = {
        "file": f
    }
    response = requests.post(url, headers=headers, data=data, files=files)

print(response.status_code)
try:
    print(response.json())
except Exception as e:
    print("Error parsing JSON:", e)
    print(response.text)
