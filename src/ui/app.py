import streamlit as st
import time
import os
import pandas as pd
import base64
from datetime import datetime
import json
from io import BytesIO
import PyPDF2
import docx2txt
import markdown2
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from src.agents.triage_agent import TriageAgent
from src.agents.research_agent import ResearchAgent
from src.agents.editor_agent import EditorAgent

# Additional imports for better visualizations
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import networkx as nx
from urllib.parse import urlparse
import random

def run_app(triage_agent, research_agent, editor_agent):
    """
    Main Streamlit application entry point with enhanced visualizations.
    
    Args:
        triage_agent: The agent responsible for planning research
        research_agent: The agent responsible for gathering information
        editor_agent: The agent responsible for compiling reports
    """
    st.set_page_config(page_title="AI Research Assistant", layout="wide")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for configuration
    with st.sidebar:
        show_sidebar_content(triage_agent, research_agent, editor_agent)
    
    # Main panel with tabs
    st.title("AI Research Assistant")
    
    research_tab, visualize_tab, chat_tab, about_tab = st.tabs([
        "Research Generator", 
        "Research Visualization", 
        "Chat with Documents", 
        "About"
    ])
    
    with research_tab:
        show_research_tab(triage_agent, research_agent, editor_agent)
    
    with visualize_tab:
        show_visualization_tab()
    
    with chat_tab:
        show_chat_tab(research_agent)
    
    with about_tab:
        show_about_tab()

def initialize_session_state():
    """Initialize all session state variables."""
    if "uploaded_docs" not in st.session_state:
        st.session_state.uploaded_docs = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "current_persona" not in st.session_state:
        st.session_state.current_persona = "default"
    if "generated_report" not in st.session_state:
        st.session_state.generated_report = ""
    if "research_topic" not in st.session_state:
        st.session_state.research_topic = ""
    if "research_plan" not in st.session_state:
        st.session_state.research_plan = {}
    if "research_facts" not in st.session_state:
        st.session_state.research_facts = []
    if "research_queries" not in st.session_state:
        st.session_state.research_queries = []
    if "research_sources" not in st.session_state:
        st.session_state.research_sources = set()
    if "research_categories" not in st.session_state:
        st.session_state.research_categories = {}
    if "visualization_type" not in st.session_state:
        st.session_state.visualization_type = "facts_by_category"

def show_sidebar_content(triage_agent, research_agent, editor_agent):
    """Display sidebar content for the app."""
    st.title("Settings")
    
    # Persona selection
    st.subheader("Choose Research Persona")
    persona_options = {
        "default": "Standard Research Assistant",
        "academic": "Academic Scholar",
        "journalistic": "Investigative Journalist",
        "business": "Business Analyst",
        "technical": "Technical Expert"
    }
    
    selected_persona = st.selectbox(
        "Select a research persona:",
        list(persona_options.keys()),
        format_func=lambda x: persona_options[x],
        key="persona_selector"
    )
    
    if selected_persona != st.session_state.current_persona:
        st.session_state.current_persona = selected_persona
        
        # Set persona descriptions
        persona_descriptions = {
            "default": "You are a research editor that creates well-structured, informative reports.",
            "academic": "You are a scholarly editor with expertise in academic writing. Create a rigorous research report with proper citations, methodology discussion, and literature context.",
            "journalistic": "You are an investigative journalist uncovering insights on this topic. Create an engaging narrative with key findings, quotes, and impactful conclusions.",
            "business": "You are a business analyst providing actionable insights. Create an executive-friendly report with market implications, opportunities, and strategic recommendations.",
            "technical": "You are a technical expert analyzing this subject. Create a detailed technical report with specifications, processes, and technical implications."
        }
        
        # Set the persona for the editor agent
        editor_agent.set_persona(persona_descriptions[selected_persona])
        st.success(f"Switched to {persona_options[selected_persona]} persona")
    
    # Document upload section
    st.subheader("Upload Documents")
    uploaded_file = st.file_uploader(
        "Upload research materials (PDF, DOCX, TXT)", 
        type=["pdf", "docx", "txt"],
        key="doc_uploader"
    )
    
    if uploaded_file is not None:
        # Extract and store document content
        doc_content = extract_document_text(uploaded_file)
        doc_name = uploaded_file.name
        
        if doc_content:
            st.session_state.uploaded_docs[doc_name] = doc_content
            st.success(f"Successfully uploaded: {doc_name}")
            
    # Show uploaded documents
    if st.session_state.uploaded_docs:
        st.subheader("Uploaded Documents")
        for doc_name in st.session_state.uploaded_docs.keys():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {doc_name}")
            with col2:
                if st.button("Remove", key=f"remove_{doc_name}"):
                    del st.session_state.uploaded_docs[doc_name]
                    st.rerun()
    
    # Help information
    with st.expander("How to use this app"):
        st.markdown("""
        1. **Select a research persona** that matches your needs
        2. **Upload relevant documents** (optional)
        3. **Enter your research topic** in the main panel
        4. **Start research** to generate a comprehensive report
        5. **View the research process** in the visualization tab
        6. **Download** your report in your preferred format
        """)

