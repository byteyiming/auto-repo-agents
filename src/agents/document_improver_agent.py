"""
Document Improver Agent
Automatically improves documents based on quality review feedback
"""
from typing import Optional, Dict
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentImproverAgent(BaseAgent):
    """
    Document Improver Agent
    
    Automatically improves documents based on quality review feedback.
    This agent takes the original document and quality review suggestions,
    then generates an improved version.
    """
    
    def __init__(
        self,
        provider_name: Optional[str] = None,
        model_name: Optional[str] = None,
        rate_limiter: Optional[RequestQueue] = None,
        file_manager: Optional[FileManager] = None,
        api_key: Optional[str] = None,
        **provider_kwargs
    ):
        """Initialize Document Improver Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager()
    
    def generate(self, input_data: str) -> str:
        """
        Generate improved document (required by BaseAgent)
        
        Args:
            input_data: JSON string with 'original_document', 'document_type', 'quality_feedback'
        
        Returns:
            Improved document content
        """
        import json
        try:
            data = json.loads(input_data)
            return self.improve_document(
                original_document=data.get('original_document', ''),
                document_type=data.get('document_type', 'document'),
                quality_feedback=data.get('quality_feedback', ''),
                focus_areas=data.get('focus_areas')
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback: treat input_data as quality feedback for a simple document
            return self.improve_document(
                original_document="",
                document_type="document",
                quality_feedback=input_data
            )
    
    def improve_document(
        self,
        original_document: str,
        document_type: str,
        quality_feedback: str,
        focus_areas: Optional[list] = None
    ) -> str:
        """
        Improve a document based on quality review feedback
        
        Args:
            original_document: The original document content
            document_type: Type of document (e.g., "technical_documentation")
            quality_feedback: Quality review feedback and suggestions
            focus_areas: Optional list of specific areas to focus on
        
        Returns:
            Improved document content
        """
        focus_text = ""
        if focus_areas:
            focus_text = f"\n\nFocus on these specific areas:\n" + "\n".join(f"- {area}" for area in focus_areas)
        
        prompt = f"""You are a Documentation Improvement Specialist. Your task is to improve a document based on quality review feedback.

CRITICAL INSTRUCTIONS:
1. Read the original document carefully
2. Review the quality feedback and improvement suggestions
3. Generate an IMPROVED version that addresses ALL issues mentioned in the feedback
4. Ensure the improved document is COMPLETE (no cut-off sections)
5. Maintain the original structure and style while fixing issues
6. Add missing content, clarify ambiguous sections, and improve consistency
7. The output should be a complete, improved version of the document
{focus_text}

=== ORIGINAL DOCUMENT ({document_type}) ===

{original_document}

=== QUALITY REVIEW FEEDBACK ===

{quality_feedback}

=== YOUR TASK ===

Generate a complete, improved version of the document that addresses all issues mentioned in the quality feedback. 
The improved document should:
- Be complete (no truncated sections)
- Address all specific issues mentioned in the feedback
- Maintain professional quality and consistency
- Include all necessary details and explanations

Start directly with the improved document content (no preamble):"""
        
        try:
            logger.debug(f"Improving {document_type} document (original: {len(original_document)} chars)")
            improved_doc = self._call_llm(prompt, temperature=0.5)  # Lower temperature for more consistent improvements
            
            # Clean the response
            improved_doc = improved_doc.strip()
            
            # Remove markdown code blocks if present
            if improved_doc.startswith("```"):
                lines = improved_doc.split("\n")
                if len(lines) > 2:
                    improved_doc = "\n".join(lines[1:-1])
            
            logger.debug(f"Improved document generated ({len(improved_doc)} chars)")
            return improved_doc
            
        except Exception as e:
            logger.error(f"Error improving document: {e}")
            raise
    
    def improve_and_save(
        self,
        original_document: str,
        document_type: str,
        quality_feedback: str,
        output_filename: str,
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None,
        agent_type: Optional[AgentType] = None
    ) -> str:
        """
        Improve document and save to file
        
        Args:
            original_document: Original document content
            document_type: Type of document
            quality_feedback: Quality review feedback
            output_filename: Output filename
            project_id: Project ID
            context_manager: Context manager
            agent_type: Agent type for context saving
        
        Returns:
            Path to saved improved document
        """
        logger.info(f"Improving {document_type} based on quality feedback")
        
        # Improve the document
        improved_doc = self.improve_document(original_document, document_type, quality_feedback)
        
        # Save to file (overwrite original)
        file_path = self.file_manager.write_file(output_filename, improved_doc, project_id=project_id)
        logger.info(f"Improved {document_type} saved to: {file_path}")
        
        # Save to context if available
        if project_id and context_manager and agent_type:
            try:
                output = AgentOutput(
                    agent_type=agent_type,
                    document_type=document_type,
                    content=improved_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
                logger.debug(f"Improved {document_type} saved to context")
            except Exception as e:
                logger.warning(f"Could not save improved document to context: {e}")
        
        return file_path

