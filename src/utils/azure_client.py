import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv()

def get_azure_openai_client():
    """
    Initialize and return Azure OpenAI client using environment variables.
    """
    # Get environment variables
    azure_endpoint = os.environ.get("AZURE_ENDPOINT")
    api_key = os.environ.get("AZURE_API_KEY")
    api_version = os.environ.get("AZURE_API_VERSION", "2024-08-01-preview")
    
    if not azure_endpoint:
        raise ValueError("AZURE_ENDPOINT must be set in environment variables")
    
    if not api_key:
        raise ValueError("AZURE_API_KEY must be set in environment variables")
    
    # Ensure the endpoint doesn't already have /openai (the SDK adds it)
    if azure_endpoint.endswith("/openai"):
        azure_endpoint = azure_endpoint.rstrip("/openai")
    
    # Print diagnostic information
    print(f"Connecting to Azure OpenAI at: {azure_endpoint}")
    print(f"Using API version: {api_version}")
    
    # Create Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=azure_endpoint,
        api_key=api_key,
        api_version=api_version
    )
    
    return client

def get_model_name():
    """
    Return the deployment name from environment variables.
    """
    deployment_name = os.environ.get("AZURE_DEPLOYMENT_NAME")
    if not deployment_name:
        deployment_name = "gpt-4o-mini"
    
    print(f"Using deployment: {deployment_name}")
    return deployment_name

def get_deployment_name():
    """
    Alias for get_model_name() - returns the deployment name.
    """
    return get_model_name()