def show_research_tab(triage_agent, research_agent, editor_agent):
    """Display the main research tab content."""
    st.markdown("""
    This tool uses AI to conduct comprehensive research on any topic, 
    creating well-structured reports with proper citations.
    """)
    
    # Input for research topic
    research_topic = st.text_input(
        "Enter your research topic:",
        key="research_topic_input",
        help="Be specific with your research question for better results"
    )
    
    # Store the research topic in session state
    if research_topic:
        st.session_state.research_topic = research_topic
    
    # Research options (collapsible)
    with st.expander("Research Options"):
        col1, col2 = st.columns(2)
        with col1:
            depth = st.select_slider(
                "Research Depth",
                options=["Basic", "Standard", "Comprehensive"],
                value="Standard"
            )
        with col2:
            include_visuals = st.checkbox("Suggest visualizations", value=True)
            include_counter_points = st.checkbox("Include counter perspectives", value=True)
    
    # Start research button
    if st.button("Start Research", key="start_research", type="primary"):
        if research_topic:
            # Process research with all available info
            process_research(
                research_topic, 
                triage_agent, 
                research_agent, 
                editor_agent,
                st.session_state.uploaded_docs,
                depth,
                include_visuals,
                include_counter_points
            )
        else:
            st.warning("Please enter a research topic.")
    
    # Display generated report if available
    if st.session_state.generated_report:
        st.subheader("Research Report")
        
        # Display tabs for different views of the report
        report_view_tab, markdown_tab = st.tabs(["Formatted Report", "Markdown Source"])
        
        with report_view_tab:
            st.markdown(st.session_state.generated_report)
        
        with markdown_tab:
            st.code(st.session_state.generated_report, language="markdown")
        
        # Download options
        st.subheader("Download Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Download as Markdown
            st.download_button(
                label="Download as Markdown",
                data=st.session_state.generated_report,
                file_name=f"{research_topic.replace(' ', '_')}_report.md",
                mime="text/markdown",
            )
        
        with col2:
            # Download as PDF
            pdf_bytes = convert_markdown_to_pdf(st.session_state.generated_report, research_topic)
            st.download_button(
                label="Download as PDF",
                data=pdf_bytes,
                file_name=f"{research_topic.replace(' ', '_')}_report.pdf",
                mime="application/pdf",
            )
        
        with col3:
            # Download as HTML
            html_content = markdown2.markdown(st.session_state.generated_report)
            st.download_button(
                label="Download as HTML",
                data=html_content,
                file_name=f"{research_topic.replace(' ', '_')}_report.html",
                mime="text/html",
            )

def show_visualization_tab():
    """Display the research visualization tab with enhanced visualizations."""
    st.subheader("Research Process Visualization")
    
    if not st.session_state.research_plan:
        st.info("No research has been conducted yet. Start a research to see visualizations.")
        return
    
    # Display research plan
    st.markdown("### Research Plan")
    
    # Show the research plan in a nice format
    with st.expander("Research Plan Details", expanded=True):
        if "query" in st.session_state.research_plan:
            st.markdown(f"**Main Query**: {st.session_state.research_plan['query']}")
        
        if "main_objectives" in st.session_state.research_plan:
            st.markdown("**Main Objectives**:")
            for obj in st.session_state.research_plan['main_objectives']:
                st.markdown(f"- {obj}")
        
        if "search_queries" in st.session_state.research_plan:
            st.markdown("**Search Queries**:")
            for query in st.session_state.research_plan['search_queries']:
                st.markdown(f"- {query}")
        
        if "focus_areas" in st.session_state.research_plan:
            st.markdown("**Focus Areas**:")
            for area in st.session_state.research_plan['focus_areas']:
                st.markdown(f"- {area}")
    
    # Select visualization type
    st.markdown("### Visualizations")
    viz_options = {
        "facts_by_category": "Facts by Category",
        "source_distribution": "Source Distribution",
        "search_exploration": "Search Exploration Map",
        "knowledge_graph": "Knowledge Graph",
        "topic_word_cloud": "Topic Word Cloud"
    }
    
    col1, col2 = st.columns([3, 1])
    with col1:
        selected_viz = st.selectbox(
            "Select visualization type:",
            list(viz_options.keys()),
            format_func=lambda x: viz_options[x],
            key="viz_selector"
        )
    
    with col2:
        enable_3d = st.checkbox("Enable 3D effects", value=False)
    
    st.session_state.visualization_type = selected_viz
    
    # Display the selected visualization
    if selected_viz == "facts_by_category":
        show_facts_by_category(enable_3d)
    elif selected_viz == "source_distribution":
        show_source_distribution(enable_3d)
    elif selected_viz == "search_exploration":
        show_search_exploration_map(enable_3d)
    elif selected_viz == "knowledge_graph":
        show_knowledge_graph()
    elif selected_viz == "topic_word_cloud":
        show_topic_word_cloud()
    
    # Research Resources Section
    st.markdown("### Research Resources")
    
    # Show search queries used
    if st.session_state.research_queries:
        with st.expander("Search Queries Used", expanded=True):
            for i, query_data in enumerate(st.session_state.research_queries):
                st.markdown(f"**{i+1}. {query_data['query']}**")
                st.caption(f"Timestamp: {query_data['timestamp']}")
    
    # Show sources discovered
    if st.session_state.research_sources:
        with st.expander("Sources Discovered", expanded=True):
            sources_list = list(st.session_state.research_sources)
            for i, source in enumerate(sources_list):
                domain = urlparse(source).netloc if urlparse(source).netloc else source
                st.markdown(f"**{i+1}. [{domain}]({source})**")
    
    # Raw data display
    with st.expander("View Raw Research Data"):
        st.markdown("### Research Facts")
        if st.session_state.research_facts:
            # Show cleaner table with pandas styler
            facts_df = pd.DataFrame(st.session_state.research_facts)
            if not facts_df.empty:
                # Select and reorder columns for better display
                cols_to_show = ['fact', 'source', 'category', 'query']
                cols_to_show = [col for col in cols_to_show if col in facts_df.columns]
                st.dataframe(facts_df[cols_to_show], use_container_width=True)
        else:
            st.info("No facts collected yet.")

# Enhanced category visualization
def show_facts_by_category(enable_3d=False):
    """Show enhanced visualization of facts by category."""
    if not st.session_state.research_facts:
        st.info("No facts have been collected yet.")
        return
    
    # Count facts by category
    categories = {}
    for fact in st.session_state.research_facts:
        category = fact.get('category', 'General')
        if category not in categories:
            categories[category] = 0
        categories[category] += 1
    
    # Create a dataframe for visualization
    viz_data = pd.DataFrame({
        'Category': list(categories.keys()),
        'Number of Facts': list(categories.values())
    })
    
    st.markdown("#### Facts Distribution by Category")
    
    # Use plotly for better visualization
    if enable_3d:
        fig = px.bar_3d(
            viz_data, 
            x='Category', 
            y='Number of Facts', 
            z=[1]*len(categories),
            color='Number of Facts',
            height=500,
            title="Facts by Category (3D View)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        fig = px.bar(
            viz_data, 
            x='Category', 
            y='Number of Facts',
            color='Number of Facts',
            color_continuous_scale='Viridis',
            labels={'Number of Facts': 'Count'},
            height=500,
            title="Facts by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Show facts by category
    st.markdown("#### Facts by Category")
    for category, count in categories.items():
        with st.expander(f"{category} ({count} facts)", expanded=True):
            for fact in st.session_state.research_facts:
                if fact.get('category', 'General') == category:
                    st.markdown(f"- **Fact**: {fact.get('fact', 'No fact available')}")
                    st.markdown(f"  **Source**: [{fact.get('source', 'Unknown')}]({fact.get('source', '#')})")
                    if 'query' in fact:
                        st.caption(f"Search query: {fact.get('query', 'General search')}")

# Enhanced source distribution visualization
def show_source_distribution(enable_3d=False):
    """Show enhanced visualization of sources used."""
    if not st.session_state.research_facts:
        st.info("No facts have been collected yet.")
        return
    
    # Extract unique sources
    sources = {}
    domains = {}
    
    for fact in st.session_state.research_facts:
        source = fact.get('source', 'Unknown')
        if source not in sources:
            sources[source] = 0
        sources[source] += 1
        
        # Extract domain for grouping
        domain = urlparse(source).netloc if urlparse(source).netloc else "Unknown"
        if domain not in domains:
            domains[domain] = 0
        domains[domain] += 1
    
    # Create dataframes for visualization
    source_df = pd.DataFrame({
        'Source': list(sources.keys()),
        'Number of Facts': list(sources.values())
    })
    
    domain_df = pd.DataFrame({
        'Domain': list(domains.keys()),
        'Number of Facts': list(domains.values())
    })
    
    # Create tabs for different views
    source_tab, domain_tab = st.tabs(["Sources", "Domains"])
    
    with domain_tab:
        st.markdown("#### Source Distribution by Domain")
        
        if enable_3d:
            domain_fig = px.pie_3d(
                domain_df,
                values='Number of Facts',
                names='Domain',
                title="Facts by Domain (3D)",
                height=600
            )
            st.plotly_chart(domain_fig, use_container_width=True)
        else:
            domain_fig = px.pie(
                domain_df,
                values='Number of Facts',
                names='Domain',
                title="Facts by Domain",
                height=500
            )
            st.plotly_chart(domain_fig, use_container_width=True)
    
    with source_tab:
        st.markdown("#### Source Distribution by URL")
        
        if enable_3d:
            source_fig = go.Figure(data=[go.Scatter3d(
                x=[random.random() for _ in sources],
                y=[random.random() for _ in sources],
                z=list(sources.values()),
                mode='markers',
                marker=dict(
                    size=10,
                    color=list(sources.values()),
                    colorscale='Viridis',
                    opacity=0.8,
                    colorbar=dict(title="Number of Facts")
                ),
                text=list(sources.keys()),
                hoverinfo='text+z'
            )])
            source_fig.update_layout(
                title="Sources in 3D Space",
                height=600,
                scene=dict(
                    xaxis_title="X",
                    yaxis_title="Y",
                    zaxis_title="Number of Facts"
                )
            )
            st.plotly_chart(source_fig, use_container_width=True)
        else:
            source_fig = px.treemap(
                source_df,
                path=['Source'],
                values='Number of Facts',
                color='Number of Facts',
                color_continuous_scale='RdBu',
                title="Sources Treemap"
            )
            st.plotly_chart(source_fig, use_container_width=True)
    
    # Show facts by source
    st.markdown("#### Facts by Source")
    for source, count in sources.items():
        with st.expander(f"{source} ({count} facts)", expanded=False):
            for fact in st.session_state.research_facts:
                if fact.get('source', 'Unknown') == source:
                    st.markdown(f"- **Fact**: {fact.get('fact', 'No fact available')}")
                    st.markdown(f"  **Category**: {fact.get('category', 'General')}")
                    if 'query' in fact:
                        st.caption(f"Search query: {fact.get('query', 'General search')}")

# New visualization: Search exploration map
def show_search_exploration_map(enable_3d=False):
    """Show visualization of how search queries led to discoveries."""
    if not st.session_state.research_facts or not st.session_state.research_queries:
        st.info("No search exploration data is available yet.")
        return
    
    # Create a mapping of queries to facts
    query_facts = {}
    for fact in st.session_state.research_facts:
        query = fact.get('query', 'Unknown')
        if query not in query_facts:
            query_facts[query] = []
        query_facts[query].append(fact)
    
    # Create nodes for visualization
    nodes = []
    edges = []
    
    # Main topic node
    if "query" in st.session_state.research_plan:
        main_topic = st.session_state.research_plan["query"]
        nodes.append({"id": "topic", "label": main_topic, "type": "topic"})
    
        # Add search query nodes connected to main topic
        for i, query_data in enumerate(st.session_state.research_queries):
            query = query_data["query"]
            query_id = f"query_{i}"
            nodes.append({"id": query_id, "label": query, "type": "query"})
            edges.append({"from": "topic", "to": query_id})
            
            # Add fact nodes connected to queries
            if query in query_facts:
                for j, fact in enumerate(query_facts[query]):
                    fact_id = f"fact_{i}_{j}"
                    nodes.append({
                        "id": fact_id, 
                        "label": fact.get("fact", "")[:50] + "..." if len(fact.get("fact", "")) > 50 else fact.get("fact", ""),
                        "type": "fact",
                        "category": fact.get("category", "General")
                    })
                    edges.append({"from": query_id, "to": fact_id})
    
    # Create network visualization
    st.markdown("#### Research Exploration Map")
    st.markdown("This visualization shows how the research topic led to search queries, which in turn yielded facts.")
    
    # Use NetworkX to create a graph
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for node in nodes:
        G.add_node(node["id"], label=node["label"], type=node.get("type", "unknown"))
    
    # Add edges
    for edge in edges:
        G.add_edge(edge["from"], edge["to"])
    
    # Visualize using matplotlib
    plt.figure(figsize=(10, 8))
    
    # Set node colors based on type
    node_colors = []
    for node in G.nodes(data=True):
        node_type = node[1].get('type', 'unknown')
        if node_type == 'topic':
            node_colors.append('red')
        elif node_type == 'query':
            node_colors.append('blue')
        else:
            node_colors.append('green')
    
    # Use spring layout
    pos = nx.spring_layout(G, seed=42)
    
    # Draw the network
    nx.draw(
        G, 
        pos, 
        with_labels=True,
        node_color=node_colors,
        node_size=700,
        font_size=8,
        font_color="white",
        edge_color="gray",
        arrows=True
    )
    
    # Save to buffer
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Show image
    st.image(buf, use_column_width=True)
    
    # Show interactive network with Plotly if 3D is enabled
    if enable_3d:
        # Create 3D network visualization with Plotly
        edge_x = []
        edge_y = []
        edge_z = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            z0 = node_type_to_z(G.nodes[edge[0]]['type'])
            z1 = node_type_to_z(G.nodes[edge[1]]['type'])
            
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_z.extend([z0, z1, None])
        
        edge_trace = go.Scatter3d(
            x=edge_x, y=edge_y, z=edge_z,
            line=dict(width=1, color='#888'),
            mode='lines',
            hoverinfo='none'
        )
        
        # Create node traces by type
        node_x_by_type = {'topic': [], 'query': [], 'fact': []}
        node_y_by_type = {'topic': [], 'query': [], 'fact': []}
        node_z_by_type = {'topic': [], 'query': [], 'fact': []}
        node_text_by_type = {'topic': [], 'query': [], 'fact': []}
        
        for node in G.nodes(data=True):
            x, y = pos[node[0]]
            node_type = node[1].get('type', 'unknown')
            z = node_type_to_z(node_type)
            
            if node_type in node_x_by_type:
                node_x_by_type[node_type].append(x)
                node_y_by_type[node_type].append(y)
                node_z_by_type[node_type].append(z)
                node_text_by_type[node_type].append(node[1]['label'])
        
        # Create a trace for each node type
        node_traces = []
        node_colors = {'topic': 'red', 'query': 'blue', 'fact': 'green'}
        
        for node_type in ['topic', 'query', 'fact']:
            if node_x_by_type[node_type]:  # Only create traces for types with nodes
                node_traces.append(go.Scatter3d(
                    x=node_x_by_type[node_type],
                    y=node_y_by_type[node_type],
                    z=node_z_by_type[node_type],
                    mode='markers',
                    marker=dict(
                        size=10,
                        color=node_colors[node_type],
                        opacity=0.8
                    ),
                    text=node_text_by_type[node_type],
                    hoverinfo='text',
                    name=node_type.capitalize()
                ))
        
        # Create the 3D network graph
        fig = go.Figure(data=[edge_trace] + node_traces)
        
        # Update layout
        fig.update_layout(
            title="3D Research Network",
            scene=dict(
                xaxis=dict(showticklabels=False, title=''),
                yaxis=dict(showticklabels=False, title=''),
                zaxis=dict(showticklabels=False, title=''),
            ),
            margin=dict(b=20,l=5,r=5,t=40),
            showlegend=True
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Show textual representation of the research path
    st.markdown("#### Research Path")
    if "query" in st.session_state.research_plan:
        main_topic = st.session_state.research_plan["query"]
        st.markdown(f"**Main Research Topic**: {main_topic}")
        
        for i, query_data in enumerate(st.session_state.research_queries):
            query = query_data["query"]
            st.markdown(f"**Search Query {i+1}**: {query}")
            
            if query in query_facts:
                st.markdown("*Facts discovered:*")
                for fact in query_facts[query]:
                    st.markdown(f"- {fact.get('fact', 'No fact available')} (Source: [{fact.get('source', 'Unknown')}]({fact.get('source', '#')}))")

# New visualization: Knowledge Graph
def show_knowledge_graph():
    """Show knowledge graph visualization of facts and their relationships."""
    if not st.session_state.research_facts:
        st.info("No facts have been collected yet.")
        return
    
    st.markdown("#### Knowledge Graph")
    st.markdown("This visualization shows connections between different facts and categories.")
    
    # Create a network of facts connected by categories
    G = nx.Graph()
    
    # Add category nodes first
    categories = set()
    for fact in st.session_state.research_facts:
        categories.add(fact.get('category', 'General'))
    
    for category in categories:
        G.add_node(category, type='category')
    
    # Add fact nodes with connections to categories
    for i, fact in enumerate(st.session_state.research_facts):
        fact_id = f"fact_{i}"
        fact_text = fact.get('fact', 'No fact')[:50]
        G.add_node(fact_id, label=fact_text, type='fact')
        
        # Connect fact to its category
        category = fact.get('category', 'General')
        G.add_edge(fact_id, category)
    
    # Draw the graph
    plt.figure(figsize=(12, 10))
    
    # Set node colors
    node_colors = []
    for node in G.nodes(data=True):
        if node[1].get('type', '') == 'category':
            node_colors.append('red')
        else:
            node_colors.append('lightblue')
    
    # Set node sizes
    node_sizes = []
    for node in G.nodes(data=True):
        if node[1].get('type', '') == 'category':
            node_sizes.append(1000)
        else:
            node_sizes.append(300)
    
    # Use spring layout with more space
    pos = nx.spring_layout(G, k=0.6, seed=42)
    
    # Draw the network
    nx.draw(
        G, 
        pos, 
        with_labels=True,
        labels={n: n if G.nodes[n].get('type', '') == 'category' else G.nodes[n].get('label', '') for n in G.nodes()},
        node_color=node_colors,
        node_size=node_sizes,
        font_size=8,
        edge_color="gray"
    )
    
    # Save to buffer
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Show image
    st.image(buf, use_column_width=True)

# New visualization: Topic Word Cloud
def show_topic_word_cloud():
    """Show word cloud of main topics and facts."""
    if not st.session_state.research_facts:
        st.info("No facts have been collected yet.")
        return
    
    st.markdown("#### Topic Word Cloud")
    st.markdown("This visualization shows the most prominent words found in the research facts.")
    
    # Combine all fact text for word cloud
    all_text = " ".join([fact.get('fact', '') for fact in st.session_state.research_facts])
    
    # Generate word cloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        colormap='viridis',
        max_words=100,
        stopwords=None,
        contour_width=1,
        contour_color='steelblue'
    ).generate(all_text)
    
    # Display the generated image
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    
    # Save to buffer
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    
    # Show image
    st.image(buf, use_column_width=True)
    
    # Show top words
    word_freq = wordcloud.process_text(all_text)
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:20]
    
    st.markdown("#### Top Words in Research")
    
    # Create bar chart of top words
    top_words_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    fig = px.bar(
        top_words_df,
        x='Word',
        y='Frequency',
        color='Frequency',
        color_continuous_scale='Viridis',
        title="Top 20 Words by Frequency"
    )
    st.plotly_chart(fig, use_container_width=True)

def node_type_to_z(node_type):
    """Map node type to z coordinate for 3D visualization."""
    if node_type == 'topic':
        return 2.0
    elif node_type == 'query':
        return 1.0
    else:  # fact
        return 0.0

def show_chat_tab(research_agent):
    """Display the chat tab content."""
    st.markdown("### Chat with Your Documents")
    
    if not st.session_state.uploaded_docs:
        st.info("Please upload documents in the sidebar to chat with them.")
    else:
        st.markdown("Ask questions about your uploaded documents:")
        
        # Chat input
        user_question = st.text_input("Your question:", key="chat_input")
        
        if st.button("Ask", key="ask_button"):
            if user_question:
                # Add user question to chat history
                st.session_state.chat_history.append({"role": "user", "content": user_question})
                
                # Show thinking indicator
                with st.spinner("Thinking..."):
                    # Generate response based on uploaded documents
                    answer = generate_document_response(user_question, st.session_state.uploaded_docs, research_agent)
                
                # Add assistant response to chat history
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        # Display chat history
        st.subheader("Conversation")
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**Assistant:** {message['content']}")
        
        # Clear chat button
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()

def show_about_tab():
    """Display the about tab content."""
    st.markdown("""
    ## About This Research Assistant
    
    This AI-powered research assistant helps you generate comprehensive reports on any topic. It combines:
    
    1. **Triage Agent**: Plans and structures the research approach
    2. **Research Agent**: Gathers and fact-checks information
    3. **Editor Agent**: Compiles findings into a well-structured report
    
    ### Features:
    - Multiple research personas to match your needs
    - Document upload and analysis
    - Chat interface for document Q&A
    - Multiple export formats
    
    ### Limitations:
    - Research is based on AI capabilities and may require verification
    - Document processing has size limitations
    - Citations should be verified for accuracy
    
    ### Feedback
    We're constantly improving! Let us know if you have suggestions.
    """)

def extract_document_text(uploaded_file):
    """Extract text from uploaded documents."""
    file_type = uploaded_file.name.split('.')[-1].lower()
    
    try:
        if file_type == 'pdf':
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        
        elif file_type == 'docx':
            text = docx2txt.process(uploaded_file)
            return text
        
        elif file_type == 'txt':
            text = uploaded_file.read().decode('utf-8')
            return text
        
        else:
            return None
    except Exception as e:
        st.error(f"Error processing file: {e}")
        return None

def process_research(
    research_topic, 
    triage_agent, 
    research_agent, 
    editor_agent, 
    uploaded_docs,
    depth="Standard",
    include_visuals=True,
    include_counter_points=True
):
    """Process research request and generate a report with enhanced tracking of resources."""
    
    # Update UI with progress
    progress_container = st.empty()
    status_text = st.empty()
    
    with progress_container.container():
        st.subheader("Research Progresss")
        progress_bar = st.progress(0)
    
    # Step 1: Planning research (15%)
    status_text.text("Planning research approach...")
    
    # Incorporate uploaded documents into research context
    context = ""
    if uploaded_docs:
        status_text.text("Analyzing uploaded documents...")
        # Combine document texts (limit length for API constraints)
        for doc_name, doc_content in uploaded_docs.items():
            context += f"\n--- Document: {doc_name} ---\n{doc_content[:5000]}\n"
    
    # Prepare research parameters based on depth
    max_tokens_map = {
        "Basic": 2000,
        "Standard": 3000,
        "Comprehensive": 4000
    }
    max_tokens = max_tokens_map.get(depth, 3000)
    
    # Plan research with triage agent
    research_plan = triage_agent.plan_research(research_topic)
    
    # Save research plan to session state
    st.session_state.research_plan = research_plan
    
    progress_bar.progress(15)
    
    # Step 2: Gathering information (60%)
    status_text.text("Gathering information...")
    search_queries = []
    
    # Get search queries from the research plan
    if "search_queries" in research_plan:
        search_queries = research_plan["search_queries"]
    
    # Save search queries with timestamp
    st.session_state.research_queries = []
    for query in search_queries:
        st.session_state.research_queries.append({
            "query": query,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "topic": research_topic
        })
    
    # Track progress for each query
    query_count = len(search_queries)
    if query_count > 0:
        progress_step = 50 / query_count  # 60% total for this phase - 10% for context analysis
    else:
        progress_step = 50
    
    # Incorporate document content if available
    if context:
        research_agent.add_context(context)
        status_text.text("Analyzing document context...")
        progress_bar.progress(20)
    
    # Track search progress
    current_progress = 20
    
    # Process and display each search query
    for i, query in enumerate(search_queries):
        query_container = st.empty()
        with query_container.container():
            st.markdown(f"**Searching**: {query}")
        
        # Update progress
        current_progress += progress_step/2
        progress_bar.progress(min(int(current_progress), 70))
        status_text.text(f"Gathering information for query: {query}")
        
        # In a real implementation, we'd search for each query separately
        # For now, we'll just use the gather_information method
        query_container.empty()
    
    # Get information from research agent
    facts = research_agent.gather_information(research_topic)
    
    # Save facts with search query info and timestamp
    enriched_facts = []
    for fact in facts:
        # Add timestamp and corresponding search query if possible
        enriched_fact = fact.copy()
        enriched_fact["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Try to match this fact with a query
        for query in search_queries:
            if query.lower() in fact.get("fact", "").lower():
                enriched_fact["query"] = query
                break
        else:
            # If no specific query matched, use the main topic
            enriched_fact["query"] = research_topic
        
        enriched_facts.append(enriched_fact)
    
    # Save to session state
    st.session_state.research_facts = enriched_facts
    
    # Extract and save all unique sources
    sources = set()
    for fact in enriched_facts:
        source = fact.get("source", "Unknown")
        if source != "Unknown":
            sources.add(source)
    
    st.session_state.research_sources = sources
    
    # Calculate facts by category
    categories = {}
    for fact in enriched_facts:
        category = fact.get("category", "General")
        if category not in categories:
            categories[category] = []
        categories[category].append(fact)
    
    st.session_state.research_categories = categories
    
    # Update progress
    progress_bar.progress(75)
    status_text.text("Compiling final report...")
    
    # Step 3: Compiling report (25%)
    # Compile report
    editor_agent.compile_report(enriched_facts)
    
    # Generate report with appropriate style
    if st.session_state.current_persona == "default":
        report = editor_agent.generate_report(
            research_topic,
            include_visuals=include_visuals,
            include_counter_points=include_counter_points,
            max_tokens=max_tokens
        )
    else:
        report = editor_agent.generate_report(
            research_topic, 
            include_visuals=include_visuals,
            include_counter_points=include_counter_points,
            max_tokens=max_tokens
        )
    
    # Complete progress
    for i in range(75, 101):
        progress_bar.progress(i)
        time.sleep(0.01)
    
    # Save report to session state
    st.session_state.generated_report = report
    
    # Clear progress indicators
    status_text.empty()
    progress_container.empty()
    
    # Show success message
    st.success("Research completed successfully!")

def generate_document_response(question, documents, research_agent):
    """Generate a response based on the uploaded documents."""
    # Combine document content (with truncation if needed)
    combined_text = ""
    for doc_name, content in documents.items():
        # Add document name as context
        combined_text += f"\n--- From document: {doc_name} ---\n"
        # Add truncated content to avoid token limits
        combined_text += content[:10000] + ("\n..." if len(content) > 10000 else "")
    
    # Use research agent to answer question based on documents
    try:
        answer = research_agent.query_documents(question, combined_text)
        return answer
    except Exception as e:
        print(f"Error generating document response: {e}")
        return f"I encountered an error while processing your question: {str(e)}"

def convert_markdown_to_pdf(markdown_text, title):
    """Convert markdown text to a downloadable PDF."""
    # Create a byte buffer
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Create content
    content = []
    
    # Add title
    title_style = styles['Title']
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 12))
    
    # Convert markdown to HTML and then to PDF content
    # This is a simplified approach - proper markdown to PDF conversion would require more processing
    lines = markdown_text.split('\n')
    for line in lines:
        if line.startswith('# '):
            # Heading 1
            content.append(Paragraph(line[2:], styles['Heading1']))
            content.append(Spacer(1, 12))
        elif line.startswith('## '):
            # Heading 2
            content.append(Paragraph(line[3:], styles['Heading2']))
            content.append(Spacer(1, 6))
        elif line.startswith('### '):
            # Heading 3
            content.append(Paragraph(line[4:], styles['Heading3']))
            content.append(Spacer(1, 6))
        elif line.startswith('- '):
            # Bullet point
            content.append(Paragraph('• ' + line[2:], styles['Normal']))
            content.append(Spacer(1, 3))
        elif line.strip() == '':
            # Empty line
            content.append(Spacer(1, 6))
        else:
            # Normal text
            content.append(Paragraph(line, styles['Normal']))
            content.append(Spacer(1, 3))
    
    # Build the PDF
    doc.build(content)
    
    # Get the PDF data
    buffer.seek(0)
    return buffer.getvalue()

