#!/usr/bin/env python
"""
Simple application to run the Privacy Assessment Agent directly.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.adk.runners import Runner

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment.")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# Configure genai with the API key
genai.configure(api_key=api_key)

# Import the agent
try:
    from privacy_agent.agent import root_agent
    print(f"Successfully imported root_agent: {root_agent}")
    
    # Verify that it's a proper agent object
    if hasattr(root_agent, 'sub_agents'):
        print(f"root_agent has {len(root_agent.sub_agents)} sub-agents")
    else:
        print(f"WARNING: root_agent does not have sub_agents attribute")
        
    # Print the sub-agents
    if hasattr(root_agent, 'sub_agents'):
        print("Sub-agents:")
        for i, sub_agent in enumerate(root_agent.sub_agents):
            print(f"  {i+1}. {sub_agent.name}: {type(sub_agent)}")
except ImportError as e:
    print(f"ImportError while importing root_agent: {e}")
    exit(1)
except Exception as e:
    print(f"Exception while importing root_agent: {e}")
    exit(1)

print("\nPrivacy Assessment Agent is ready to use!")
print("You can run it with the ADK web server using: ./.venv/bin/adk web")
