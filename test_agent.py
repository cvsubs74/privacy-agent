#!/usr/bin/env python
"""
Simple test script to verify that the Privacy Assessment Agent is working correctly.
"""
import os
from dotenv import load_dotenv
from privacy_agent.agents.policy_analyzer_agent import PolicyAnalyzerAgent
from privacy_agent.agents.compliance_assessor_agent import ComplianceAssessorAgent
from privacy_agent.agents.regulation_understanding_agent import RegulationUnderstandingAgent

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("ERROR: GOOGLE_API_KEY not found in environment.")
    exit(1)

print(f"API Key found: {api_key[:5]}...{api_key[-5:]}")

# Test the RegulationUnderstandingAgent
print("\n=== Testing RegulationUnderstandingAgent ===")
regulation_agent = RegulationUnderstandingAgent(name="TestRegulationUnderstander")
regulation_result = regulation_agent.invoke(regulation_name="Data Minimization")
print(f"Regulation Understanding Result: {regulation_result}")

# Test the PolicyAnalyzerAgent
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
analyzer_agent = PolicyAnalyzerAgent(name="TestPolicyAnalyzer")
analyzer_result = analyzer_agent.invoke(policy_text=SAMPLE_POLICY_TEXT, principle_name="Data Minimization")
print(f"Policy Analysis Result: {analyzer_result}")

# Test the ComplianceAssessorAgent
print("\n=== Testing ComplianceAssessorAgent ===")
SAMPLE_ANALYSIS = """
Principle: Data Minimization
Relevant Excerpt(s):
"Data Minimization: We strive to collect only the data necessary for the stated purposes. For newsletter signup, only your email is required."
Analysis:
The policy explicitly addresses the principle of data minimization by stating that they strive to collect only necessary data for stated purposes. They provide a specific example of minimization by noting that for newsletter signup, only an email address is required.
"""
assessor_agent = ComplianceAssessorAgent(name="TestComplianceAssessor")
assessor_result = assessor_agent.invoke(
    principle_name="Data Minimization",
    policy_excerpt="Data Minimization: We strive to collect only the data necessary for the stated purposes. For newsletter signup, only your email is required.",
    analysis=SAMPLE_ANALYSIS
)
print(f"Compliance Assessment Result: {assessor_result}")

print("\nAll tests completed successfully!")
