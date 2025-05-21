import pytest
import os
from dotenv import load_dotenv

from privacy_agent.agents.policy_analyzer_agent import PolicyAnalyzerAgent

load_dotenv()

SAMPLE_POLICY_TEXT = """
Our Privacy Policy
Effective Date: January 1, 2024

1. Data Collection: We collect your email address when you sign up for our newsletter.
   We also collect usage data through cookies to improve our service.
2. Data Usage: Your email is used to send newsletters. Usage data helps us understand user behavior.
   We do not sell your personal data.
3. Data Minimization: We strive to collect only the data necessary for the stated purposes.
   For newsletter signup, only your email is required.
4. User Rights: You can unsubscribe at any time. You can request access to or deletion of your data.
"""

@pytest.fixture
def analyzer_agent_fixture():
    """Fixture to create an instance of PolicyAnalyzerAgent."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found, skipping PolicyAnalyzerAgent integration tests.")
    return PolicyAnalyzerAgent(name="TestPolicyAnalyzer")

def test_policy_analyzer_principle_addressed(analyzer_agent_fixture):
    """Tests analysis when the principle is clearly addressed in the policy."""
    principle = "Data Minimization"
    print(f"\n--- Analyzing for Principle: '{principle}' ---")
    result = analyzer_agent_fixture.invoke(policy_text=SAMPLE_POLICY_TEXT, principle_name=principle)

    assert "error" not in result, f"LLM call resulted in an error: {result.get('error')}"
    assert "analysis" in result, "Result should contain an 'analysis' key."
    assert isinstance(result["analysis"], str) and len(result["analysis"].strip()) > 0, "Analysis should not be empty."
    assert "excerpts" in result, "Result should contain an 'excerpts' key."
    assert isinstance(result["excerpts"], list)
    assert len(result["excerpts"]) > 0, f"Expected excerpts for '{principle}', but got none."
    # Ensure excerpts are not just placeholders like "None." or very short.
    assert all(excerpt.strip().lower() != "none." and len(excerpt.strip()) > 5 for excerpt in result["excerpts"]), \
        f"Excerpts for '{principle}' should be substantive, not placeholders like 'None.' or very short. Got: {result['excerpts']}"

    print(f"Analysis: {result.get('analysis')}")
    if result.get('excerpts'):
        for excerpt in result['excerpts']:
            print(f"- {excerpt}")

def test_policy_analyzer_principle_not_addressed(analyzer_agent_fixture):
    """Tests analysis when the principle is likely not addressed in the policy."""
    principle = "Data Security Breach Notification" # This principle is likely not in the sample
    print(f"\n--- Analyzing for Principle: '{principle}' ---")
    result = analyzer_agent_fixture.invoke(policy_text=SAMPLE_POLICY_TEXT, principle_name=principle)

    assert "error" not in result, f"LLM call resulted in an error: {result.get('error')}"
    assert "analysis" in result, "Result should contain an 'analysis' key."
    analysis_text = result.get("analysis", "").lower()
    assert len(analysis_text.strip()) > 0, "Analysis should not be empty even if principle not addressed."

    # Flexible check for "not addressed"
    not_addressed_indicators = [
        "policy does not appear to address this principle",
        "does not address",
        "not addressed in the policy",
        "no mention of",
        "not explicitly cover",
        "unable to find specific clauses"
    ]
    assert any(indicator in analysis_text for indicator in not_addressed_indicators), \
        f"Analysis text '{result.get('analysis')}' does not clearly state the principle '{principle}' is unaddressed. Looked for: {not_addressed_indicators}"

    assert "excerpts" in result, "Result should contain an 'excerpts' key."
    assert isinstance(result["excerpts"], list)

    # Allow excerpts to be empty OR contain a single placeholder like "None.", "(None.)", or "(None)" when not addressed.
    excerpts = result.get("excerpts", [])
    is_placeholder = False
    if len(excerpts) == 1:
        placeholder_text = excerpts[0].strip().lower()
        if placeholder_text in ["none.", "(none.)", "(none)"]:
            is_placeholder = True
    
    assert len(excerpts) == 0 or is_placeholder, \
        f"Expected no substantive excerpts or a single 'None' placeholder when principle '{principle}' is not addressed, but got: {excerpts}"

    print(f"Analysis: {result.get('analysis')}")


def test_policy_analyzer_invalid_inputs(analyzer_agent_fixture):
    """Tests the agent's handling of invalid or empty inputs."""
    print("\n--- Testing with invalid inputs ---")
    
    # Test with empty policy text
    invalid_policy_result = analyzer_agent_fixture.invoke(policy_text="", principle_name="Data Minimization")
    assert "error" in invalid_policy_result, "Expected error for empty policy text."
    assert "invalid or empty policy text" in invalid_policy_result.get("error", "").lower(), \
        f"Error message for empty policy text is not as expected. Got: {invalid_policy_result.get('error')}"
    print(f"Empty policy text test: {invalid_policy_result}")

    # Test with empty principle name
    invalid_principle_result = analyzer_agent_fixture.invoke(policy_text=SAMPLE_POLICY_TEXT, principle_name="")
    assert "error" in invalid_principle_result, "Expected error for empty principle name."
    assert "invalid or empty principle name" in invalid_principle_result.get("error", "").lower(), \
        f"Error message for empty principle name is not as expected. Got: {invalid_principle_result.get('error')}"
    print(f"Empty principle name test: {invalid_principle_result}")
