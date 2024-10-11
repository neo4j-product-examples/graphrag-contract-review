import os
import json
from openai import OpenAI
from openai.types.beta.threads.message_create_params import (
    Attachment,
    AttachmentToolFileSearch,
)
from Utils import read_text_file, save_json_string_to_file, extract_json_from_string
import re

# Configuring the OpenAI library with your API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# Load the system instruction and extraction prompt
system_instruction = read_text_file('./prompts/system_prompt.txt')
extraction_prompt = read_text_file('./prompts/contract_extraction_prompt.txt')

# Configure the assistant
pdf_assistant = client.beta.assistants.create(
    model="gpt-4o-2024-08-06",
    description="An assistant to extract the information from contracts in PDF format.",
    tools=[{"type": "file_search"}],
    name="PDF assistant",
    instructions=system_instruction,
)

def process_pdf(pdf_filename):
    # Create thread
    thread = client.beta.threads.create()
    # Upload PDF file
    file = client.files.create(file=open(pdf_filename, "rb"), purpose="assistants")
    # Create assistant message with attachment and extraction_prompt
    client.beta.threads.messages.create(thread_id=thread.id,role="user",
        attachments=[
            Attachment(
                file_id=file.id, tools=[AttachmentToolFileSearch(type="file_search")]
            )
        ],
        content=extraction_prompt,
    )

    # Run thread
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=pdf_assistant.id, timeout=1000)

    if run.status != "completed":
        raise Exception("Run failed:", run.status)

    # Retrieve messages
    messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
    messages = [message for message in messages_cursor]
   
    # Output extracted content
    return messages[0].content[0].text.value

def main():
    pdf_files = [filename for filename in os.listdir('./data/input/') if filename.endswith('.pdf')]
    
    for pdf_filename in pdf_files:
        print('Processing ' + pdf_filename + '...')    
        # Extract content from PDF using the assistant
        complete_response = process_pdf('./data/input/' + pdf_filename)
        # Log the complete response to debug
        save_json_string_to_file(complete_response, './data/debug/complete_response_' + pdf_filename + '.json')
        # Try to load the response as valid JSON
        try:
            contract_json = extract_json_from_string(complete_response)
            # Store as valid JSON so it can be imported into a KG later
            json_string = json.dumps(contract_json, indent=4)
            save_json_string_to_file(json_string, './data/output/' + pdf_filename + '.json')
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")

if __name__ == '__main__':
    main()