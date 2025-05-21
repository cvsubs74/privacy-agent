# privacy_agent/agents/policy_fetcher_agent.py
import typing
from google.adk.agents import Agent
from privacy_agent.utils.web_parser import fetch_url_content, extract_text_from_html

class PolicyFetcherAgent(Agent):
    """
    An agent responsible for fetching and extracting text content from a given URL.
    """

    def __init__(self, name: str = "PolicyFetcherAgent", **kwargs):
        # Provide default string values if 'model' and 'instruction' are not passed
        # to satisfy Pydantic validation in the base Agent class.
        # These are placeholders as PolicyFetcherAgent doesn't use an LLM directly.
        model_arg = kwargs.pop('model', "gemini-2.0-flash") # Placeholder model
        instruction_arg = kwargs.pop('instruction', "Fetch and parse web content from a URL.") # Placeholder instruction

        super().__init__(
            name=name,
            description="Fetches and extracts plain text from a web page URL.",
            model=model_arg,
            instruction=instruction_arg,
            **kwargs
        )

    def invoke(self, input_request: str | dict[str, any], **kwargs) -> typing.Dict[str, any]:
        """
        Fetches and extracts text from the URL provided in input_request.

        Args:
            input_request: A string containing the URL to process.
                           Alternatively, a dictionary with a 'url' key.
            **kwargs: Additional arguments (not used by this agent).

        Returns:
            An AgentOutput dictionary containing the extracted text under the key 'extracted_text'
            or an error message under 'error'.
        """
        if isinstance(input_request, dict):
            url = input_request.get("url")
        elif isinstance(input_request, str):
            url = input_request
        else:
            return {"error": "Invalid input_request type. Expected str or dict with 'url' key."}

        if not url:
            return {"error": "URL not provided in input_request."}

        print(f"{self.name}: Fetching policy from URL: {url}")
        html_content = fetch_url_content(url)

        if html_content is None:
            error_message = f"Failed to fetch content from URL: {url}"
            print(f"{self.name}: {error_message}")
            return {"error": error_message}

        print(f"{self.name}: Extracting text from HTML content (length: {len(html_content)}).")
        extracted_text = extract_text_from_html(html_content)
        print(f"{self.name}: Successfully extracted text (length: {len(extracted_text)}).")

        return {"extracted_text": extracted_text}
