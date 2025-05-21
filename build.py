"""
This module imports and exposes the root agent for the ADK framework.
"""
import sys
import os

# Add the project root to the Python path if it's not already there
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the agent from privacy_agent.agent
try:
    from privacy_agent.agent import root_agent as agent
    print(f"DEBUG: build.py - Successfully imported root_agent from privacy_agent.agent: {agent}")
except ImportError as e:
    print(f"DEBUG: build.py - ImportError while importing root_agent: {e}")
    # Create a fallback agent
    from google.adk.agents import Agent
    agent = Agent(name="FallbackAgent", description=f"ERROR: Failed to import root_agent: {e}")
    print(f"DEBUG: build.py - Created fallback Agent: {agent}")
except Exception as e:
    print(f"DEBUG: build.py - Exception while importing root_agent: {e}")
    # Create a fallback agent
    from google.adk.agents import Agent
    agent = Agent(name="FallbackAgent", description=f"ERROR: Unexpected error: {e}")
    print(f"DEBUG: build.py - Created fallback Agent: {agent}")

# Verify that agent is properly defined
if agent is None:
    print("DEBUG: build.py - agent is None, creating fallback agent")
    from google.adk.agents import Agent
    agent = Agent(name="FallbackAgent", description="ERROR: agent was None")
    print(f"DEBUG: build.py - Created fallback Agent: {agent}")
elif isinstance(agent, str):
    print(f"DEBUG: build.py - agent is a string: {agent}, creating fallback agent")
    from google.adk.agents import Agent
    agent = Agent(name="FallbackAgent", description=f"ERROR: agent was a string: {agent}")
    print(f"DEBUG: build.py - Created fallback Agent: {agent}")
else:
    print(f"DEBUG: build.py - agent is properly defined: {agent}")
