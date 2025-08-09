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
        
        show_info("CodeBuddy initialized with full development capabilities!")
        show_output("FILE OPERATIONS:")
        show_output("- Read files: 'What's in main.py?'")
        show_output("- Create files: 'Write a Python class for...'")
        show_output("- Search code: 'Find all TODO comments'")
        show_output("- File structure: 'Show me the project structure'")
        show_output("")
        show_output("CODE ANALYSIS:")
        show_output("- Check syntax: 'Validate syntax of main.py'")
        show_output("- Run linter: 'Run pylint on agent.py'")
        show_output("- Find references: 'Find all uses of execute_command'")
        show_output("- Quality report: 'Generate code quality report'")
        show_output("")
        show_output("EXECUTION:")
        show_output("- Run Python: 'Execute main.py'")
        show_output("- Run tests: 'Run tests in current directory'")
        show_output("- Shell commands: 'Run command ls -la'")
        show_output("- Install packages: 'Install requests package'")
        show_output("- Check environment: 'Check development environment'")
        show_output("")
        show_output("SYSTEM:")
        show_output("- Memory: 'clear memory', 'memory stats'")
        show_output("- Debug: Type 'debug' to toggle debug mode")
        show_output("- Exit: Type 'exit' or 'quit' to stop\n")
        
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