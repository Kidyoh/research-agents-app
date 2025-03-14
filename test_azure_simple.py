from dotenv import load_dotenv
from src.utils.azure_client import get_azure_openai_client, get_deployment_name

def test_azure_connection():
    print("Testing Azure OpenAI connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get client and model name
    client = get_azure_openai_client()
    deployment_name = get_deployment_name()
    
    # Make a simple request
    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=30
        )
        
        print("\n✅ Connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_azure_connection()