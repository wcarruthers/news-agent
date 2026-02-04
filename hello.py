import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from google import genai
# Or if you are using the specific Client-style code from earlier:
from google.genai import types
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
for model in client.models.list():
    print(f"ID: {model.name}")
    print(f"Display Name: {model.display_name}")
    print(f"Supported Actions: {model.supported_actions}")
    print("-" * 30)

# Define your Gemini Pro Model using your Paid Tier access
gemini_pro = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# Create a simple agent
test_agent = Agent(
    role='System Tester',
    goal='Verify the environment is ready for news scraping.',
    backstory='A helpful assistant ensuring all systems are go.',
    llm=gemini_pro
)

# Define a simple task
test_task = Task(
    description='Write a one-sentence confirmation that you are online and using Gemini Pro.',
    expected_output='A single sentence confirmation.',
    agent=test_agent
)

# Run the crew
crew = Crew(agents=[test_agent], tasks=[test_task])
result = crew.kickoff()

print(f"\n--- Agent Result ---\n{result}")