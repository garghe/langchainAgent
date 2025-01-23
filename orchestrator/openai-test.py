import os
import requests
import json
from dotenv import load_dotenv, find_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool

###############################################################################
# 1) Load environment variables
###############################################################################
_ = load_dotenv(find_dotenv())  # Read local .env file
openai_api_key = os.environ.get("OPENAI_API_KEY", "")

###############################################################################
# 2) Define your booking tool function
###############################################################################
def call_booking_api(json_string: str) -> str:
    """
    Expects a JSON string with the structure:
      {
        "data": {
          "firstname": "string",
          "lastname": "string",
          "num_people": "number",
          "booking_datetime": "string (e.g., 2025-01-23 14:00:00)"
        }
      }
    Sends it to http://localhost:5000/book as JSON.
    """
    try:
        # Parse input JSON string
        payload = json.loads(json_string)
        if "data" not in payload:
            return "Error: Missing 'data' key in the payload."
    except json.JSONDecodeError as e:
        return f"Error: Invalid JSON input - {str(e)}"

    # Make the POST request to the API
    api_url = "http://localhost:5000/book"
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code == 200:
            return f"Booking confirmed: {response.json()}"
        else:
            return f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error during API call: {str(e)}"

###############################################################################
# 3) Wrap the booking API tool
###############################################################################
booking_tool = Tool(
    name="BookingAPI",
    func=call_booking_api,
    description=(
        "Use this tool to book a table by providing a JSON string with a 'data' key. "
        "The JSON should include the following details: firstname, lastname, "
        "number of people, and booking date/time. Example: "
        '{"data": {"firstname": "John", "lastname": "Doe", "num_people": 4, '
        '"booking_datetime": "2025-01-23 14:00:00"}}'
    ),
)

###############################################################################
# 4) Initialize the Agent
###############################################################################
llm = ChatOpenAI(
    openai_api_key=openai_api_key,
    model="gpt-4o",
    temperature=0.0
)

# Initialize the agent with only the tool and let the agent manage the flow
agent = initialize_agent(
    tools=[booking_tool],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True  # Enable detailed logging to see how the agent manages the process
)

###############################################################################
# 5) Provide User Input to the Agent
###############################################################################
user_input = "Book a table for Marco Garghentini tomorrow at 2pm for 5 people."

# Run the agent and capture the output
result = agent.run({"input": user_input})

print("\nAgent final output:")
print(result)
