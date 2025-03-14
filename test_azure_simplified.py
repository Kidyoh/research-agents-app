import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def test_connection():
    load_dotenv()
    
    # Use exact values from your working Node.js setup
    api_key = os.environ.get("AZURE_API_KEY")
    endpoint = os.environ.get("AZURE_ENDPOINT")  # This should be https://shega-ai.openai.azure.com/openai
    api_version = os.environ.get("AZURE_API_VERSION")  # This should be 2024-08-01-preview
    deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME")  # This should be gpt-4o-mini
    
    print(f"API Key (masked): {api_key[:5]}...{api_key[-5:]}")
    print(f"Endpoint: {endpoint}")
    print(f"API Version: {api_version}")
    print(f"Deployment: {deployment_name}")
    
    try:
        # Initialize client exactly as in Node.js but with Python syntax
        client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint
        )
        
        # Make a simple request
        response = client.chat.completions.create(
            model=deployment_name,  # In Python we pass the deployment name here
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            temperature=0.7,
            max_tokens=30
        )
        
        print("\n✅ SUCCESS!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_connection()