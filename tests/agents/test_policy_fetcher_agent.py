import pytest
from privacy_agent.agents.policy_fetcher_agent import PolicyFetcherAgent

@pytest.fixture
def fetcher_agent():
    """Fixture to create an instance of PolicyFetcherAgent."""
    return PolicyFetcherAgent()

VALID_URL = "https://termly.io/html_document/website-privacy-policy-template-text-format/"
PROBLEMATIC_URL = "https://www.google.com/policies/privacy/"

def test_policy_fetcher_valid_url(fetcher_agent):
    """Tests fetching and extracting text from a known valid URL."""
    print(f"\n--- Testing {fetcher_agent.name} with valid URL: {VALID_URL} ---")
    output = fetcher_agent.invoke(VALID_URL)

    assert "error" not in output, f"Fetching resulted in an error: {output.get('error')}"
    assert "extracted_text" in output, "Output dictionary should contain 'extracted_text'."
    assert isinstance(output["extracted_text"], str), "Extracted text should be a string."
    assert len(output["extracted_text"].strip()) > 500, \
        f"Expected more than 500 chars, got {len(output['extracted_text'])} for {VALID_URL}"
    print(f"Successfully extracted text, length: {len(output['extracted_text'])}")

def test_policy_fetcher_problematic_url(fetcher_agent):
    """
    Tests fetching from a URL known to be problematic for simple scrapers.
    The test expects either an error during fetching or very little extracted text.
    """
    print(f"\n--- Testing {fetcher_agent.name} with problematic URL: {PROBLEMATIC_URL} ---")
    output = fetcher_agent.invoke(PROBLEMATIC_URL)

    if "error" in output:
        print(f"Fetching problematic URL resulted in an error (as sometimes expected): {output['error']}")
        assert isinstance(output["error"], str)
    else:
        assert "extracted_text" in output, \
            "Output should contain 'extracted_text' even if content is minimal or fetching was problematic but didn't error."
        assert isinstance(output["extracted_text"], str), "Extracted text should be a string."
        assert len(output["extracted_text"].strip()) < 500, \
            f"Expected minimal text (<500 chars) from problematic URL, got length {len(output['extracted_text'].strip()) if output.get('extracted_text') else 'N/A'}"
        print(f"Extracted text length (problematic URL, no error): {len(output['extracted_text'])}")

def test_policy_fetcher_invalid_input_type(fetcher_agent):
    """Tests the agent's response to an invalid input type (e.g., an integer)."""
    print(f"\n--- Testing {fetcher_agent.name} with invalid input type (integer) ---")
    output = fetcher_agent.invoke(123) # type: ignore
    assert "error" in output, "Expected an error for invalid input type."
    assert "Invalid input_request type" in output["error"], f"Unexpected error message: {output['error']}"

def test_policy_fetcher_missing_url_in_dict(fetcher_agent):
    """Tests agent's response when a dictionary input is missing the 'url' key."""
    print(f"\n--- Testing {fetcher_agent.name} with missing 'url' in dict ---")
    output = fetcher_agent.invoke({})
    assert "error" in output, "Expected an error for missing URL in dictionary."
    assert "URL not provided" in output["error"], f"Unexpected error message: {output['error']}"

def test_policy_fetcher_empty_url_string(fetcher_agent):
    """Tests agent's response to an empty string as URL."""
    print(f"\n--- Testing {fetcher_agent.name} with empty URL string ---")
    output = fetcher_agent.invoke("")
    assert "error" in output, "Expected an error for empty URL string."
    assert "URL not provided" in output["error"], f"Unexpected error message: {output['error']}"
