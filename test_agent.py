import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
# Or if you are using the specific Client-style code from earlier:
from google.genai import types

# Load your API key from the .env file
load_dotenv()

# Initialize the Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Step 1: Define a "Tool" 
# This is a standard Python function.
def get_current_time():
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 2: Register the tool
# We tell Gemini this function exists so it can "call" it.
tools = [get_current_time]

# Step 3: Run the Agent
response = client.models.generate_content(
    model="models/gemini-2.5-flash-preview-09-2025", # Use Flash for testing—it's fast and free
    contents="What time is it right now? Use your tool to find out.",
    config=types.GenerateContentConfig(tools=tools)
)

# Step 4: Output the result
print(f"Agent Response: {response.text}")