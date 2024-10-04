import base64
import re
import json

def open_as_bytes(pdf_filename:str):
    with open(pdf_filename, 'rb') as pdf_file:
        pdf_bytes = pdf_file.read()
        pdf_base64 = base64.b64encode(pdf_bytes)
    return pdf_base64

def read_text_file(file_path):
    # Open the file in read mode
    with open(file_path, 'r') as file:
        file_content = file.read()
    return file_content

def extract_json_from_string(input_string):
    try:
        # Parse the JSON string into a Python object (dictionary)
        
        json_object = json.loads(input_string)
        return json_object
    except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            return None
    else:
        print("No valid JSON block found.")
        return None

def save_json_string_to_file(json_string, file_path):
    # Open the file in write mode and save the JSON string
    with open(file_path, 'w') as file:
        file.write(json_string)
