"""
PolicyAnalyzerAgent: Analyzes privacy policy text against a specific privacy principle.
"""
import os
import typing
from typing import ClassVar
from dotenv import load_dotenv

load_dotenv() # Load .env from the project root or current working directory

from google.adk.agents import Agent
import google.generativeai as genai
from google.adk.models.google_llm import Gemini

class PolicyAnalyzerAgent(Agent):
    """
    An agent that analyzes a given privacy policy text to determine how it addresses
    a specific privacy principle or regulation, extracting relevant excerpts.
    """

    DEFAULT_INSTRUCTION: ClassVar[str] = (
        "You are an AI assistant specialized in privacy policy analysis. "
        "Your task is to analyze the provided privacy policy text to determine if and how it addresses "
        "the given privacy principle or regulation. Identify specific clauses or statements in the policy "
        "that are relevant to the principle. Provide a concise analysis and quote the most relevant "
        "excerpts from the policy text. If the policy does not address the principle, state that clearly. "
        "Structure your output as follows:\n"
        "Analysis: [Your analysis of how the policy addresses the principle]\n"
        "Relevant Excerpts:\n"
        "- [Quote 1]\n"
        "- [Quote 2 (if applicable)]\n"
        "If not addressed: Policy does not appear to address this principle."
    )

    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = "PolicyAnalyzer"):
        """
        Initialize the PolicyAnalyzerAgent.
        
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
            description="Analyzes privacy policy text against a specific privacy principle.",
            instruction=self.DEFAULT_INSTRUCTION,
        )
        print(f"DEBUG: {name} - Initialization complete")

    def invoke(self, input_request: str, context=None):
        """
        Analyze a privacy policy text against a specific privacy principle.
        
        Args:
            input_request: The user's request, typically asking for analysis of a policy.
            context: The invocation context, which should contain the policy_text and principle_name.
            
        Returns:
            A string analysis of how the policy addresses the principle.
        """
        print(f"DEBUG: {self.name} - invoke() called with input: '{input_request}'")
        
        # Extract policy_text and principle_name from context
        policy_text = None
        principle_name = None
        
        if context and hasattr(context, 'state'):
            policy_text = context.state.get('policy_text')
            principle_name = context.state.get('principle_name')
            
        if not policy_text or not principle_name:
            error_msg = "Missing required inputs: policy_text and principle_name must be provided in context."
            print(f"ERROR: {self.name} - {error_msg}")
            return f"Error: {error_msg}"
            
        print(f"DEBUG: {self.name} - Analyzing policy for principle: '{principle_name}'")
        print(f"DEBUG: {self.name} - Policy text length: {len(policy_text)} characters")
        
        try:
            # Ensure GOOGLE_API_KEY is set, otherwise GenerativeModel() will fail
            if not os.getenv("GOOGLE_API_KEY"):
                 return {"error": "GOOGLE_API_KEY not set."}
            
            # Construct the prompt
            prompt = (
                f"Analyze the following privacy policy text to determine how it addresses the privacy principle of '{principle_name}'.\n\n"
                f"PRIVACY POLICY TEXT:\n{policy_text}\n\n"
                f"Provide your analysis of how the policy addresses the principle of '{principle_name}'. "
                f"Include relevant excerpts from the policy text. If the policy does not address this principle, state that clearly."
            )
            
            # Use the model to generate a response
            response = self.model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                analysis = response.text.strip()
                print(f"DEBUG: {self.name} - Generated analysis (first 100 chars): '{analysis[:100]}...'")
                return analysis
            else:
                error_msg = "Failed to generate analysis: empty or invalid response from LLM."
                print(f"ERROR: {self.name} - {error_msg}")
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Exception during LLM call: {str(e)}"
            print(f"ERROR: {self.name} - {error_msg}")
            return f"Error: {error_msg}"


# For testing directly
if __name__ == "__main__":
    print("--- Testing PolicyAnalyzerAgent --- (Requires GOOGLE_API_KEY)")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nWARNING: GOOGLE_API_KEY environment variable not found.")
        print("LLM calls will fail. Set this in your environment or .env file.")
        exit(1)
    
    # Create an instance of the agent
    agent = PolicyAnalyzerAgent()
    
    # Sample privacy policy text
    sample_policy = """
    Privacy Policy
    
    1. Data Collection
    We collect the following information:
    - Email address when you sign up
    - Usage data through cookies
    - IP address for security purposes
    
    2. Data Usage
    We use your data to:
    - Provide our services
    - Improve user experience
    - Send newsletters (if you opt in)
    
    3. Data Sharing
    We do not sell your personal information to third parties.
    We may share anonymized data with partners for analytics.
    
    4. Data Retention
    We keep your data for as long as your account is active.
    You can request deletion of your data at any time.
    
    5. Your Rights
    You have the right to:
    - Access your data
    - Request correction of inaccurate data
    - Request deletion of your data
    - Opt out of marketing communications
    """
    
    # Test with different principles
    principles = ["Data Minimization", "Purpose Limitation", "Right to Access"]
    
    for principle in principles:
        print(f"\n--- Analyzing for: {principle} ---")
        
        # Create a mock context with the required inputs
        class MockContext:
            def __init__(self):
                self.state = {
                    'policy_text': sample_policy,
                    'principle_name': principle
                }
        
        # Invoke the agent
        result = agent.invoke("Analyze this privacy policy", MockContext())
        print(f"\nResult:\n{result}")
    
    print("\n--- Test Complete ---")
