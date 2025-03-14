import json
from openai import AzureOpenAI
from src.utils.azure_client import get_azure_openai_client, get_deployment_name
from src.utils.document_handler import chunk_text

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
        self.document_content = None
        self.persona_prompt = "You are a research assistant that provides factual information."
        print(f"ResearchAgent initialized with deployment: {model_name}")

    def set_persona(self, persona_prompt):
        """Set the research persona for this agent."""
        self.persona_prompt = persona_prompt
        print(f"Persona set to: {persona_prompt[:50]}...")

    def gather_information(self, query):
        """
        Gather information related to the query.
        
        Args:
            query: The research query
            
        Returns:
            A list of facts
        """
        print(f"Gathering information for query: {query}")
        
        # If we have document content, use that for research
        if self.document_content:
            return self.research_from_document(query)
        else:
            # For now, let's generate some mock facts
            # In a real implementation, this would use web search APIs
            return self.research_from_web(query)

    def research_from_web(self, query):
        """Generate research facts from web search (simulation)."""
        # Mock search queries
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
                        {"role": "system", "content": self.persona_prompt},
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

    def research_from_document(self, query):
        """
        Extract information from uploaded document based on query.
        
        Args:
            query: The research question
            
        Returns:
            List of facts extracted from the document
        """
        document_facts = []
        
        # Split document into manageable chunks to avoid token limits
        chunks = chunk_text(self.document_content)
        
        try:
            for i, chunk in enumerate(chunks):
                prompt = f"""
                Based on the following document content, extract relevant information about "{query}".
                
                Document content:
                {chunk}
                
                Extract 3-5 key facts related to "{query}" from this text.
                For each fact, include:
                1. The fact itself
                2. The source (in this case, cite it as "Uploaded Document")
                3. A relevant category for organizing this information
                
                Format as a JSON array of fact objects.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": self.persona_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=800,
                    response_format={"type": "json_object"}
                )
                
                try:
                    result = json.loads(response.choices[0].message.content)
                    if "facts" in result:
                        document_facts.extend(result["facts"])
                    else:
                        # Handle case where the model didn't return in expected format
                        for key, value in result.items():
                            if isinstance(value, list):
                                document_facts.extend(value)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON from chunk {i}")
                
        except Exception as e:
            print(f"Error extracting from document: {e}")
            document_facts = [{
                "fact": "Could not extract information from the document.",
                "source": "Error processing document",
                "category": "Error"
            }]
        
        self.facts = document_facts
        return self.facts

    def set_document_content(self, content):
        """
        Set the document content for research.
        
        Args:
            content: Text content of the document
        """
        self.document_content = content
        print(f"Document content set ({len(content)} characters)")

    def clear_document_content(self):
        """Clear any document content to return to web research."""
        self.document_content = None
        print("Document content cleared")

    def save_facts(self):
        """Save the collected facts for later use."""
        print("Saving collected facts:")
        for fact in self.facts:
            print(f"Fact: {fact.get('fact', 'Unknown')} (Source: {fact.get('source', 'Unknown')})")
        return self.facts