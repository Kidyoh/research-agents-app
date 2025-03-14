import json
from openai import AzureOpenAI
from src.utils.azure_client import get_azure_openai_client, get_deployment_name

class ResearchAgent:
    def __init__(self, client=None, model_name=None):
        """
        Initialize the Research Agent.
        
        Args:
            client: The Azure OpenAI client
            model_name: The deployment name to use
        """
        self.facts = []
        self.client = client
        self.model_name = model_name
        print(f"ResearchAgent initialized with deployment: {model_name}")

    def gather_information(self, query):
        """
        Gather information related to the query.
        
        Args:
            query: The research query
            
        Returns:
            A list of facts
        """
        print(f"Gathering information for query: {query}")
        
        # For now, let's generate some mock facts
        # In a real implementation, this would use web search APIs
        
        # Mock search results
        search_queries = [f"{query} overview", f"{query} recent studies", f"{query} key facts"]
        mock_facts = []
        
        try:
            for search_query in search_queries:
                prompt = f"""
                Generate 3 factual pieces of information about "{query}".
                Format each fact as a JSON object with the following structure:
                {{
                    "fact": "the factual statement",
                    "source": "a plausible website URL where this information might be found",
                    "category": "a relevant category for this fact"
                }}
                Return an array of these facts.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a research assistant that provides factual information."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800,
                    response_format={"type": "json_object"}
                )
                
                result = json.loads(response.choices[0].message.content)
                if "facts" in result:
                    mock_facts.extend(result["facts"])
                else:
                    # Handle case where the model didn't return in expected format
                    for key, value in result.items():
                        if isinstance(value, list):
                            mock_facts.extend(value)
        except Exception as e:
            print(f"Error gathering information: {e}")
            # Fallback to default facts
            mock_facts = [
                {
                    "fact": f"This is a sample fact about {query}",
                    "source": "https://example.com/sample",
                    "category": "General"
                },
                {
                    "fact": f"Another example fact related to {query}",
                    "source": "https://research.org/example",
                    "category": "Background"
                }
            ]
        
        self.facts = mock_facts
        return self.facts

    def save_facts(self):
        """Save the collected facts for later use."""
        print("Saving collected facts:")
        for fact in self.facts:
            print(f"Fact: {fact.get('fact', 'Unknown')} (Source: {fact.get('source', 'Unknown')})")
        return self.facts