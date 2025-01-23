import os
import json
import requests
from dotenv import load_dotenv, find_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.prompts import PromptTemplate

# Load environment variables - these are saved in a local .env file (remember to add it to .gitignore)
_ = load_dotenv(find_dotenv())
openai_api_key = os.environ.get("OPENAI_API_KEY", "")

# Define API endpoint for the local Flask App, used to store appointment requests
RESTAURANT_API_URL = "http://127.0.0.1:5001/book"

# Define the tool function for calling the booking service
def tool_restaurant(json_booking: str) -> str:
    """
    Sends the booking details to the restaurant API.
    """
    try:
        booking_data = json.loads(json_booking)
        response = requests.post(
            RESTAURANT_API_URL,
            headers={"Content-Type": "application/json"},
            json=booking_data,
        )
        if response.status_code == 200:
            return f"Restaurant booking confirmed: {response.json()}"
        else:
            return f"Failed to book restaurant: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error in restaurant booking tool: {str(e)}"

# Define Mock function for dentist bookings.
def tool_dentist(json_booking: str) -> str:
    return f"Dentist booking processed: {json_booking}"

#Define the restaurant tool
restaurant_tool = Tool(
    name="toolRestaurant",
    func=tool_restaurant,
    description="""Use this tool to process restaurant bookings. 
    Provide a JSON object with the fields:
    - firstname: The first name of the person.
    - lastname: The last name of the person.
    - num_people: The number of people for the booking.
    - booking_datetime: The booking date and time in 'YYYY-MM-DD HH:mm:ss' format."""
)

#Define the dentist tool
dentist_tool = Tool(
    name="toolDentist",
    func=tool_dentist,
    description="""Use this tool to process dentist appointments. 
    Provide a JSON object with the fields:
    - firstname: The first name of the person.
    - lastname: The last name of the person.
    - booking_datetime: The appointment date and time in 'YYYY-MM-DD HH:mm:ss' format."""
)

# Define the prompt template
prompt_template = PromptTemplate(
    input_variables=["user_prompt"],
    template="""You are a smart booking assistant.
    Analyze the user's request and determine if it is about a restaurant booking or a dentist appointment.
    Extract the necessary details and pass them to the appropriate tool:
    - For restaurant bookings, include: firstname, lastname, num_people, booking_datetime.
    - For dentist appointments, include: firstname, lastname, booking_datetime.

    User Prompt: {user_prompt}
    Provide the extracted JSON directly to the tool without additional explanations."""
)

# Initialize the agent
#AgentType.ZERO_SHOT_REACT_DESCRIPTION is a setting in LangChain that makes the agent
# capable of deciding what to do (which tool to use) without needing prior training or multiple examples.
tools = [restaurant_tool, dentist_tool]
chat_model = ChatOpenAI(model="gpt-4o", temperature=0.0, openai_api_key=openai_api_key) #Note temperature set to 0
agent = initialize_agent(tools, chat_model, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

# Process bookings
def process_booking(user_input: str):
    try:
        response = agent.invoke(prompt_template.format_prompt(user_prompt=user_input))
        print(response)
    except Exception as e:
        print(f"Error processing booking: {e}")

# Example prompts
user_prompt_1 = "I want to book a table for 2 at 2:30 PM on January 22, 2024, for John Doe."
#user_prompt_2 = "I need a dentist appointment for Jane Doe at 10 AM on February 3, 2024."

process_booking(user_prompt_1)
#process_booking(user_prompt_1)

