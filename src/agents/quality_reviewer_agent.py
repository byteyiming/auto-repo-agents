"""
Quality Reviewer Agent
Reviews and improves all generated documentation
"""
from typing import Optional, Dict, List
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.quality.quality_checker import QualityChecker
from src.quality.document_type_quality_checker import DocumentTypeQualityChecker
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_quality_reviewer_prompt


class QualityReviewerAgent(BaseAgent):
    """
    Quality Reviewer Agent
    
    Reviews all generated documentation and provides:
    - Overall quality assessment
    - Completeness analysis
    - Clarity and readability review
    - Consistency checks
    - Technical accuracy review
    - Improvement suggestions
    - Quality metrics
    """
    
    def __init__(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        rate_limiter: Optional[RequestQueue] = None,
        file_manager: Optional[FileManager] = None,
        quality_checker: Optional[QualityChecker] = None,
        api_key: Optional[str] = None,
        **provider_kwargs
    ):
        """Initialize Quality Reviewer Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/quality")
        self.quality_checker = quality_checker or QualityChecker()
        # Use document-type-aware quality checker for better accuracy
        self.document_type_checker = DocumentTypeQualityChecker()
    
    def generate(self, all_documentation: Dict[str, str]) -> str:
        """
        Generate quality review report from all documentation
        
        Args:
            all_documentation: Dict mapping document names to their content
        
        Returns:
            Generated quality review report (Markdown)
        """
        # First run automated quality checks using document-type-aware checker
        automated_scores = {}
        for doc_name, doc_content in all_documentation.items():
            try:
                # Use document-type-aware checker for better accuracy
                quality_result = self.document_type_checker.check_multiple_documents(
                    {doc_name: doc_content}
                ).get(doc_name, {})
                
                # Fallback to base checker if document-type checker fails
                if not quality_result or quality_result.get("error"):
                    quality_result = self.quality_checker.check_quality(doc_content)
                
                automated_scores[doc_name] = quality_result
            except Exception as e:
                # Skip quality check for this document if it fails
                automated_scores[doc_name] = {
                    "overall_score": 0,
                    "passed": False,
                    "error": str(e),
                    "word_count": {"word_count": 0},
                    "sections": {"completeness_score": 0, "found_count": 0, "required_count": 0},
                    "readability": {"readability_score": 0, "level": "unknown"}
                }
        
        # Get prompt from centralized prompts config
        full_prompt = get_quality_reviewer_prompt(all_documentation)
        
        # Add automated scores to prompt for LLM context
        if automated_scores:
            scores_summary = "\n\n## Automated Quality Scores:\n"
            for doc_name, score_data in automated_scores.items():
                scores_summary += f"\n### {doc_name}\n"
                scores_summary += f"- Overall Score: {score_data.get('overall_score', 0):.1f}/100\n"
                # Fix: Access word_count directly from the result structure
                word_count_data = score_data.get('word_count', {})
                sections_data = score_data.get('sections', {})
                readability_data = score_data.get('readability', {})
                
                scores_summary += f"- Word Count: {word_count_data.get('word_count', 0)} (min: {word_count_data.get('min_threshold', 100)}, passed: {word_count_data.get('passed', False)})\n"
                scores_summary += f"- Section Completeness: {sections_data.get('completeness_score', 0):.1f}% ({sections_data.get('found_count', 0)}/{sections_data.get('required_count', 0)} sections found, passed: {sections_data.get('passed', False)})\n"
                scores_summary += f"- Readability Score: {readability_data.get('readability_score', 0):.1f} ({readability_data.get('level', 'unknown')}, passed: {readability_data.get('passed', False)})\n"
                if sections_data.get('missing_sections'):
                    scores_summary += f"- Missing Sections: {', '.join([s.replace('^#+\\\\s+', '').replace('\\\\s+', ' ') for s in sections_data.get('missing_sections', [])[:3]])}\n"
            
            full_prompt += scores_summary + "\n\nConsider these automated scores in your review. Focus on improving documents with low scores."
        
        
        stats = self.get_stats()
        
        try:
            review_report = self._call_llm(full_prompt)
            return review_report
        except Exception as e:
            raise
    
    def generate_and_save(
        self,
        all_documentation: Dict[str, str],
        output_filename: str = "quality_review.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate quality review and save to file
        
        Args:
            all_documentation: Dict mapping document names to their content
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
            
        Returns:
            Absolute path to saved file
        """
        # Generate review report
        review_report = self.generate(all_documentation)
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, review_report)
            file_size = self.file_manager.get_file_size(output_filename)
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.QUALITY_REVIEWER,
                    document_type="quality_review",
                    content=review_report,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
            
            return file_path
        except Exception as e:
            raise

