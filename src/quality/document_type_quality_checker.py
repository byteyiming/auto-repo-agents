"""
Document Type-Aware Quality Checker
Provides document-type-specific quality checking with appropriate thresholds
"""
import re
from typing import Dict, List, Optional
from src.quality.quality_checker import QualityChecker
from src.context.shared_context import AgentType

# Document type-specific quality requirements
DOCUMENT_TYPE_REQUIREMENTS = {
    AgentType.REQUIREMENTS_ANALYST: {
        "min_words": 300,
        "required_sections": [
            r"^#+\s+Project\s+Overview",
            r"^#+\s+Core\s+Features",
            r"^#+\s+Technical\s+Requirements",
            r"^#+\s+User\s+Personas",
            r"^#+\s+Business\s+Objectives",
            r"^#+\s+Constraints"
        ],
        "min_readability": 50.0
    },
    AgentType.PROJECT_CHARTER: {
        "min_words": 500,
        "required_sections": [
            r"^#+\s+(Executive\s+)?Summary",
            r"^#+\s+Project\s+Overview",
            r"^#+\s+(Business\s+)?Objectives",
            r"^#+\s+Scope",
            r"^#+\s+Stakeholders"
        ],
        "min_readability": 50.0
    },
    AgentType.PM_DOCUMENTATION: {
        "min_words": 800,
        "required_sections": [
            r"^#+\s+Project\s+Timeline",
            r"^#+\s+Resource\s+Requirements",
            r"^#+\s+Budget",
            r"^#+\s+Risk",
            r"^#+\s+Success\s+Metrics"
        ],
        "min_readability": 50.0
    },
    AgentType.USER_STORIES: {
        "min_words": 400,
        "required_sections": [
            r"^#+\s+User\s+Stories",
            r"^#+\s+(Acceptance\s+)?Criteria",
            r"^#+\s+Epic",
            r"^#+\s+(Feature|Feature\s+Breakdown)"
        ],
        "min_readability": 50.0
    },
    AgentType.TECHNICAL_DOCUMENTATION: {
        "min_words": 1000,
        "required_sections": [
            r"^#+\s+System\s+Architecture",
            r"^#+\s+Technical\s+Stack",
            r"^#+\s+Database\s+Design",
            r"^#+\s+API\s+Design",
            r"^#+\s+Security"
        ],
        "min_readability": 45.0
    },
    AgentType.DATABASE_SCHEMA: {
        "min_words": 600,
        "required_sections": [
            r"^#+\s+Database\s+Overview",
            r"^#+\s+(Schema|Table)",
            r"^#+\s+(Relationship|Entity)",
            r"^#+\s+(Index|Indexing)"
        ],
        "min_readability": 45.0
    },
    AgentType.API_DOCUMENTATION: {
        "min_words": 800,
        "required_sections": [
            r"^#+\s+API\s+Overview",
            r"^#+\s+Authentication",
            r"^#+\s+Endpoint",
            r"^#+\s+(Data\s+)?Model",
            r"^#+\s+Error"
        ],
        "min_readability": 50.0
    },
    AgentType.SETUP_GUIDE: {
        "min_words": 600,
        "required_sections": [
            r"^#+\s+Prerequisite",
            r"^#+\s+Installation",
            r"^#+\s+(Setup|Configuration)",
            r"^#+\s+(Running|Start)",
            r"^#+\s+Troubleshooting"
        ],
        "min_readability": 60.0
    },
    AgentType.DEVELOPER_DOCUMENTATION: {
        "min_words": 800,
        "required_sections": [
            r"^#+\s+(Getting\s+)?Started",
            r"^#+\s+(Architecture|Structure)",
            r"^#+\s+(Development|Coding)",
            r"^#+\s+(Testing|Test)",
            r"^#+\s+(Deployment|Deploy)"
        ],
        "min_readability": 50.0
    },
    AgentType.STAKEHOLDER_COMMUNICATION: {
        "min_words": 400,
        "required_sections": [
            r"^#+\s+(Executive\s+)?Summary",
            r"^#+\s+(Key\s+)?(Point|Highlight)",
            r"^#+\s+(Impact|Benefit)",
            r"^#+\s+(Next\s+)?Step"
        ],
        "min_readability": 60.0
    },
    AgentType.TEST_DOCUMENTATION: {
        "min_words": 600,
        "required_sections": [
            r"^#+\s+Test\s+(Strategy|Plan)",
            r"^#+\s+Test\s+Case",
            r"^#+\s+Test\s+Scenario",
            r"^#+\s+(Test\s+)?Environment",
            r"^#+\s+(Test\s+)?(Coverage|Result)"
        ],
        "min_readability": 50.0
    },
    AgentType.USER_DOCUMENTATION: {
        "min_words": 500,
        "required_sections": [
            r"^#+\s+Introduction",
            r"^#+\s+(Installation|Setup)",
            r"^#+\s+(Usage|Basic|Getting\s+Started)",
            r"^#+\s+Feature",
            r"^#+\s+(Troubleshooting|FAQ)"
        ],
        "min_readability": 65.0
    },
    AgentType.BUSINESS_MODEL: {
        "min_words": 600,
        "required_sections": [
            r"^#+\s+(Executive\s+)?Summary",
            r"^#+\s+Business\s+Model",
            r"^#+\s+(Revenue|Monetization)",
            r"^#+\s+(Market|Target)",
            r"^#+\s+(Competitive|Competition)"
        ],
        "min_readability": 55.0
    },
    AgentType.MARKETING_PLAN: {
        "min_words": 700,
        "required_sections": [
            r"^#+\s+(Executive\s+)?Summary",
            r"^#+\s+(Marketing\s+)?Strategy",
            r"^#+\s+(Channel|Campaign)",
            r"^#+\s+(Budget|Cost)",
            r"^#+\s+(Metric|KPI|Performance)"
        ],
        "min_readability": 55.0
    },
    AgentType.SUPPORT_PLAYBOOK: {
        "min_words": 500,
        "required_sections": [
            r"^#+\s+(Support|Troubleshooting)",
            r"^#+\s+(Common|Issue)",
            r"^#+\s+(Escalation|Process)",
            r"^#+\s+(Resolution|Solution)",
            r"^#+\s+(FAQ|Help)"
        ],
        "min_readability": 60.0
    },
    AgentType.LEGAL_COMPLIANCE: {
        "min_words": 500,
        "required_sections": [
            r"^#+\s+(Privacy|Legal)",
            r"^#+\s+(Compliance|Regulation)",
            r"^#+\s+(Data\s+)?(Handling|Protection)",
            r"^#+\s+(License|License\s+Compatibility)",
            r"^#+\s+(Policy|Term)"
        ],
        "min_readability": 45.0
    }
}


