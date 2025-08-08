from agent.llm_provider import GeminiProvider
from tools.file_tools import read_file
from cli.interface import get_user_input, show_output
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def main():
    if not GEMINI_API_KEY:
        show_output("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")
        return

    llm = GeminiProvider(api_key=GEMINI_API_KEY)
    while True:
        user_query = get_user_input()
        if user_query.lower() in ["exit", "quit"]:
            break

        # Perceive: Check if user asks about a file
        if "package.json" in user_query:
            file_content = read_file("package.json")
            prompt = f"Summarize the following file content:\n{file_content}"
            # Reason: Use LLM to summarize
            summary = llm.ask(prompt)
            # Act: Show output
            show_output(summary)
            # Learn: (for now, just print; later, store context)
        else:
            show_output("I can currently answer questions about package.json. More features coming soon!")

if __name__ == "__main__":
    main()