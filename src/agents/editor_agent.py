from openai import AzureOpenAI
from src.utils.azure_client import get_azure_openai_client, get_deployment_name

class EditorAgent:
    def __init__(self, client=None, model_name=None):
        """
        Initialize the Editor Agent.
        
        Args:
            client: The Azure OpenAI client
            model_name: The deployment name to use
        """
        self.report = None
        self.client = client
        self.model_name = model_name
        print(f"EditorAgent initialized with deployment: {model_name}")

    def compile_report(self, facts):
        """Compile a report from gathered facts."""
        self.report = self.organize_facts(facts)
        return self.report

    def organize_facts(self, facts):
        """Organize facts into categories."""
        if not facts:
            return {"General": [{"fact": "No facts were collected", "source": "N/A"}]}
        
        organized_facts = {}
        for fact in facts:
            category = fact.get('category', 'General')
            if category not in organized_facts:
                organized_facts[category] = []
            organized_facts[category].append(fact)
        return organized_facts

    def generate_report(self, query):
        """Generate a final report using Azure OpenAI."""
        if self.report is None:
            raise ValueError("No report compiled. Please compile the report first.")
        
        # Convert organized facts to text format
        report_sections = []
        for category, facts in self.report.items():
            section_facts = "\n".join([f"- {fact.get('fact', 'No fact provided')} (Source: {fact.get('source', 'Unknown')})" for fact in facts])
            report_sections.append(f"## {category}\n{section_facts}")
        
        facts_text = "\n\n".join(report_sections)
        
        # Use Azure OpenAI to generate a coherent report
        try:
            prompt = f"""
            Generate a comprehensive research report about "{query}" based on the following facts:
            
            {facts_text}
            
            Format the report with the following sections:
            1. Executive Summary
            2. Key Findings
            3. Detailed Analysis
            4. Conclusions
            5. References
            """
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a research editor that creates well-structured, informative reports."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating report: {e}")
            # Fallback to basic report
            return f"""
            # Research Report: {query}
            
            ## Executive Summary
            This is an automatically generated report about {query}.
            
            ## Key Findings
            {facts_text}
            
            ## Conclusions
            More detailed research is needed in this area.
            
            ## References
            See sources listed with each fact.
            """