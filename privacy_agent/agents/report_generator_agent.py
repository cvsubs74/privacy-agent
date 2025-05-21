"""
ReportGeneratorAgent: Compiles findings from other agents into a comprehensive report.
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv
from google.adk.agents import Agent
from privacy_agent.data_structures import AssessmentResult, PolicyAnalysisResult, ComplianceAssessmentResult

# Load environment variables
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    print("WARNING: GOOGLE_API_KEY not found in environment variables. LLM functionality may not work properly.")
else:
    genai.configure(api_key=google_api_key)
    print(f"DEBUG: ReportGeneratorAgent - Configured genai with GOOGLE_API_KEY")


REPORT_GENERATOR_PROMPT = """
You are a Privacy Assessment Report Generator. Your task is to synthesize the provided information into a 
comprehensive and well-structured privacy assessment report.

Input:
- The full text of the privacy policy being assessed.
- A list of assessment results for various privacy principles. Each assessment result includes:
    - The name of the privacy principle.
    - An explanation of the privacy principle.
    - An analysis of how the privacy policy addresses this principle (including relevant excerpts).
    - A compliance level (e.g., High, Medium, Low, Not Addressed).
    - A justification for the compliance level.
    - Suggestions for improvement related to this principle.

Output Structure:
Produce a report with the following sections:

1.  **Overall Summary:**
    *   Brief overview of the assessment.
    *   General impression of the policy's strengths and weaknesses regarding the assessed principles.

2.  **Detailed Principle Assessments:**
    For each privacy principle assessed:
    *   **Principle:** [Name of the Principle]
    *   **Principle Explanation:** [Explanation of the Principle]
    *   **Policy Analysis Summary:** [Summary of how the policy addresses the principle, include key excerpts if concise and impactful]
    *   **Compliance Level:** [Compliance Level]
    *   **Justification:** [Justification for the level]
    *   **Suggestions for Improvement:** [List of suggestions]

3.  **General Recommendations & Conclusion:**
    *   Broader recommendations that might not fit under a single principle but improve overall privacy posture.
    *   Concluding thoughts on the policy's adherence to privacy best practices based on the assessment.

