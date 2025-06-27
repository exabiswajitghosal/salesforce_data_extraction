import json
import requests
from dotenv import load_dotenv
import os
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import base64
import io
from pdf2image import convert_from_bytes
from typing import List

# Load environment variables
load_dotenv()
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


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


def fetch_insights_from_base64_images(images: list):
    """Send base64-encoded images to OpenAI gpt-4o-mini and extract insights."""
    try:
        if not images:
            print("No base64 images provided.")
            return None

        # Construct messages payload
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract all information from the document in JSON format"}
                ]
            }
        ]

        for img_base64 in images:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": img_base64}
            })

        data = {
            "model": openai_model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            json=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {openai_api_key}",
            },
        )

        if response.status_code != 200:
            print(f"API Error {response.status_code}: {response.text}")
            return None

        # Parse textual JSON from the LLM response
        content = response.json()["choices"][0]["message"]["content"]
        # json_start = content.find('{')
        # json_end = content.rfind('}') + 1
        #
        # if json_start == -1 or json_end == -1:
        #     print("No JSON structure found in response.")
        #     return None
        #
        # json_str = content[json_start:json_end]
        # parsed_response = json.loads(json_str)
        #
        # # Save extracted raw output
        # response_output_path = f"./output/{submission_id}/extracted_data.json"
        # os.makedirs(os.path.dirname(response_output_path), exist_ok=True)
        # with open(response_output_path, "w") as f:
        #     json.dump(parsed_response, f, indent=4)

        return content

    except Exception as e:
        print(f"Error fetching insights: {e}")
        return None


def match_extracted_with_template_from_images(base64_images: list, submission_id: str, form_type= str):
    """Matches extracted raw insights with the target template using LLM."""
    data = fetch_insights_from_base64_images(base64_images)
    if not data:
        return None

    try:
        model = ChatOpenAI(model=openai_model, temperature=0)
        if form_type == "125":
            with open('utils/template/125_JSON_Schema.json') as f:
                structure = f.read()
        elif form_type == "127a":
            return None
            # with open('utils/template/127a_JSON_Schema.json') as f:
            #     structure = f.read()
        elif form_type == "137":
            return None
            # with open('utils/template/127b_JSON_Schema.json') as f:
            #     structure = f.read()
        else:
            print(f"Unsupported form type: {form_type}")
            return None


        system_prompt = (
            "You are an AI assistant specialized in extracting structured information from documents. "
            "Please analyze the following extracted data and map it to the structure provided. "
            "Replace <value> placeholders with actual values. If a value is missing, leave it blank."
            "Strictly follow the provided JSON structure and do not add any additional fields.\n\n"
            f"Return the full JSON structure:\n{structure}"
        )

        response = model.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Please extract the information from the following text:\n\n{data}")
        ])

        response_text = response.content
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1

        if json_start == -1 or json_end == -1:
            print("No JSON array found in final structured response.")
            return None

        parsed_response = json.loads(response_text[json_start:json_end])

        # Save mapped template output
        output_path = f"./output/{submission_id}/output.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(parsed_response, f, indent=4)

        return parsed_response

    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        return None
    except Exception as e:
        print(f"Error processing structured extraction: {e}")
        return None
    finally:
        print("process done")
