import os
import sys
from dotenv import load_dotenv

# Add the project root to Python path to make src imports work
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Update imports to reference the src directory
from src.agents.triage_agent import TriageAgent
from src.agents.research_agent import ResearchAgent
from src.agents.editor_agent import EditorAgent
from src.ui.app import run_app
from src.utils.tracing import start_tracing, end_tracing
from src.utils.azure_client import get_azure_openai_client, get_model_name

def main():
    # Load environment variables
    load_dotenv()
    
    # Start tracing
    start_tracing()
    
    # Get Azure OpenAI client and model name
    azure_client = get_azure_openai_client()
    model_name = get_model_name()
    
    # Initialize agents with Azure client
    triage_agent = TriageAgent(client=azure_client, model_name=model_name)
    research_agent = ResearchAgent(client=azure_client, model_name=model_name)
    editor_agent = EditorAgent(client=azure_client, model_name=model_name)

    try:
        # Run the Streamlit application
        run_app(triage_agent, research_agent, editor_agent)
    finally:
        # End tracing
        end_tracing()

if __name__ == "__main__":
    main()