Instructions:
- Be objective and base your report strictly on the provided input.
- Use clear, concise language.
- Maintain a professional tone.
- Ensure the report is well-organized and easy to read using markdown for formatting (headers, bolding, lists).
- If policy excerpts were provided in the analysis, you can choose to include very short, key excerpts in the 'Policy Analysis Summary' if they are highly illustrative. Avoid copying large chunks.
"""

class ReportGeneratorAgent(Agent):
    """Agent to generate a comprehensive privacy assessment report."""

    def __init__(self, model_name: str = "gemini-2.0-flash", name: str = "ReportGenerator"):
        # Ensure the GOOGLE_API_KEY is loaded for the ADK Agent to use internally.
        # The ADK Agent base class should handle the LLM client initialization when a model name string is provided.
        # We also need to ensure genai is configured if the ADK doesn't do it explicitly.
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print(f"WARNING: {name} - GOOGLE_API_KEY not found. LLM functionality might be affected if ADK relies on it being pre-configured.")
        else:
            # It's generally safe to call configure multiple times if needed, 
            # or the ADK might do this itself. Let's ensure it's done once.
            try:
                genai.configure(api_key=api_key)
                print(f"DEBUG: {name} - Configured genai with GOOGLE_API_KEY in __init__")
            except Exception as e_configure:
                print(f"ERROR: {name} - Error configuring genai in __init__: {e_configure}")

        super().__init__(
            model=model_name, # Pass the model name string, ADK should handle LLM init
            name=name,
            description="Generates a comprehensive privacy assessment report based on policy analysis and compliance assessments.",
            instruction=REPORT_GENERATOR_PROMPT,
        )
        print(f"DEBUG: {name} initialized with model: {model_name}")

    def invoke(
        self, 
        policy_text: str,
        assessment_results: list[AssessmentResult] # or list[dict] if not using AssessmentResult directly
    ):
        """
        Generates a comprehensive report based on policy text and assessment results.

        Args:
            policy_text: The full text of the privacy policy.
            assessment_results: A list of AssessmentResult objects (or dicts) containing 
                                assessment data for various privacy principles.

        Returns:
            A formatted report as a string, or None if there was an error.
        """
        if not assessment_results:
            print(f"Error in {self.name}: No assessment results provided.")
            return None

        if not policy_text:
            print(f"Warning in {self.name}: No policy text provided. Report will only be based on assessment results.")
            policy_text = "No policy text provided."

        # Format the assessment results for the prompt
        assessments_string_parts = []
        
        for result in assessment_results:
            # Handle both AssessmentResult objects and dicts
            if isinstance(result, dict):
                principle_name = result.get('principle_name', 'Unknown Principle')
                explanation = result.get('principle_explanation', 'No explanation provided.')
                
                analysis_obj = result.get('policy_analysis', {})
                analysis_summary = analysis_obj.get('summary', 'No analysis summary provided.') if analysis_obj else 'No analysis provided.'
                relevant_excerpts_list = analysis_obj.get('relevant_excerpts', []) if analysis_obj else []
                
                compliance_obj = result.get('compliance_assessment', {})
                compliance_level = compliance_obj.get('level', 'N/A') if compliance_obj else 'N/A'
                justification = compliance_obj.get('justification', 'N/A') if compliance_obj else 'N/A'
                suggestions_list = compliance_obj.get('suggestions', []) if compliance_obj else []
            else:
                # It's an AssessmentResult object
                principle_name = getattr(result, 'principle_name', 'Unknown Principle')
                explanation = getattr(result, 'principle_explanation', 'No explanation provided.')
                
                analysis_obj = getattr(result, 'policy_analysis', None)
                analysis_summary = getattr(analysis_obj, 'summary', 'No analysis summary provided.') if analysis_obj else 'No analysis provided.'
                relevant_excerpts_list = getattr(analysis_obj, 'relevant_excerpts', []) if analysis_obj else []
            
            # Format the excerpts
            analysis_excerpts = "\n".join([
                f"  - Excerpt: {ex.get('excerpt', 'N/A')}\n    (Location: {ex.get('location_context', 'N/A')})" 
                for ex in relevant_excerpts_list
            ])

            compliance_obj = getattr(result, 'compliance_assessment', None)
            compliance_level = getattr(compliance_obj, 'level', 'N/A') if compliance_obj else 'N/A'
            justification = getattr(compliance_obj, 'justification', 'N/A') if compliance_obj else 'N/A'
            suggestions_list = getattr(compliance_obj, 'suggestions', []) if compliance_obj else []
            suggestions = "\n".join([f"  - {s}" for s in suggestions_list])

            assessments_string_parts.append(
                f"### Assessment for Principle: {principle_name}\n"
                f"**Principle Explanation:** {explanation}\n"
                f"**Policy Analysis Summary:** {analysis_summary}\n"
                f"**Relevant Excerpts:**\n{analysis_excerpts if analysis_excerpts else '  None provided.'}\n"
                f"**Compliance Level:** {compliance_level}\n"
                f"**Justification:** {justification}\n"
                f"**Suggestions for Improvement:**\n{suggestions if suggestions else '  None provided.'}\n"
                f"---"
            )
        
        formatted_assessments = "\n\n".join(assessments_string_parts)

        input_prompt = (
            f"## Full Privacy Policy Text:\n---BEGIN POLICY TEXT---\n{policy_text}\n---END POLICY TEXT---\n\n"
            f"## Detailed Assessment Results:\n{formatted_assessments}"
        )

        print(f"Invoking {self.name} with combined input length: {len(input_prompt)}")
        # print(f"DEBUG: Report Generator Input Prompt:\n{input_prompt[:2000]}...\n") # For debugging

        try:
            active_llm_client = None
            
            # Try to use self.llm if it's a valid client
            if hasattr(self, 'llm') and isinstance(self.llm, genai.GenerativeModel):
                active_llm_client = self.llm
                print(f"Using self.llm (type: {type(self.llm)}) for LLM call in {self.name}.")
            else:
                llm_current_type = type(getattr(self, 'llm', None))
                print(f"self.llm is not a ready GenerativeModel client (type: {llm_current_type}).")
                # If self.llm is not a client, try to create a local one using self.model (string model name)
                if isinstance(self.model, str):
                    print(f"Attempting to create a local LLM client using self.model string: '{self.model}'")
                    try:
                        # genai should have been configured in __init__
                        active_llm_client = genai.GenerativeModel(self.model)
                        print(f"Local LLM client created successfully (type: {type(active_llm_client)}).")
                    except Exception as e_create_local:
                        print(f"Error creating local LLM client in {self.name} invoke: {e_create_local}")
                        return None # Cannot proceed without a client
                else:
                    print(f"Cannot create local LLM client: self.model is not a string. Type: {type(self.model)}.")
                    return None # Cannot proceed
            
            if active_llm_client is None:
                print(f"Critical Error in {self.name} invoke: No LLM client could be established.")
                return None
            
            response_obj = active_llm_client.generate_content(input_prompt)
            raw_response_text = response_obj.text

            if raw_response_text:
                print(f"{self.name} generated report successfully.")
                return raw_response_text
            else:
                print(f"Error in {self.name}: LLM returned an empty response.")
                return None
        except Exception as e:
            print(f"Error during {self.name} LLM call: {e}")
            return None
