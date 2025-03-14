import streamlit as st
import time
from src.agents.triage_agent import TriageAgent
from src.agents.research_agent import ResearchAgent
from src.agents.editor_agent import EditorAgent

def run_app(triage_agent, research_agent, editor_agent):
    """
    Main Streamlit application entry point
    
    Args:
        triage_agent: The agent responsible for planning research
        research_agent: The agent responsible for gathering information
        editor_agent: The agent responsible for compiling reports
    """
    st.set_page_config(page_title="Research Assistant", layout="wide")
    
    st.title("AI Research Assistant")
    st.markdown("""
    This application leverages Azure OpenAI to conduct comprehensive research on any topic.
    Enter your research topic below to get started.
    """)
    
    # Input for research topic
    research_topic = st.text_input("Enter your research topic:")
    
    if st.button("Start Research"):
        if research_topic:
            with st.spinner("Planning research strategy..."):
                # Plan research
                research_plan = triage_agent.plan_research(research_topic)
                
            st.subheader("Research Plan")
            st.json(research_plan)
            
            with st.spinner("Gathering information..."):
                # Show progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate research progress
                for i in range(101):
                    progress_bar.progress(i)
                    status_text.text(f"Researching... {i}%")
                    time.sleep(0.05)  # Speed up the progress bar a bit
                
                # Gather information
                facts = research_agent.gather_information(research_topic)
            
            st.subheader("Research Facts")
            for fact in facts:
                st.markdown(f"""
                - **{fact.get('fact', 'No fact available')}**  
                  *Source: [{fact.get('source', 'Unknown')}]({fact.get('source', '#')})*
                """)
            
            with st.spinner("Compiling final report..."):
                # Compile report
                editor_agent.compile_report(facts)
                report = editor_agent.generate_report(research_topic)
            
            st.subheader("Research Report")
            st.markdown(report)
            
            # Download option
            st.download_button(
                label="Download Report as Text",
                data=report,
                file_name=f"{research_topic.replace(' ', '_')}_report.md",
                mime="text/markdown"
            )
            
        else:
            st.warning("Please enter a research topic.")

if __name__ == "__main__":
    triage_agent = TriageAgent()
    research_agent = ResearchAgent()
    editor_agent = EditorAgent()
    run_app(triage_agent, research_agent, editor_agent)