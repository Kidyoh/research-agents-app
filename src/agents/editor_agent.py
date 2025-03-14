from openai import AzureOpenAI
import json

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
        self.persona_prompt = "You are a research editor that creates well-structured, informative reports."
        print(f"EditorAgent initialized with deployment: {model_name}")

    def set_persona(self, persona_prompt):
        """Set the editor persona for this agent."""
        self.persona_prompt = persona_prompt
        print(f"Persona set to: {persona_prompt[:50]}...")

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

    def generate_report(self, query, include_visuals=False, include_counter_points=False, max_tokens=3000):
        """Generate a final report using Azure OpenAI with additional options."""
        if self.report is None:
            raise ValueError("No report compiled. Please compile the report first.")
        
        # Convert organized facts to text format
        report_sections = []
        for category, facts in self.report.items():
            section_facts = "\n".join([f"- {fact.get('fact', 'No fact provided')} (Source: {fact.get('source', 'Unknown')})" for fact in facts])
            report_sections.append(f"## {category}\n{section_facts}")
        
        facts_text = "\n\n".join(report_sections)
        
        # Build prompt with options
        prompt = f"""
        Generate a comprehensive research report about "{query}" based on the following facts:
        
        {facts_text}
        
        Format the report with the following sections:
        1. Executive Summary
        2. Key Findings
        3. Detailed Analysis
        4. Conclusions
        5. References
        
        For the references section, properly list all sources cited in the research.
        Make sure each fact is properly attributed to its source in the text.
        
        Format the report in Markdown. Use proper headings, bullet points, and links.
        Use markdown links for citations where appropriate.
        """
        
        if include_visuals:
            prompt += "\n\nSuggest what kinds of charts, graphs, or visual aids would complement this report and why."
        
        if include_counter_points:
            prompt += "\n\nInclude a section on alternative perspectives or counter-arguments to provide a balanced view."
        
        # Use Azure OpenAI to generate a coherent report
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.persona_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=max_tokens
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
    
    def generate_report_with_style(self, query, style="academic"):
        """
        Generate a report with a specific style.
        
        Args:
            query: The research query
            style: The style to use (academic, journalistic, business, etc.)
            
        Returns:
            The formatted report
        """
        # Adjust the persona prompt based on style
        style_prompts = {
            "academic": "You are a scholarly editor creating an academic research report with rigorous citations.",
            "journalistic": "You are a journalist editor creating an engaging news-style report.",
            "business": "You are a business analyst creating an executive-friendly report with actionable insights.",
            "technical": "You are a technical writer creating a detailed technical report."
        }
        
        original_prompt = self.persona_prompt
        self.persona_prompt = style_prompts.get(style, original_prompt)
        
        # Generate the report
        report = self.generate_report(query)
        
        # Restore the original prompt
        self.persona_prompt = original_prompt
        
        return report