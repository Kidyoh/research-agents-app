from dotenv import load_dotenv
import os
from openai import AzureOpenAI

def test_endpoint_variations():
    load_dotenv()
    
    api_key = os.environ.get("AZURE_API_KEY", "CMTkPAl47AxwG9PL2kMbGVbygNgN645uXGOG5NAExzbKaoF2jVtmJQQJ99ALACYeBjFXJ3w3AAAAACOGB59s")
    deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME", "gpt-4o-mini")
    api_version = os.environ.get("AZURE_API_VERSION", "2024-08-01-preview")
    
    # Try different endpoint variations
    endpoint_variations = [
        "https://shega-ai.openai.azure.com",
        "https://shega-ai.openai.azure.com/",
        "https://shega-ai.openai.azure.com/openai",
        "https://shega-ai.openai.azure.com/openai/",
        "https://shega-ai.azure.com", 
        "https://shega-ai.azure.com/openai",
        "https://shega-ai.services.ai.azure.com",
        "https://shega-ai.services.ai.azure.com/openai"
    ]
    
    for i, endpoint in enumerate(endpoint_variations):
        print(f"\n\nTesting endpoint variation #{i+1}: {endpoint}")
        
        try:
            client = AzureOpenAI(
                azure_endpoint=endpoint,
                api_key=api_key,
                api_version=api_version
            )
            
            print("Making API call...")
            response = client.chat.completions.create(
                model=deployment_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say hello briefly."}
                ],
                max_tokens=20
            )
            
            print("\n✅ SUCCESS with this endpoint!")
            print(f"Response: {response.choices[0].message.content}")
            print(f"\nWorking endpoint: {endpoint}")
            
            # Save this to .env file
            with open(".env", "w") as f:
                f.write(f"AZURE_API_KEY={api_key}\n")
                f.write(f"AZURE_ENDPOINT={endpoint}\n")
                f.write(f"AZURE_API_VERSION={api_version}\n")
                f.write(f"AZURE_DEPLOYMENT_NAME={deployment_name}\n")
            
            print("Updated .env file with working endpoint")
            return endpoint
            
        except Exception as e:
            print(f"❌ Error with endpoint {endpoint}: {e}")
    
    print("\n❌ All endpoint variations failed.")
    return None

if __name__ == "__main__":
    test_endpoint_variations()