# Privacy Assessment Agent

An AI-powered agent designed to analyze privacy policies against various privacy regulations and principles. This agent leverages Google's Gemini AI models to provide comprehensive privacy assessments for websites and applications.

## Features

- **Policy Fetching**: Automatically retrieves privacy policies from websites
- **Regulation Understanding**: Explains privacy principles and regulations in detail
- **Policy Analysis**: Analyzes privacy policies against specific principles
- **Compliance Assessment**: Evaluates compliance levels and provides justifications
- **Report Generation**: Creates comprehensive privacy assessment reports

## Architecture

The Privacy Assessment Agent is built using a modular architecture with specialized sub-agents:

1. **PolicyFetcherAgent**: Retrieves and extracts text from privacy policy URLs
2. **RegulationUnderstandingAgent**: Explains privacy principles and regulations
3. **PolicyAnalyzerAgent**: Analyzes policy text against specific principles
4. **ComplianceAssessorAgent**: Assesses compliance levels with justifications
5. **ReportGeneratorAgent**: Compiles findings into comprehensive reports

## Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:cvsubs74/privacy-agent.git
   cd privacy-agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project root
   - Add your Google API key:
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```
   - Note: For backward compatibility, `GEMINI_API_KEY` is also supported

## Running the Agent

### Using the ADK Web Interface

```bash
./.venv/bin/adk web
```

This will start a web server at http://localhost:8000 where you can interact with the agent.

### Example Prompts

- "Analyze the privacy policy for example.com and check its compliance with GDPR"
- "Explain the principle of data minimization and how it applies to privacy policies"
- "Assess the privacy policy at https://example.com/privacy for CCPA compliance"

## Development

### Running Tests

```bash
python -m pytest
```

### Project Structure

```
privacy_agent/
├── agents/                 # Individual specialized agents
│   ├── policy_fetcher_agent.py
│   ├── regulation_understanding_agent.py
│   ├── policy_analyzer_agent.py
│   ├── compliance_assessor_agent.py
│   └── report_generator_agent.py
├── utils/                  # Utility functions
│   └── web_parser.py       # Web scraping utilities
└── agent.py               # Main orchestrator agent

tests/                     # Test suite
└── agents/                # Tests for individual agents
```

## Requirements

- Python 3.9+
- Google API key with access to Gemini models
- Internet access for fetching privacy policies

## License

MIT
