import os
from dotenv import load_dotenv

# 1. Load environment variables from a .env file
load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")
if not gemini_api_key:
    print("Error: GOOGLE_API_KEY not found in environment variables.")
    exit()

# --- 2. LangChain Model Initialization ---
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain.agents import AgentExecutor, create_tool_calling_agent
    from langchain.tools import tool
    from langchain_core.prompts import ChatPromptTemplate
    print("LangChain and Google Generative AI components imported successfully.")
except ImportError as e:
    print(f"Error importing LangChain components: {e}")
    print("Please ensure 'langchain' and 'langchain-google-genai' are installed:")
    print("pip install -U langchain langchain-google-genai python-dotenv")
    exit()

# Define the model name
MODEL_NAME = "gemini-1.5-flash"

try:
    llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7, google_api_key=gemini_api_key)
    print(f"Google Gemini model '{MODEL_NAME}' initialized successfully.")
except Exception as e:
    print(f"Error initializing Google Gemini model: {e}")
    print("Please check your API key and ensure the model name is correct.")
    exit()

# --- 3. Define Tools ---
@tool
def get_current_weather(location: str) -> str:
    """Get the current weather in a given location."""
    if "murukkumpuzha" in location.lower() or "kerala" in location.lower():
        return "The current weather in Murukkumpuzha, Kerala is 30°C and humid with chances of rain."
    elif "new york" in location.lower():
        return "The current weather in New York is 20°C and partly cloudy."
    else:
        return f"Sorry, I don't have weather information for {location}."

@tool
def get_current_time(timezone: str = "Asia/Kolkata") -> str:
    """Get the current time in a specified timezone."""
    from datetime import datetime
    import pytz
    try:
        tz = pytz.timezone(timezone)
        now = datetime.now(tz)
        return now.strftime("%Y-%m-%d %H:%M:%S %Z%z")
    except pytz.exceptions.UnknownTimeZoneError:
        return f"Unknown timezone: {timezone}. Please provide a valid IANA timezone."

@tool
def search_web(query: str) -> str:
    """Performs a web search for the given query and returns the results."""
    print(f"DEBUG: Performing a web search for: '{query}'")
    if "python langchain" in query.lower():
        return "LangChain is a framework for developing applications powered by language models."
    elif "capital of france" in query.lower():
        return "The capital of France is Paris."
    else:
        return f"Search results for '{query}': 'No specific information found.'"

# Create a list of tools
tools = [get_current_weather, get_current_time, search_web]

# --- 4. Define the Agent's Prompt ---
# Simplified prompt to avoid issues with {tools} variable
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant with access to tools for answering questions.
    Use the tools when necessary to provide accurate and helpful responses.
    If a tool is needed, format your response to invoke the tool appropriately."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# --- 5. Create the Agent ---
try:
    agent = create_tool_calling_agent(llm, tools, prompt)
    print("Agent created successfully.")
except Exception as e:
    print(f"Error creating agent: {e}")
    exit()

# --- 6. Create the Agent Executor ---
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# --- 7. Interact with the Agent ---
print("\n--- Agent Ready! ---")
print("You can ask questions like:")
print("- What's the weather in Murukkumpuzha, Kerala?")
print("- What time is it now?")
print("- What is LangChain?")
print("- What is the capital of France?")
print("Type 'exit' to quit.")

while True:
    user_input = input("\nYour command: ")
    if user_input.lower() == 'exit':
        print("Exiting agent.")
        break
    try:
        response = agent_executor.invoke({"input": user_input})
        print("\nAgent's Final Answer:", response["output"])
    except Exception as e:
        print(f"\nAn error occurred while processing your request: {e}")
        print("Please check the terminal for verbose output to debug.")