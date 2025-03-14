# Research Agents Application

This project is a multi-agent research application built with OpenAI's Agents SDK and Streamlit. It enables users to conduct comprehensive research on any topic by leveraging multiple specialized AI agents.

## Features

- **Multi-Agent Architecture**:
  - **Triage Agent**: Plans the research approach and coordinates the workflow.
  - **Research Agent**: Searches the web and gathers relevant information.
  - **Editor Agent**: Compiles collected facts into a comprehensive report.

- **Automatic Fact Collection**: Captures important facts from research with source attribution.

- **Structured Report Generation**: Creates well-organized reports with titles, outlines, and source citations.

- **Interactive UI**: Built with Streamlit for easy research topic input and results viewing.

- **Tracing and Monitoring**: Integrated tracing for the entire research workflow.

## Project Structure

```
research-agents-app
├── src
│   ├── agents
│   │   ├── __init__.py
│   │   ├── triage_agent.py
│   │   ├── research_agent.py
│   │   └── editor_agent.py
│   ├── ui
│   │   ├── __init__.py
│   │   └── app.py
│   ├── utils
│   │   ├── __init__.py
│   │   ├── tracing.py
│   │   └── web_search.py
│   └── models
│       ├── __init__.py
│       └── research_report.py
├── requirements.txt
├── main.py
├── .env.example
└── README.md
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/research-agents-app.git
   cd research-agents-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up your environment variables by copying `.env.example` to `.env` and filling in the necessary values.

## Usage

To start the application, run:
```
python main.py
```

This will launch the Streamlit app in your web browser, allowing you to input research topics and view the generated reports.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.