# Add these methods to the ResearchAgent class if they don't exist
def add_agent_methods():
    from src.agents.research_agent import ResearchAgent
    
    # Only add methods if they don't exist
    if not hasattr(ResearchAgent, "add_context"):
        def add_context(self, context):
            """Add document context to the research agent."""
            self.context = context
            print(f"Added context: {len(context)} characters")
        
        ResearchAgent.add_context = add_context
    
    if not hasattr(ResearchAgent, "query_documents"):
        def query_documents(self, question, document_text):
            """Query the uploaded documents with a specific question."""
            try:
                prompt = f"""
                Based only on the following documents, answer this question: "{question}"
                
                DOCUMENTS:
                {document_text}
                
                If the answer cannot be found in the documents, say "I don't have enough information to answer that question based on the provided documents."
                
                Provide specific references to where in the documents you found the information.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based solely on the provided documents."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                print(f"Error querying documents: {e}")
                return f"An error occurred while processing your question: {str(e)}"
        
        ResearchAgent.query_documents = query_documents

# Initialize the additional methods when the module is loaded
add_agent_methods()

if __name__ == "__main__":
    triage_agent = TriageAgent()
    research_agent = ResearchAgent()
    editor_agent = EditorAgent()
    run_app(triage_agent, research_agent, editor_agent)