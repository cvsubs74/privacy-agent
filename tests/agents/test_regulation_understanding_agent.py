import pytest
import os
from dotenv import load_dotenv

from privacy_agent.agents.regulation_understanding_agent import RegulationUnderstandingAgent

load_dotenv()

@pytest.fixture
def understanding_agent():
    """Fixture to create an instance of RegulationUnderstandingAgent."""
    if not os.getenv("GEMINI_API_KEY"):
        pytest.skip("GEMINI_API_KEY not found, skipping RegulationUnderstandingAgent integration tests.")
    return RegulationUnderstandingAgent(name="TestRegulationUnderstandingAgent", model_name="gemini-1.5-flash-latest")

def test_regulation_understanding_valid_principle_string(understanding_agent):
    """Tests the agent with a valid principle name as a string input."""
    test_principle = "Data Minimization"
    print(f"\n--- Testing {understanding_agent.name} with principle: '{test_principle}' ---")
    output = understanding_agent.invoke(test_principle)

    assert "error" not in output, f"LLM call resulted in an error: {output.get('error')}"
    assert "explanation" in output, "Output dictionary should contain an 'explanation' key."
    assert isinstance(output["explanation"], str), "Explanation should be a string."
    assert len(output["explanation"].strip()) > 0, "Explanation should not be empty."
    print(f"Explanation received: {output['explanation'][:100]}...")

def test_regulation_understanding_valid_principle_dict(understanding_agent):
    """Tests the agent with a valid principle name as a dictionary input."""
    test_principle_dict_input = {"principle": "Purpose Limitation"}
    principle_name = test_principle_dict_input['principle']
    print(f"\n--- Testing {understanding_agent.name} with principle (dict input): '{principle_name}' ---")
    output = understanding_agent.invoke(test_principle_dict_input)

    assert "error" not in output, f"LLM call resulted in an error: {output.get('error')}"
    assert "explanation" in output, "Output dictionary should contain an 'explanation' key."
    assert isinstance(output["explanation"], str), "Explanation should be a string."
    assert len(output["explanation"].strip()) > 0, "Explanation should not be empty."
    print(f"Explanation received: {output['explanation'][:100]}...")

def test_regulation_understanding_invalid_input_none(understanding_agent):
    """Tests the agent's response to None as input."""
    print(f"\n--- Testing {understanding_agent.name} with invalid input (None) ---")
    output = understanding_agent.invoke(None) # type: ignore
    assert "error" in output, "Expected an error for None input."
    assert "Invalid input_request type" in output["error"] or "Privacy principle/regulation name not provided" in output["error"]

def test_regulation_understanding_invalid_input_empty_dict(understanding_agent):
    """Tests the agent's response to an empty dictionary as input."""
    print(f"\n--- Testing {understanding_agent.name} with invalid input (empty dict) ---")
    output = understanding_agent.invoke({})
    assert "error" in output, "Expected an error for empty dictionary input."
    assert "Privacy principle/regulation name not provided" in output["error"]
