import os
from dotenv import load_dotenv
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
import json
import base64

# Load environment variables from .env file
load_dotenv()

# Get the API key from environment
api_key = os.getenv("LANDINGAI_API_KEY")
openai_api_key = os.getenv('OPENAI_API_KEY')
openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
if not api_key:
    raise ValueError("Missing API key. Make sure LANDINGAI_API_KEY is set in your .env file.")

# AgenticDoc expects 'VISION_AGENT_API_KEY'
os.environ["VISION_AGENT_API_KEY"] = api_key

from agentic_doc.parse import parse

def extract_data_landing_ai(pdf_base64: str):
    if pdf_base64.startswith("data:"):
        pdf_base64 = pdf_base64.split(",", 1)[1]
    pdf_bytes = base64.b64decode(pdf_base64)
    result = parse(pdf_bytes)
    print(f"Final result: {result[0]}")
    return result[0]


def match_extracted_with_template( pdf_base64: str,submission_id: str, form_type: str):
    """Matches extracted raw insights with the target template using LLM."""
    data = extract_data_landing_ai(pdf_base64)
    if not data:
        return None
    try:
        model = ChatOpenAI(model=openai_model, temperature=0)
        if form_type == "125":
            template_path = "utils/template/125_JSON_Schema.json"
            with open(template_path,'r') as f:
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
            "if there is any checkbox in the data, please return it as yes or no."
            "if the is any $ in the data, please return it as a number without $ sign.\n"
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