class DocumentTypeQualityChecker:
    """Quality checker with document-type-specific requirements"""
    
    def __init__(self):
        """Initialize document type quality checker"""
        self.base_checker = QualityChecker()
    
    def get_requirements_for_type(self, document_type: str) -> Dict:
        """
        Get quality requirements for a specific document type
        
        Args:
            document_type: Document type (AgentType enum value or string)
            
        Returns:
            Dict with min_words, required_sections, min_readability
        """
        # Try to match document type
        doc_type_lower = document_type.lower().replace('_', ' ').replace('-', ' ')
        
        # Try exact match first
        for agent_type, requirements in DOCUMENT_TYPE_REQUIREMENTS.items():
            if agent_type.value.lower() == document_type.lower():
                return requirements
        
        # Try partial match
        for agent_type, requirements in DOCUMENT_TYPE_REQUIREMENTS.items():
            if doc_type_lower in agent_type.value.lower() or agent_type.value.lower() in doc_type_lower:
                return requirements
        
        # Default requirements for unknown types
        return {
            "min_words": 500,
            "required_sections": [
                r"^#+\s+.*",  # At least one section
            ],
            "min_readability": 50.0
        }
    
    def check_quality_for_type(
        self,
        content: str,
        document_type: str,
        weights: Optional[Dict[str, float]] = None
    ) -> Dict:
        """
        Check quality for a specific document type
        
        Args:
            content: Document content
            document_type: Document type (AgentType enum value or string)
            weights: Custom weights for overall score calculation
            
        Returns:
            Comprehensive quality report
        """
        # Get requirements for this document type
        requirements = self.get_requirements_for_type(document_type)
        
        # Create checker with document-type-specific requirements
        checker = QualityChecker(
            min_words=requirements["min_words"],
            required_sections=requirements["required_sections"],
            min_readability_score=requirements["min_readability"]
        )
        
        # Run quality check
        result = checker.check_quality(content, weights=weights)
        
        # Add document type info to result
        result["document_type"] = document_type
        result["requirements"] = requirements
        
        return result
    
    def check_multiple_documents(
        self,
        documents: Dict[str, str],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Dict]:
        """
        Check quality for multiple documents
        
        Args:
            documents: Dict mapping document names/types to content
            weights: Custom weights for overall score calculation
            
        Returns:
            Dict mapping document names to quality reports
        """
        results = {}
        
        for doc_name, doc_content in documents.items():
            try:
                # Extract document type from name
                doc_type = self._extract_document_type(doc_name)
                
                # Check quality
                result = self.check_quality_for_type(
                    doc_content,
                    doc_type,
                    weights=weights
                )
                
                results[doc_name] = result
            except Exception as e:
                # If check fails, provide minimal result
                results[doc_name] = {
                    "overall_score": 0,
                    "passed": False,
                    "error": str(e),
                    "document_type": doc_name
                }
        
        return results
    
    def _extract_document_type(self, doc_name: str) -> str:
        """
        Extract document type from document name
        
        Args:
            doc_name: Document name (e.g., "requirements.md", "technical_documentation")
            
        Returns:
            Document type string
        """
        # Remove file extension
        doc_name = doc_name.replace('.md', '').replace('.txt', '')
        
        # Map common names to agent types
        name_mapping = {
            "requirements": AgentType.REQUIREMENTS_ANALYST.value,
            "project_charter": AgentType.PROJECT_CHARTER.value,
            "charter": AgentType.PROJECT_CHARTER.value,
            "pm_documentation": AgentType.PM_DOCUMENTATION.value,
            "project_plan": AgentType.PM_DOCUMENTATION.value,
            "pm": AgentType.PM_DOCUMENTATION.value,
            "user_stories": AgentType.USER_STORIES.value,
            "technical_documentation": AgentType.TECHNICAL_DOCUMENTATION.value,
            "technical_spec": AgentType.TECHNICAL_DOCUMENTATION.value,
            "technical": AgentType.TECHNICAL_DOCUMENTATION.value,
            "database_schema": AgentType.DATABASE_SCHEMA.value,
            "database": AgentType.DATABASE_SCHEMA.value,
            "api_documentation": AgentType.API_DOCUMENTATION.value,
            "api": AgentType.API_DOCUMENTATION.value,
            "setup_guide": AgentType.SETUP_GUIDE.value,
            "setup": AgentType.SETUP_GUIDE.value,
            "developer_documentation": AgentType.DEVELOPER_DOCUMENTATION.value,
            "developer_guide": AgentType.DEVELOPER_DOCUMENTATION.value,
            "developer": AgentType.DEVELOPER_DOCUMENTATION.value,
            "stakeholder_communication": AgentType.STAKEHOLDER_COMMUNICATION.value,
            "stakeholder": AgentType.STAKEHOLDER_COMMUNICATION.value,
            "test_documentation": AgentType.TEST_DOCUMENTATION.value,
            "test": AgentType.TEST_DOCUMENTATION.value,
            "user_documentation": AgentType.USER_DOCUMENTATION.value,
            "user_guide": AgentType.USER_DOCUMENTATION.value,
            "user": AgentType.USER_DOCUMENTATION.value,
            "business_model": AgentType.BUSINESS_MODEL.value,
            "business": AgentType.BUSINESS_MODEL.value,
            "marketing_plan": AgentType.MARKETING_PLAN.value,
            "marketing": AgentType.MARKETING_PLAN.value,
            "support_playbook": AgentType.SUPPORT_PLAYBOOK.value,
            "support": AgentType.SUPPORT_PLAYBOOK.value,
            "legal_compliance": AgentType.LEGAL_COMPLIANCE.value,
            "legal": AgentType.LEGAL_COMPLIANCE.value,
        }
        
        # Try to find matching type
        doc_name_lower = doc_name.lower()
        for key, agent_type in name_mapping.items():
            if key in doc_name_lower:
                return agent_type
        
        # Return as-is if no match
        return doc_name

