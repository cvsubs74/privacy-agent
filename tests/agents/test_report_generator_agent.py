import pytest
import os
from dotenv import load_dotenv
from privacy_agent.agents.report_generator_agent import ReportGeneratorAgent
from privacy_agent.data_structures import AssessmentResult, PolicyAnalysisResult, ComplianceAssessmentResult

# Load environment variables for testing context if needed, or mock them
load_dotenv()

# Ensure GEMINI_API_KEY is available for tests that might make real API calls
# For production tests, consider mocking the API calls.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("Warning: GEMINI_API_KEY not found. Real API calls in tests might fail.")
    # pytest.skip("GEMINI_API_KEY not found, skipping integration tests", allow_module_level=True)


def test_report_generator_agent_invoke():
    """
    Tests the invoke method of the ReportGeneratorAgent.
    """
    print("Testing ReportGeneratorAgent...")
    report_agent = ReportGeneratorAgent()

    # Sample data (mimicking outputs from previous agents)
    sample_policy_text = """
    Privacy Policy for Sample Service

    1. Data Collection: We collect your email address when you sign up for our newsletter.
    We try not to collect more data than we need.

    2. Data Usage: We use your email to send you newsletters and promotional offers.

    3. Data Sharing: We do not share your personal data with third parties without your consent,
    unless required by law.

    4. Data Security: Our security is industry standard.

    5. Your Rights: You can unsubscribe at any time.
    """

    assessment_results_data = [
        {
            "principle_name": "Data Minimization",
            "principle_explanation": "Collect only data that is strictly necessary for the specified purpose.",
            "policy_analysis": {
                "summary": "The policy mentions collecting email addresses for newsletters and expresses an intention to minimize data collection.",
                "relevant_excerpts": [
                    {"excerpt": "We collect your email address when you sign up for our newsletter.", "location_context": "Section 1"},
                    {"excerpt": "We try not to collect more data than we need.", "location_context": "Section 1"}
                ]
            },
            "compliance_assessment": {
                "level": "Medium",
                "justification": "The policy states an intention for data minimization but lacks specifics on what 'need' means.",
                "suggestions": ["Specify the exact data points collected and why each is necessary.", "Define retention periods."]
            }
        },
        {
            "principle_name": "Data Security",
            "principle_explanation": "Implement appropriate technical and organizational measures to protect data.",
            "policy_analysis": {
                "summary": "The policy makes a general statement about 'industry standard' security.",
                "relevant_excerpts": [
                    {"excerpt": "Our security is industry standard.", "location_context": "Section 4"}
                ]
            },
            "compliance_assessment": {
                "level": "Low",
                "justification": "'Industry standard' is vague and provides no concrete information on security measures.",
                "suggestions": ["Detail specific security measures (e.g., encryption, access controls).", "Mention security certifications or audits if applicable."]
            }
        },
        {
            "principle_name": "Transparency",
            "principle_explanation": "Be clear and open with individuals about how their personal data is collected, used, and shared.",
            "policy_analysis": {
                "summary": "The policy is very brief and lacks detailed information on data usage and sharing.",
                "relevant_excerpts": []
            },
            "compliance_assessment": {
                "level": "Low",
                "justification": "Insufficient detail on data processing activities. Does not clearly state all purposes or sharing practices.",
                "suggestions": ["Provide a comprehensive list of data uses.", "Clearly list any third-party sharing.", "Explain user rights more thoroughly."]
            }
        }
    ]

    # Convert dicts to Pydantic models
    assessment_results = []
    for item in assessment_results_data:
        policy_analysis = PolicyAnalysisResult(**item["policy_analysis"])
        compliance_assessment = ComplianceAssessmentResult(**item["compliance_assessment"])
        assessment_results.append(AssessmentResult(
            principle_name=item["principle_name"],
            principle_explanation=item["principle_explanation"],
            policy_analysis=policy_analysis,
            compliance_assessment=compliance_assessment
        ))

    print(f"Generating report for {len(assessment_results)} principles...")
    report = report_agent.invoke(policy_text=sample_policy_text, assessment_results=assessment_results)

    assert report is not None, "Report generation failed, returned None."
    assert isinstance(report, str), f"Report should be a string, but got {type(report)}"
    assert len(report.strip()) > 0, "Generated report is empty."
    print("ReportGenerator generated report successfully.")
    print("\n--- Generated Report (Snippet) ---")
    print(report[:1000] + "..." if len(report) > 1000 else report) # Print a snippet
    print("\n--- Test complete for ReportGenerator ---")

# Example of how to run this test file using pytest:
# In your terminal, navigate to the root of your project (where pyproject.toml is)
# and run: poetry run pytest tests/agents/test_report_generator_agent.py
# Or if pytest is globally available or in your venv path: pytest tests/agents/test_report_generator_agent.py
