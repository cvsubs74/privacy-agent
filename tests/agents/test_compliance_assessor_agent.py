import pytest
import os
from dotenv import load_dotenv

from privacy_agent.agents.compliance_assessor_agent import ComplianceAssessorAgent

load_dotenv()

SAMPLE_PRINCIPLE_EXPLANATION_MINIMIZATION = (
    "Data Minimization is a core privacy principle stating that organizations should only collect, "
    "use, or retain personal data that is necessary to accomplish a specified and legitimate purpose. "
    "Excessive data collection should be avoided, and data should not be kept longer than needed."
)

SAMPLE_PRINCIPLE_EXPLANATION_SECURITY = (
    "Data Security is about protecting data from unauthorized access, use, disclosure, alteration, or destruction."
)

SAMPLE_POLICY_ANALYSIS_ADDRESSED_MINIMIZATION = {
    "analysis": "The policy mentions data minimization in section 3, stating they collect only necessary data, e.g., email for newsletters.",
    "excerpts": [
        "We strive to collect only the data necessary for the stated purposes.",
        "For newsletter signup, only your email is required."
    ]
}

SAMPLE_POLICY_ANALYSIS_NOT_ADDRESSED_SECURITY = {
    "analysis": "The policy does not appear to address data security measures explicitly.",
    "excerpts": []
}

@pytest.fixture
def assessor_agent():
    """Fixture to create an instance of ComplianceAssessorAgent."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found, skipping ComplianceAssessorAgent integration tests.")
    return ComplianceAssessorAgent(name="TestComplianceAssessor")

def test_compliance_assessor_principle_addressed(assessor_agent):
    """Tests compliance assessment when the principle is addressed in the policy analysis."""
    print("\n--- Test Case: Principle Addressed (Minimization) ---")
    result = assessor_agent.invoke(
        principle_explanation=SAMPLE_PRINCIPLE_EXPLANATION_MINIMIZATION,
        policy_analysis=SAMPLE_POLICY_ANALYSIS_ADDRESSED_MINIMIZATION
    )
    print(f"LLM Raw Output: {result}")

    assert "error" not in result, f"LLM call resulted in an error: {result.get('error')}"
    assert result.get("compliance_level") != "Could not parse from LLM output.", "Compliance level was not parsed."
    assert isinstance(result.get("compliance_level"), str) and len(result["compliance_level"].strip()) > 0, "Compliance level is empty or invalid."
    assert isinstance(result.get("justification"), str) and len(result["justification"].strip()) > 0, "Justification is empty or invalid."
    assert isinstance(result.get("suggestions"), list), "Suggestions should be a list."

def test_compliance_assessor_principle_not_addressed(assessor_agent):
    """Tests compliance assessment when policy analysis indicates the principle is not addressed."""
    print("\n--- Test Case: Principle Not Addressed (Security) ---")
    result = assessor_agent.invoke(
        principle_explanation=SAMPLE_PRINCIPLE_EXPLANATION_SECURITY,
        policy_analysis=SAMPLE_POLICY_ANALYSIS_NOT_ADDRESSED_SECURITY
    )
    print(f"LLM Raw Output: {result}")

    assert "error" not in result, f"LLM call resulted in an error: {result.get('error')}"
    assert result.get("compliance_level") != "Could not parse from LLM output.", "Compliance level was not parsed."
    assert isinstance(result.get("compliance_level"), str) and len(result["compliance_level"].strip()) > 0
    assert isinstance(result.get("justification"), str) and len(result["justification"].strip()) > 0
    assert isinstance(result.get("suggestions"), list)

def test_compliance_assessor_invalid_inputs(assessor_agent):
    """Tests agent's handling of invalid or empty inputs."""
    print("\n--- Test Case: Invalid Inputs ---")
    
    invalid_explanation_result = assessor_agent.invoke(
        principle_explanation="", 
        policy_analysis=SAMPLE_POLICY_ANALYSIS_ADDRESSED_MINIMIZATION
    )
    assert "error" in invalid_explanation_result, "Expected error for empty principle explanation."
    assert "Invalid or empty principle explanation" in invalid_explanation_result["error"]

    invalid_analysis_result = assessor_agent.invoke(
        principle_explanation=SAMPLE_PRINCIPLE_EXPLANATION_MINIMIZATION, 
        policy_analysis={}
    )
    assert "error" in invalid_analysis_result, "Expected error for empty policy analysis."
    assert "Invalid or incomplete policy analysis" in invalid_analysis_result["error"]

    invalid_analysis_result_missing_keys = assessor_agent.invoke(
        principle_explanation=SAMPLE_PRINCIPLE_EXPLANATION_MINIMIZATION, 
        policy_analysis={"analysis": "some analysis"}
    )
    assert "error" in invalid_analysis_result_missing_keys, "Expected error for policy analysis missing keys."
    assert "Invalid or incomplete policy analysis" in invalid_analysis_result_missing_keys["error"]
