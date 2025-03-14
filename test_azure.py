import os
from dotenv import load_dotenv
import requests
from openai import AzureOpenAI

def test_azure_connection():
    load_dotenv()
    
    print("=== Azure OpenAI Connection Test ===")
    
    # Print all relevant environment variables (without showing full API key)
    api_key = os.environ.get("AZURE_API_KEY", "")
    masked_key = api_key[:5] + "..." + api_key[-5:] if len(api_key) > 10 else "Not set"
    
    print(f"AZURE_API_KEY: {masked_key}")
    print(f"AZURE_ENDPOINT: {os.environ.get('AZURE_ENDPOINT', 'Not set')}")
    print(f"AZURE_API_VERSION: {os.environ.get('AZURE_API_VERSION', 'Not set')}")
    print(f"AZURE_DEPLOYMENT_NAME: {os.environ.get('AZURE_DEPLOYMENT_NAME', 'Not set')}")
    
    # Check if we can connect to the endpoint
    endpoint = os.environ.get("AZURE_ENDPOINT", "")
    if endpoint:
        print(f"\nTesting connection to endpoint: {endpoint}")
        try:
            # Simple HEAD request to check if the endpoint is reachable
            response = requests.head(endpoint)
            print(f"Endpoint response status: {response.status_code}")
        except Exception as e:
            print(f"Error connecting to endpoint: {e}")
    
    # Test the actual Azure OpenAI client
    print("\nTesting Azure OpenAI client...")
    try:
        client = AzureOpenAI(
            api_key=os.environ.get("AZURE_API_KEY", ""),
            api_version=os.environ.get("AZURE_API_VERSION", "2024-05-01-preview"),
            azure_endpoint=os.environ.get("AZURE_ENDPOINT", "")
        )
        
        # Try listing models first (this can help diagnose issues)
        try:
            print("\nAttempting to list available models...")
            models = client.models.list()
            print("Available models:")
            for model in models:
                print(f"- {model.id}")
        except Exception as e:
            print(f"Could not list models: {e}")
        
        # Try making a chat completion
        print("\nAttempting to create a chat completion...")
        deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o")
        
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=30
        )
        
        print("\n✅ Chat completion successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ Error with Azure OpenAI client: {e}")
        
        # Provide helpful guidance based on the error
        if "Resource not found" in str(e):
            print("\nSuggestions:")
            print("1. Double-check your AZURE_ENDPOINT value")
            print("2. Make sure the endpoint doesn't need '/openai' at the end")
            print("3. Verify that you have access to this Azure OpenAI resource")
            print("4. Check if your deployment name exists in your Azure OpenAI resource")
            
            # Try alternative endpoint formats
            base_endpoint = os.environ.get("AZURE_ENDPOINT", "")
            if base_endpoint and not base_endpoint.endswith("/openai"):
                print("\nTrying alternative endpoint with '/openai' suffix...")
                try:
                    alt_client = AzureOpenAI(
                        api_key=os.environ.get("AZURE_API_KEY", ""),
                        api_version=os.environ.get("AZURE_API_VERSION", "2024-05-01-preview"),
                        azure_endpoint=f"{base_endpoint}/openai"
                    )
                    
                    alt_response = alt_client.chat.completions.create(
                        model=deployment_name,
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": "Say hello!"}
                        ],
                        max_tokens=30
                    )
                    
                    print("\n✅ Success with alternative endpoint!")
                    print(f"Response: {alt_response.choices[0].message.content}")
                    print("\nPlease update your .env file to use this endpoint format.")
                    return True
                except Exception as alt_e:
                    print(f"Alternative endpoint also failed: {alt_e}")
        
        return False

if __name__ == "__main__":
    test_azure_connection()