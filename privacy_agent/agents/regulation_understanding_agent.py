"""
RegulationUnderstandingAgent: Explains privacy principles and regulations using an LLM.
"""
import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini

# Load environment variables
load_dotenv()

# Check for API key
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)
    print(f"DEBUG: RegulationUnderstandingAgent - Configured genai with GOOGLE_API_KEY")
else:
    print("DEBUG: RegulationUnderstandingAgent - GOOGLE_API_KEY not found in environment. GenAI calls will likely fail.")

class RegulationUnderstandingAgent(Agent):
    """
    An agent that explains privacy principles and regulations using an LLM.
    """
    
    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = "RegulationUnderstander"):
        """
        Initialize the RegulationUnderstandingAgent.
        
        Args:
            model_name: The name of the LLM model to use.
            name: The name of the agent.
        """
        print(f"DEBUG: {name} - Initializing with model {model_name}")
        
        # Try both API key environment variables
        google_api_key = os.getenv("GOOGLE_API_KEY")
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        api_key_to_use = google_api_key or gemini_api_key
        
        llm_instance = None
        if api_key_to_use:
            key_source = "GOOGLE_API_KEY" if google_api_key else "GEMINI_API_KEY"
            print(f"DEBUG: {name} - API key found from {key_source}. Creating Gemini instance with this API key.")
            llm_instance = Gemini(model_name=model_name, api_key=api_key_to_use)
        else:
            print(f"ERROR: {name} - No API key found in environment (checked both GOOGLE_API_KEY and GEMINI_API_KEY). Creating Gemini without explicit API key. This will likely fail if global genai.configure() also failed.")
            llm_instance = Gemini(model_name=model_name)
        
        super().__init__(
            model=llm_instance,
            name=name,
            description="Explains privacy principles and regulations using an LLM.",
            instruction="""You are an expert in privacy regulations and data protection. Your task is to clearly and concisely explain the given privacy principle or regulation. Focus on its core meaning, its importance, and provide a simple example if possible. The user will provide the name of the principle or regulation to be explained.""",
        )
        print(f"DEBUG: {name} - Initialization complete")

    def invoke(self, input_request: str, context=None):
        """
        Explain a privacy principle or regulation.
        
        Args:
            input_request: The user's request, typically asking for an explanation of a privacy principle.
            context: The invocation context, which may contain additional information.
            
        Returns:
            A string explanation of the privacy principle or regulation.
        """
        print(f"DEBUG: {self.name} - invoke() called with input: '{input_request}'")
        
        # Extract the regulation name from context if available
        regulation_name = None
        if context and hasattr(context, 'state') and 'regulation_name' in context.state:
            regulation_name = context.state['regulation_name']
            print(f"DEBUG: {self.name} - Found regulation_name in context: '{regulation_name}'")
        
        # If regulation_name is not in context, try to extract it from the input_request
        if not regulation_name:
            # This is a simple heuristic; in a real agent, you might use more sophisticated NLP
            if "explain" in input_request.lower() and "principle" in input_request.lower():
                # Try to extract the principle name from the request
                parts = input_request.split("principle")
                if len(parts) > 1:
                    potential_name = parts[1].strip()
                    if potential_name.startswith("of "):
                        potential_name = potential_name[3:].strip()
                    regulation_name = potential_name
                    print(f"DEBUG: {self.name} - Extracted regulation_name from input: '{regulation_name}'")
        
        # If we still don't have a regulation name, use the whole input as the query
        query = regulation_name if regulation_name else input_request
        print(f"DEBUG: {self.name} - Using query: '{query}'")
        
        try:
            # Ensure GOOGLE_API_KEY is set, otherwise GenerativeModel() will fail
            if not os.getenv("GOOGLE_API_KEY"):
                error_msg = "GOOGLE_API_KEY environment variable not set. LLM call will fail."
                print(f"ERROR: {self.name} - {error_msg}")
                return f"Error: {error_msg}"
            
            # Use the model to generate a response
            response = self.model.generate_content(
                f"Explain the privacy principle or regulation known as '{query}'. Focus on its core meaning, importance, and provide a simple example."
            )
            
            if response and hasattr(response, 'text'):
                explanation = response.text.strip()
                print(f"DEBUG: {self.name} - Generated explanation (first 100 chars): '{explanation[:100]}...'")
                return explanation
            else:
                error_msg = "Failed to generate explanation: empty or invalid response from LLM."
                print(f"ERROR: {self.name} - {error_msg}")
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Exception during LLM call: {str(e)}"
            print(f"ERROR: {self.name} - {error_msg}")
            return f"Error: {error_msg}"


# For testing directly
if __name__ == "__main__":
    # IMPORTANT: This requires the GOOGLE_API_KEY to be set in your environment
    print("\n=== Testing RegulationUnderstandingAgent ===")
    
    # Create an instance of the agent
    agent = RegulationUnderstandingAgent()
    
    # Test with a sample regulation
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nWARNING: GOOGLE_API_KEY environment variable not found.")
        print("LLM calls will likely fail. Set this in your environment or .env file.")
    
    # Test the agent
    test_regulations = ["Data Minimization", "Purpose Limitation", "Right to be Forgotten"]
    
    for reg in test_regulations:
        print(f"\nTesting with regulation: {reg}")
        result = agent.invoke(f"Explain the principle of {reg}")
        print(f"\nResult:\n{result}")
        
    print("\n=== Test Complete ===")
