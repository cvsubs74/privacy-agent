# /Users/cvsubramanian/CascadeProjects/privacyagent/privacy_agent/__init__.py
print("DEBUG: Executing privacy_agent/__init__.py START (attempting to import .agent module)")

try:
    from . import agent  # Imports privacy_agent/agent.py
    print("DEBUG: privacy_agent/__init__.py - Successfully imported .agent module.")
    
    # For verification, check if root_agent is now accessible
    if hasattr(agent, 'root_agent'):
        print(f"DEBUG: privacy_agent/__init__.py - .agent.root_agent exists: {agent.root_agent}")
    else:
        print("DEBUG: privacy_agent/__init__.py - .agent.root_agent NOT FOUND.")
        # This would be an issue, means agent.py didn't define it or this __init__.py can't see it

except ImportError as e:
    print(f"DEBUG: privacy_agent/__init__.py - ImportError when importing .agent: {e}")
    # To make ADK happy even on failure, define 'agent' but as an error indicator
    # This helps distinguish this error from agent.py errors
    class AgentModulePlaceholder: pass
    agent = AgentModulePlaceholder() # Create a dummy 'agent' module attribute
    setattr(agent, 'root_agent', f"ERROR_TOP_INIT_IMPORT_FAILED: {e}")

except Exception as e:
    print(f"DEBUG: privacy_agent/__init__.py - UNEXPECTED EXCEPTION when importing .agent: {e}")
    import traceback
    print(traceback.format_exc())
    class AgentModulePlaceholder: pass
    agent = AgentModulePlaceholder()
    setattr(agent, 'root_agent', f"ERROR_TOP_INIT_UNEXPECTED: {e}")


print("DEBUG: Executing privacy_agent/__init__.py FINISH")
