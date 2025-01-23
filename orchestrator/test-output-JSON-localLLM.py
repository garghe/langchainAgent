from langchain.schema import BaseOutputParser
from langchain.prompts import PromptTemplate
import requests
import json
import re

# Define the prompt template
template = """
Extract the following details from the text:
- First name
- Last name
- Number of people
- Time and Date

Text: {input_text}

Then, output ONLY the JSON string below with the following fields, in this specific order:
1. firstname
2. lastname
3. number_of_people
4. time_and_date

Follow these rules:
1. Do not include any backticks or additional formatting.
2. Provide only the JSON, nothing else.
3. Ensure the JSON is well formatted, and do not add any extra explanations, text, or symbols.
4. The JSON should look like this:
{{
    "firstname": "John",
    "lastname": "Doe",
    "number_of_people": 4,
    "time_and_date": "2025-01-25T19:00:00"
}}

Only output the JSON string in the format above, with no additional text or formatting.
"""


# Define the custom output parser
class JSONOutputParser(BaseOutputParser):
    def parse(self, text: str):
        try:
            # Ensure the text is valid JSON
            return json.loads(text.strip())
        except json.JSONDecodeError as e:
            print("Error parsing the output as JSON:", e)
            return None

# Create a custom LLM class to interact with your local LMStudio
class LocalLLM:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def call(self, prompt: str):
        print(f"Sending request to LLM with prompt:\n{prompt}\n")
        response = requests.post(
            self.endpoint,
            json={"prompt": prompt, "max_tokens": 200},
            headers={"Content-Type": "application/json"},
        )
        print("Received response from LLM.")
        print(f"Response status code: {response.status_code}")
        print(f"Response body: {response.text}")
        if response.status_code == 200:
            try:
                return response.json().get("choices", [{}])[0].get("text", "").strip()
            except Exception as e:
                print("Error processing the response:", e)
                print("Full response content:", response.text)
                return None
        else:
            raise Exception(f"Request failed with status code {response.status_code}: {response.text}")

# Initialize components
llm = LocalLLM(endpoint="http://127.0.0.1:9999/v1/completions")
prompt = PromptTemplate(template=template, input_variables=["input_text"])
print(prompt)
parser = JSONOutputParser()

def run_chain(input_text: str):
    print("run chain")
    print(input_text)
    # Generate the prompt
    generated_prompt = prompt.format(input_text=input_text)
    print(f"Generated prompt:\n{generated_prompt}")

    # Call the local LLM
    response = llm.call(generated_prompt)

    response = remove_all_json_backticks(response)
    print(f"LLM response:\n{response}")
    # Parse the response
    return parser.parse(response)

def remove_all_json_backticks(text: str) -> str:
    # Remove all occurrences of ```json and ```
    text = re.sub(r'```json|```', '', text)
    # Strip any leading or trailing whitespace
    return text.strip()



# Example usage
if __name__ == "__main__":
    print("Start")
    input_prompt = "Resever a table for John Doe for 4 people on January 25, 2025, at 7 PM."
    result = run_chain(input_prompt)

    if result:
        print("Extracted Information:")
        print(f"First Name: {result.get('firstname', 'N/A')}")
        print(f"Last Name: {result.get('lastname', 'N/A')}")
        print(f"Number of People: {result.get('number_of_people', 'N/A')}")
        print(f"Time and Date: {result.get('time_and_date', 'N/A')}")
