import json
from src.utils.azure_client import get_azure_openai_client, get_deployment_name

class TriageAgent:
    def __init__(self, client=None, model_name=None):
        """
        Initialize the Triage Agent.
        
        Args:
            client: The Azure OpenAI client
            model_name: The deployment name to use
        """
        self.research_plan = {}
        self.client = client
        self.model_name = model_name
        print(f"TriageAgent initialized with deployment: {model_name}")

    def plan_research(self, query):
        """
        Create a structured research plan based on the user's query.
        
        Args:
            query: The research question or topic
            
        Returns:
            A dictionary containing the research plan
        """
        # Create a structured research plan based on the user's query using Azure OpenAI
        prompt = f"""
        Create a research plan for the query: "{query}"
        The plan should include:
        1. Main research objectives
        2. Key search queries
        3. Focus areas for research
        
        Return the plan as a JSON object with the format:
        {{
            "query": "the main query",
            "search_queries": ["query 1", "query 2", ...],
            "focus_areas": ["area 1", "area 2", ...],
            "main_objectives": ["objective 1", "objective 2", ...]
        }}
        """
        
        try:
            print(f"Calling Azure OpenAI with model: {self.model_name}")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a research planner that creates detailed research strategies."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800,
                response_format={"type": "json_object"}
            )
            
            print("Successfully received response from Azure OpenAI")
            self.research_plan = json.loads(response.choices[0].message.content)
            # Ensure the required fields are present
            self.research_plan.setdefault('query', query)
            self.research_plan.setdefault('search_queries', self.generate_search_queries(query))
            self.research_plan.setdefault('focus_areas', self.identify_focus_areas(query))
            self.research_plan.setdefault('main_objectives', ["Understand key concepts", "Identify major findings", "Synthesize information"])
        except Exception as e:
            print(f"Error calling Azure OpenAI: {e}")
            print("Using fallback research plan")
            # Fallback to default plan creation
            self.research_plan = {
                'query': query,
                'search_queries': self.generate_search_queries(query),
                'focus_areas': self.identify_focus_areas(query),
                'main_objectives': ["Understand key concepts", "Identify major findings", "Synthesize information"]
            }
        
        return self.research_plan

    def generate_search_queries(self, query):
        """Generate search queries based on the main query."""
        return [f"{query} overview", f"{query} recent studies", f"{query} key facts"]

    def identify_focus_areas(self, query):
        """Identify focus areas for the research based on the query."""
        return ['Background', 'Recent Developments', 'Key Challenges']

    def coordinate_workflow(self, research_agent, editor_agent):
        """
        Coordinate the complete research workflow.
        
        Args:
            research_agent: The agent responsible for gathering information
            editor_agent: The agent responsible for compiling reports
            
        Returns:
            The final research report
        """
        # Execute research using the research agent
        facts = research_agent.gather_information(self.research_plan['query'])
        
        # Save the facts
        research_agent.save_facts()
        
        # Have the editor compile and generate a report
        editor_agent.compile_report(facts)
        report = editor_agent.generate_report(self.research_plan['query'])
        
        return report