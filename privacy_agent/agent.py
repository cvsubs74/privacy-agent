# /Users/cvsubramanian/CascadeProjects/privacyagent/privacy_agent/agent.py
"""Defines the root agent for the Privacy Assessment application, including the main agent class."""

import sys
from google.adk.agents import SequentialAgent
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the genai library globally
google_api_key = os.getenv("GOOGLE_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
api_key_to_use = google_api_key or gemini_api_key

if api_key_to_use:
    print(f"DEBUG: privacy_agent/agent.py - Configuring genai with API key")
    genai.configure(api_key=api_key_to_use)
else:
    print("ERROR: No API key found in environment variables (checked both GOOGLE_API_KEY and GEMINI_API_KEY).")

print("DEBUG: Executing privacy_agent/agent.py START")

# Import the sub-agents - these paths are relative to this file's location
# (privacy_agent/agent.py), so we need to go into the 'agents' subdirectory.
try:
    from .agents.policy_fetcher_agent import PolicyFetcherAgent
    from .agents.regulation_understanding_agent import RegulationUnderstandingAgent
    from .agents.policy_analyzer_agent import PolicyAnalyzerAgent
    from .agents.compliance_assessor_agent import ComplianceAssessorAgent
    from .agents.report_generator_agent import ReportGeneratorAgent
    print("DEBUG: privacy_agent/agent.py - Successfully imported all sub-agent classes.")
except ImportError as e:
    print(f"DEBUG: privacy_agent/agent.py - ImportError while importing sub-agents: {e}")
    # Define placeholders if import fails, so class definition doesn't break immediately
    PolicyFetcherAgent = RegulationUnderstandingAgent = PolicyAnalyzerAgent = ComplianceAssessorAgent = ReportGeneratorAgent = None

class PrivacyAssessmentAgent(SequentialAgent):
    """
    A sequential agent that orchestrates various sub-agents to perform a
    privacy assessment based on a company's URL and a specific regulation.
    """
    def __init__(self):
        print("DEBUG: PrivacyAssessmentAgent __init__ STARTING.")
        if None in [PolicyFetcherAgent, RegulationUnderstandingAgent, PolicyAnalyzerAgent, ComplianceAssessorAgent, ReportGeneratorAgent]:
            print("DEBUG: PrivacyAssessmentAgent __init__ - One or more sub-agent classes are None due to import failure.")
            # Handle error appropriately, e.g., raise an exception or set a faulty state
            raise ImportError("Failed to import one or more sub-agent classes for PrivacyAssessmentAgent.")

        # Instantiate sub-agents
        policy_fetcher = PolicyFetcherAgent(name="PolicyFetcher")
        regulation_understander = RegulationUnderstandingAgent(name="RegulationUnderstander")
        policy_analyzer = PolicyAnalyzerAgent(name="PolicyAnalyzer")
        compliance_assessor = ComplianceAssessorAgent(name="ComplianceAssessor")
        report_generator = ReportGeneratorAgent(name="ReportGenerator")
        print("DEBUG: PrivacyAssessmentAgent __init__ - Sub-agents instantiated.")

        sub_agents = [
            policy_fetcher,
            regulation_understander,
            policy_analyzer,
            compliance_assessor,
            report_generator,
        ]

        super().__init__(
            name="PrivacyAssessmentOrchestrator", # You can keep this or use 'PrivacyAssessmentAgent'
            description="Orchestrates the privacy assessment process by fetching policies, understanding regulations, analyzing policies, assessing compliance, and generating a report.",
            sub_agents=sub_agents,
        )
        print("DEBUG: PrivacyAssessmentAgent __init__ FINISHED (super called).")

# --- Instantiation and root_agent assignment ---
root_agent = None # Initialize
try:
    # Instantiate the main agent
    _pa_instance = PrivacyAssessmentAgent()
    print(f"DEBUG: privacy_agent/agent.py - Successfully instantiated PrivacyAssessmentAgent: {_pa_instance}")

    # Expose the instance as root_agent, as expected by ADK
    root_agent = _pa_instance
    print(f"DEBUG: privacy_agent/agent.py - root_agent is now assigned: {root_agent}")

except ImportError as e: # Catch import errors from sub-agent loading too
    print(f"DEBUG: privacy_agent/agent.py - ImportError during PrivacyAssessmentAgent setup: {e}")
    print(f"DEBUG: Python Path: {sys.path}")
    root_agent = f"ERROR_IMPORT_IN_AGENT_PY: {e}"
except Exception as e:
    print(f"DEBUG: privacy_agent/agent.py - EXCEPTION during PrivacyAssessmentAgent instantiation or assignment:")
    import traceback
    print(traceback.format_exc())
    root_agent = f"ERROR_INSTANTIATION_IN_AGENT_PY: {e}"

if root_agent is None or (isinstance(root_agent, str) and "ERROR" in root_agent):
    print(f"DEBUG: privacy_agent/agent.py - CRITICAL: root_agent was NOT DEFINED properly or is an error. Value: {root_agent}")
    if root_agent is None: # Ensure it's at least an error string if it somehow ended up as None
        root_agent = "ERROR_AGENT_PY_ROOT_AGENT_WAS_NONE"


print("DEBUG: Executing privacy_agent/agent.py FINISH")
