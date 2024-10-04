import base64
import json
import os
from vertexai.generative_models import Part, SafetySetting
from Utils import open_as_bytes , read_text_file, save_json_string_to_file
from vertexai.generative_models import GenerativeModel
import google.generativeai as genai

# Configuring the Google Generative AI library with your API key
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)


#Generation info (prompts, safety settings, generation config)
system_instruction = read_text_file('./prompts/system_prompt.txt')
extraction_prompt = read_text_file('./prompts/contract_extraction_prompt.txt')
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0,
    "top_p": 0.95,
    "response_mime_type": "application/json"
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]

def generate(system_instruction:str,extraction_prompt:str,document, generation_config ):
  model = GenerativeModel(
        "gemini-1.5-pro",
        system_instruction=[system_instruction],
        generation_config=generation_config,
        safety_settings = safety_settings
  )
  response = model.generate_content(
      [document, extraction_prompt]
  )
  return response.text
  

def main():
    
    pdf_files = [filename for filename in os.listdir('./data/input/') if filename.endswith('.pdf')]

    # For each Contract PDF
    for pdf_filename in pdf_files:
        print ('Processing '+ pdf_filename + '...')

        #load pdf file into a document that can be sent to Gemini Model
        contract_bytes = open_as_bytes('./data/input/' + pdf_filename)
        document = Part.from_data(mime_type="application/pdf", data=base64.b64decode(contract_bytes))

        #send contract to LLM to extract answers to our legal questions
        complete_response =  generate(system_instruction,extraction_prompt,document, generation_config)
        
        #log the complete response to debug
        save_json_string_to_file(complete_response,'./data/debug/complete_reponse_' + pdf_filename + '.json')

        #Try to load the response as Valid JSON
        try:
            contract_json = json.loads(complete_response)
            #store as valid JSON so it can be imported into a KG later
            json_string = json.dumps(contract_json, indent=4)
            save_json_string_to_file(json_string,'./data/output/' + pdf_filename + '.json')
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON: {e}")
        
main()

