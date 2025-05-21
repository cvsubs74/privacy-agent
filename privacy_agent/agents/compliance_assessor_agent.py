"""
ComplianceAssessorAgent: Assesses privacy policy compliance with a specific principle.
"""
import sys
import os
import typing
from typing import ClassVar

from dotenv import load_dotenv
load_dotenv() # Load .env from the project root or current working directory

from google.adk.agents import Agent
import google.generativeai as genai
from google.adk.models.google_llm import Gemini

class ComplianceAssessorAgent(Agent):
    """
    An agent that assesses how well a privacy policy complies with a given
    privacy principle, based on an explanation of the principle and an analysis
    of the policy.
    """

    DEFAULT_INSTRUCTION: ClassVar[str] = (
        "You are an AI assistant specialized in privacy compliance assessment. "
        "Your task is to assess how well a privacy policy complies with a specific privacy principle. "
        "You will be given an explanation of the privacy principle and an analysis of the privacy policy "
        "(which includes whether the principle is addressed and relevant excerpts from the policy)."
        "Based on this information, provide a compliance assessment. The assessment should include:\n"
        "1. Compliance Level: (e.g., High, Medium, Low, Not Addressed)\n"
        "2. Justification: (Explain your reasoning for the compliance level, referencing the provided "
        "principle explanation and policy analysis. Highlight strengths and weaknesses.)\n"
        "3. Suggestions for Improvement: (If applicable, provide actionable suggestions for how the "
        "policy could better align with the principle.)\n"
        "Structure your output clearly under these three headings."
    )

    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = "ComplianceAssessor"):
        """
        Initialize the ComplianceAssessorAgent.
        
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
            description="Assesses privacy policy compliance with a specific principle.",
            instruction=self.DEFAULT_INSTRUCTION,
        )
        print(f"DEBUG: {name} - Initialization complete")

    def invoke(self, input_request: str, context=None):
        """
        Assess compliance of a privacy policy with a specific principle.
        
        Args:
            input_request: The user's request, typically asking for a compliance assessment.
            context: The invocation context, which should contain principle_name, policy_excerpt, and analysis.
            
        Returns:
            A string assessment of compliance level, justification, and suggestions.
        """
        print(f"DEBUG: {self.name} - invoke() called with input: '{input_request}'")
        
        # Extract required inputs from context
        principle_name = None
        policy_excerpt = None
        analysis = None
        
        if context and hasattr(context, 'state'):
            principle_name = context.state.get('principle_name')
            policy_excerpt = context.state.get('policy_excerpt')
            analysis = context.state.get('analysis')
            
        if not principle_name or not analysis:
            error_msg = "Missing required inputs: principle_name and analysis must be provided in context."
            print(f"ERROR: {self.name} - {error_msg}")
            return f"Error: {error_msg}"
            
        print(f"DEBUG: {self.name} - Assessing compliance for principle: '{principle_name}'")
        
        try:
            # Ensure GOOGLE_API_KEY is set, otherwise GenerativeModel() will fail
            if not os.getenv("GOOGLE_API_KEY"):
                 return {"error": "GOOGLE_API_KEY not set."}
            
            # Construct the prompt
            prompt = (
                f"Assess how well a privacy policy complies with the privacy principle of '{principle_name}'.\n\n"
                f"PRINCIPLE: {principle_name}\n\n"
            )
            
            if policy_excerpt:
                prompt += f"POLICY EXCERPT:\n{policy_excerpt}\n\n"
                
            prompt += (
                f"ANALYSIS:\n{analysis}\n\n"
                f"Provide a compliance assessment with the following structure:\n"
                f"1. Compliance Level: (High, Medium, Low, or Not Addressed)\n"
                f"2. Justification: (Explain your reasoning for the compliance level)\n"
                f"3. Suggestions for Improvement: (Provide actionable suggestions if applicable)"
            )
            
            # Use the model to generate a response
            response = self.model.generate_content(prompt)
            
            if response and hasattr(response, 'text'):
                assessment = response.text.strip()
                print(f"DEBUG: {self.name} - Generated assessment (first 100 chars): '{assessment[:100]}...'")
                return assessment
            else:
                error_msg = "Failed to generate assessment: empty or invalid response from LLM."
                print(f"ERROR: {self.name} - {error_msg}")
                return f"Error: {error_msg}"
                
        except Exception as e:
            error_msg = f"Exception during LLM call: {str(e)}"
            print(f"ERROR: {self.name} - {error_msg}")
            return f"Error: {error_msg}"

    def _parse_suggestions(self, suggestions_text):
        """
        Parse suggestions from the LLM output into a list of individual suggestions.
        
        This handles various formats that the LLM might use to present suggestions.
        
        Args:
            suggestions_text: The raw text containing suggestions from the LLM.
            
        Returns:
            A list of individual suggestion strings.
        """
        if not suggestions_text:
            return []
            
        suggestions_list = []
        
        # Split by common bullet point markers
        lines = suggestions_text.split('\n')
        
        current_main_suggestion_parts = []
        base_indent = 0
        first_bullet_processed_for_current_header = False
        
        # Process the first line if it doesn't start with a bullet
        # (it might be a header or part of a suggestion)
        content_lines = lines
        if content_lines and not (content_lines[0].lstrip().startswith("* ") or 
                                content_lines[0].lstrip().startswith("- ")):
            first_line_content = content_lines[0].strip()
            # If it's not a header (like "Suggestions:"), treat it as part of the first suggestion
            if not first_line_content.lower().endswith(":"):
                if first_line_content:
                    current_main_suggestion_parts.append(first_line_content)
                content_lines = content_lines[1:] # Processed, so remove

            for raw_line in content_lines:
                line_lstripped = raw_line.lstrip()
                current_indent = len(raw_line) - len(line_lstripped)

                is_bullet = line_lstripped.startswith("* ") or line_lstripped.startswith("- ")

                if is_bullet:
                    bullet_content = line_lstripped[2:].strip()
                    if not first_bullet_processed_for_current_header or current_indent <= base_indent:
                        # This is a new top-level bullet
                        if current_main_suggestion_parts: # Save previous main suggestion
                            suggestions_list.append(" ".join(current_main_suggestion_parts).strip())
                        current_main_suggestion_parts = [bullet_content]
                        base_indent = current_indent
                        first_bullet_processed_for_current_header = True
                    else: # This is a sub-bullet (indented further than base_indent)
                        if current_main_suggestion_parts:
                            # Append to current main suggestion, maybe marking it as a sub-point
                            current_main_suggestion_parts.append(f"(sub-point: {bullet_content})")
                        else:
                            # Orphaned sub-bullet, treat as a new main bullet for robustness
                            current_main_suggestion_parts = [bullet_content]
                            base_indent = current_indent
                else:
                    # This is a continuation of the previous bullet point or a standalone paragraph
                    content = line_lstripped.strip()
                    if content and current_main_suggestion_parts:
                        current_main_suggestion_parts.append(content)
                    elif content:
                        # Standalone paragraph without a bullet, treat as a new suggestion
                        if current_main_suggestion_parts:
                            suggestions_list.append(" ".join(current_main_suggestion_parts).strip())
                        current_main_suggestion_parts = [content]
        
        # Don't forget to add the last suggestion if there is one
        if current_main_suggestion_parts:
            suggestions_list.append(" ".join(current_main_suggestion_parts).strip())
            
        # If we didn't successfully parse any bullets, fall back to treating each line as a suggestion
        if not suggestions_list and lines:
            for line in lines:
                content = line.strip()
                if content:
                    suggestions_list.append(content)
                    
        return suggestions_list


# For testing directly
if __name__ == "__main__":
    print("--- Testing ComplianceAssessorAgent --- (Requires GOOGLE_API_KEY)")
    
    if not os.getenv("GOOGLE_API_KEY"):
        print("\nWARNING: GOOGLE_API_KEY environment variable not found.")
        print("LLM calls will fail. Set this in your environment or .env file.")
        exit(1)
    
    # Create an instance of the agent
    agent = ComplianceAssessorAgent()
    
    # Sample data
    sample_principle = "Data Minimization"
    sample_excerpt = "We collect your email address, name, and phone number when you sign up. We also collect usage data through cookies."
    sample_analysis = """
    Principle: Data Minimization
    
    Analysis: The privacy policy mentions collecting specific personal data (email, name, phone) for account creation, as well as usage data through cookies. However, it does not explicitly state that they only collect what is necessary for the stated purposes, nor does it explain why each piece of data is needed.
    
    Relevant Excerpts:
    - "We collect your email address, name, and phone number when you sign up."
    - "We also collect usage data through cookies."
    """
    
    # Create a mock context with the required inputs
    class MockContext:
        def __init__(self):
            self.state = {
                'principle_name': sample_principle,
                'policy_excerpt': sample_excerpt,
                'analysis': sample_analysis
            }
    
    # Invoke the agent
    print("\n--- Assessing compliance ---")
    result = agent.invoke("Assess compliance with data minimization", MockContext())
    print(f"\nResult:\n{result}")
    
    print("\n--- Test Complete ---")
