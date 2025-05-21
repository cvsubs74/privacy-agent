"""
Defines common data structures used across privacy agents.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class PolicyAnalysisResult:
    """Structure for the output of PolicyAnalyzerAgent."""
    summary: str
    relevant_excerpts: List[Dict[str, str]] = field(default_factory=list)
    # Example for excerpt: {'excerpt': 'text', 'location_context': 'Section 1'}

@dataclass
class ComplianceAssessmentResult:
    """Structure for the output of ComplianceAssessorAgent."""
    level: str
    justification: str
    suggestions: List[str] = field(default_factory=list)

@dataclass
class AssessmentResult:
    """Overall assessment result for a single privacy principle."""
    principle_name: str
    principle_explanation: str
    policy_text_snippet: Optional[str] = None # The specific snippet of policy analyzed, if applicable
    policy_analysis: Optional[PolicyAnalysisResult] = None
    compliance_assessment: Optional[ComplianceAssessmentResult] = None
    # Allows for additional metadata if needed
    additional_details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Converts the AssessmentResult to a dictionary for serialization or LLM input."""
        return {
            "principle_name": self.principle_name,
            "principle_explanation": self.principle_explanation,
            "policy_text_snippet": self.policy_text_snippet,
            "policy_analysis": self.policy_analysis.__dict__ if self.policy_analysis else {},
            "compliance_assessment": self.compliance_assessment.__dict__ if self.compliance_assessment else {},
            "additional_details": self.additional_details
        }

if __name__ == '__main__':
    # Example Usage
    analysis_res = PolicyAnalysisResult(
        summary="Policy mentions data collection for newsletters.",
        relevant_excerpts=[{'excerpt': 'We collect email for newsletters.', 'location_context': 'Privacy Policy p.1'}]
    )
    compliance_res = ComplianceAssessmentResult(
        level="Medium",
        justification="States intent but lacks detail.",
        suggestions=["Specify data retention periods."]
    )
    full_assessment = AssessmentResult(
        principle_name="Data Minimization",
        principle_explanation="Collect only necessary data.",
        policy_text_snippet="We collect email for newsletters.",
        policy_analysis=analysis_res,
        compliance_assessment=compliance_res,
        additional_details={"assessed_by": "TestRunner"}
    )
    print("AssessmentResult Example:")
    print(full_assessment)
    print("\nAssessmentResult as dict:")
    print(full_assessment.to_dict())
