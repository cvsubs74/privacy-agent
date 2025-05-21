#!/usr/bin/env python
"""
Simple test script to verify that the Privacy Assessment Agent components are working correctly.
This script uses the ADK Runner to test each agent individually.
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.adk.runners import Runner

# Import the agents
from privacy_agent.agents.regulation_understanding_agent import RegulationUnderstandingAgent
from privacy_agent.agents.policy_analyzer_agent import PolicyAnalyzerAgent
from privacy_agent.agents.compliance_assessor_agent import ComplianceAssessorAgent

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment.")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# Configure genai with the API key
genai.configure(api_key=api_key)

# Create a runner
runner = Runner()

# Test RegulationUnderstandingAgent
print("\n=== Testing RegulationUnderstandingAgent ===")
try:
    regulation_agent = RegulationUnderstandingAgent(name="TestRegulationUnderstander")
    regulation_result = runner.run(
        agent=regulation_agent,
        inputs={"user_input": "Explain the principle of Data Minimization"}
    )
    print(f"Regulation Understanding Result: {regulation_result}")
    print("RegulationUnderstandingAgent test PASSED!")
except Exception as e:
    print(f"RegulationUnderstandingAgent test FAILED: {e}")

# Test PolicyAnalyzerAgent
print("\n=== Testing PolicyAnalyzerAgent ===")
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
try:
    analyzer_agent = PolicyAnalyzerAgent(name="TestPolicyAnalyzer")
    analyzer_result = runner.run(
        agent=analyzer_agent,
        inputs={
            "user_input": "Analyze this policy for Data Minimization principles",
            "policy_text": SAMPLE_POLICY_TEXT,
            "principle_name": "Data Minimization"
        }
    )
    print(f"Policy Analysis Result: {analyzer_result}")
    print("PolicyAnalyzerAgent test PASSED!")
except Exception as e:
    print(f"PolicyAnalyzerAgent test FAILED: {e}")

# Test ComplianceAssessorAgent
print("\n=== Testing ComplianceAssessorAgent ===")
SAMPLE_ANALYSIS = """
Principle: Data Minimization
Relevant Excerpt(s):
"Data Minimization: We strive to collect only the data necessary for the stated purposes. For newsletter signup, only your email is required."
Analysis:
The policy explicitly addresses the principle of data minimization by stating that they strive to collect only necessary data for stated purposes. They provide a specific example of minimization by noting that for newsletter signup, only an email address is required.
"""
try:
    assessor_agent = ComplianceAssessorAgent(name="TestComplianceAssessor")
    assessor_result = runner.run(
        agent=assessor_agent,
        inputs={
            "user_input": "Assess compliance for Data Minimization",
            "principle_name": "Data Minimization",
            "policy_excerpt": "Data Minimization: We strive to collect only the data necessary for the stated purposes. For newsletter signup, only your email is required.",
            "analysis": SAMPLE_ANALYSIS
        }
    )
    print(f"Compliance Assessment Result: {assessor_result}")
    print("ComplianceAssessorAgent test PASSED!")
except Exception as e:
    print(f"ComplianceAssessorAgent test FAILED: {e}")

print("\nAll tests completed!")
