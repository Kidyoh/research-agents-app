from typing import Dict, List, Optional
import json

# Define different research personas
RESEARCH_PERSONAS = {
    "academic": {
        "name": "Academic Researcher",
        "description": "Specializes in rigorous academic research with proper citations and methodology.",
        "system_prompt": "You are an Academic Researcher specializing in thorough literature review and methodical analysis. Focus on peer-reviewed sources, proper citations, and balanced viewpoints. Maintain academic rigor and precision in your research."
    },
    "journalist": {
        "name": "Investigative Journalist",
        "description": "Focuses on uncovering facts, interviewing sources, and presenting balanced narratives.",
        "system_prompt": "You are an Investigative Journalist skilled at fact-finding and source verification. Focus on uncovering the truth, presenting multiple perspectives, and explaining complex topics clearly. Prioritize factual accuracy, balance, and public interest in your research."
    },
    "business": {
        "name": "Business Analyst",
        "description": "Specializes in market trends, competitive analysis, and business implications.",
        "system_prompt": "You are a Business Analyst expert in market research and competitive analysis. Focus on industry trends, market data, competitive positioning, and business implications. Provide actionable insights and data-driven recommendations in your research."
    },
    "technical": {
        "name": "Technical Specialist",
        "description": "Focuses on technical details, specifications, and implementation considerations.",
        "system_prompt": "You are a Technical Specialist with deep expertise in analyzing technologies and systems. Focus on technical specifications, implementation details, and practical applications. Provide thorough technical analysis with clear explanations in your research."
    },
    "medical": {
        "name": "Medical Researcher",
        "description": "Specializes in medical and health-related research with proper clinical context.",
        "system_prompt": "You are a Medical Researcher focusing on health-related topics. Emphasize evidence-based information, clinical relevance, and patient impact. Maintain scientific accuracy while making medical information accessible in your research."
    }
}

def get_personas_list():
    """
    Get a list of available personas
    
    Returns:
        List of persona dictionaries with name and description
    """
    return [
        {"id": persona_id, "name": persona["name"], "description": persona["description"]}
        for persona_id, persona in RESEARCH_PERSONAS.items()
    ]

def get_persona_system_prompt(persona_id: str) -> str:
    """
    Get the system prompt for a specific persona
    
    Args:
        persona_id: ID of the persona
        
    Returns:
        The system prompt for this persona
    """
    if persona_id not in RESEARCH_PERSONAS:
        # Default to academic if persona not found
        persona_id = "academic"
    
    return RESEARCH_PERSONAS[persona_id]["system_prompt"]

def create_custom_persona(name: str, description: str, system_prompt: str) -> str:
    """
    Create a custom research persona
    
    Args:
        name: Name of the persona
        description: Description of the persona
        system_prompt: System prompt for this persona
        
    Returns:
        ID of the new persona
    """
    # Create a simple ID from the name
    persona_id = name.lower().replace(" ", "_")
    
    # Store the new persona (in a real app, you might save this to a database)
    RESEARCH_PERSONAS[persona_id] = {
        "name": name,
        "description": description,
        "system_prompt": system_prompt
    }
    
    return persona_id