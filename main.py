import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import TavilySearchTool #
from supabase import create_client
import resend
import time

def run_news_briefing():
    # 1. Load Keys
    load_dotenv()
    # Initialize the Search Tool
    supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

    search_tool = TavilySearchTool()

    # Define your Gemini Pro Model
    gemini_pro = LLM(
        model="gemini/gemini-flash-latest",
        api_key=os.getenv("GEMINI_API_KEY")
    )

    # Agents
    scout = Agent(
        role='News Scout',
        goal='Find 3 Memphis tech news stories from the last 24 hours.',
        #expected_output='A list of 3 news stories with summaries and source URLs.',
        backstory='Expert researcher at finding local signals in global noise.',
        tools=[search_tool],
        llm=gemini_pro # Use your Gemini Pro here
    )

    editor = Agent(
        role='Chief Editor',
        goal='Summarize the news into a punchy, 3-bullet briefing for a busy executive.',
        #expected_output='A summarized briefing for each news story.',
        backstory='You specialize in taking raw data and making it readable and actionable.',
        llm=gemini_pro
    )

    # Tasks
    scout_task = Task(description='Search for Memphis tech news.', agent=scout, expected_output='A list of 3 news stories with summaries and source URLs.')

    edit_task = Task(
        description='Summarize the findings from the scout into a professional briefing.',
        expected_output='A Markdown formatted summary.',
        agent=editor,
        context=[scout_task] # This passes the scout's output to the editor
    )

    # 4. Execute Crew
    news_crew = Crew(
        agents=[scout, editor],
        tasks=[scout_task, edit_task],
        step_callback=lambda x: time.sleep(2)
        verbose=True
    )
    
    final_briefing = news_crew.kickoff()

    # 5. Persistence (Database Storage)
    # We save as a string to ensure compatibility with Supabase 'text' columns
    try:
        supabase.table("news_briefings").insert({
            "content": str(final_briefing), 
            "category": "Memphis Tech"
        }).execute()
        print("\n✅ Successfully saved to Supabase.")
    except Exception as e:
        print(f"\n❌ Database Error: {e}")

    return final_briefing

import resend

# Add this inside your run_news_briefing() function after the editor finishes
def send_email_briefing(content):
    resend.api_key = os.getenv("RESEND_API_KEY")
    
    params = {
        "from": "Memphis News Agent <onboarding@resend.dev>",
        "to": os.getenv("EMAIL_TO"), # Put your real email here
        "subject": "Your Daily Memphis Tech Briefing",
        "html": f"<div>{content}</div>",
    }
    
    resend.Emails.send(params)
    print("📧 Email sent successfully!")

# Call it before the function returns


if __name__ == "__main__":
    # The entry point of your script
    print("🚀 Starting Daily News Briefing...\n")
    
    result = run_news_briefing()
    
    print("\n--- FINAL BRIEFING ---")
    print(result)

    send_email_briefing(result)

    print("🔔 Email sent successfully!")