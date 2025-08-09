from agent.llm_provider import GeminiProvider
from agent.agent import Agent
from cli.interface import get_user_input, show_output, show_info, show_error
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    if not GEMINI_API_KEY:
        show_error("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
        return

    try:
        llm = GeminiProvider(api_key=GEMINI_API_KEY, mock_mode=False)
        agent = Agent(llm)
        
        show_info("CodeBuddy initialized with memory! Available commands:")
        show_output("- Ask about files: 'What's in main.py?'")
        show_output("- Search code: 'Find all TODO comments'") 
        show_output("- View structure: 'Show me the project structure'")
        show_output("- Create files: 'Write a Python class for...'")
        show_output("- Memory commands: 'clear memory', 'memory stats'")
        show_output("- Type 'debug' to toggle debug mode")
        show_output("- Type 'exit' or 'quit' to stop\n")
        
        while True:
            try:
                user_query = get_user_input()
                if user_query.lower() in ["exit", "quit"]:
                    break
                elif user_query.lower() == "debug":
                    agent.toggle_debug()
                    continue

                response = agent.execute_command(user_query)
                
                if response:
                    show_output(response)
                    
            except Exception as e:
                show_error(f"Error processing command: {e}")

    except Exception as e:
        show_error(f"Error initializing CodeBuddy: {e}")

if __name__ == "__main__":
    main()