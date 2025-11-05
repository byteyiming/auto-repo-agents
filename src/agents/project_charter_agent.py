"""
Project Charter Agent (Business Case)
Level 1: Strategic - For Entrepreneurs
Generates Project Charter and Business Case documentation
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_project_charter_prompt
from src.utils.logger import get_logger

logger = get_logger(__name__)


class ProjectCharterAgent(BaseAgent):
    """
    Project Charter Agent (Business Case)
    
    Generates Project Charter and Business Case documentation including:
    - Executive Summary
    - Business Case and ROI analysis
    - Project Objectives
    - Stakeholder Analysis
    - Scope and Boundaries
    - High-Level Timeline
    - Budget and Resources
    - Risks and Mitigation
    - Success Criteria
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
        """Initialize Project Charter Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/charter")
    
    def generate(self, requirements_summary: dict) -> str:
        """
        Generate Project Charter from requirements
        
        Args:
            requirements_summary: Summary from Requirements Analyst
                Should contain: user_idea, project_overview, core_features, business_objectives
        
        Returns:
            Generated Project Charter (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_project_charter_prompt(requirements_summary)
        
        logger.info(f"{self.agent_name} is generating Project Charter (Business Case)...")
        
        stats = self.get_stats()
        
        try:
            charter_doc = self._call_llm(full_prompt)
            logger.info("Project Charter generated successfully")
            logger.info("✅ Project Charter generated!")
            return charter_doc
        except Exception as e:
            logger.error(f"Error generating Project Charter: {str(e)}", exc_info=True)
            logger.error("❌ Error generating Project Charter: {{e}}")
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        output_filename: str = "project_charter.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate Project Charter and save to file
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
        
        Returns:
            Absolute path to saved file
        """
        logger.info(f"Starting Project Charter generation for: {output_filename}")
        # Generate documentation
        charter_doc = self.generate(requirements_summary)
        logger.debug(f"Project Charter document generated (length: {len(charter_doc)} characters)")
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, charter_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            logger.info(f"Project Charter saved: {file_path} (size: {file_size} bytes)")
            logger.info("✅ File written successfully to {{file_path}}")
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.PROJECT_CHARTER,
                    document_type="project_charter",
                    content=charter_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
                logger.info(f"Project Charter saved to shared context (project: {project_id})")
                logger.info("✅ Project Charter saved to shared context (project: {{project_id}})")
            
            return file_path
        except Exception as e:
            logger.error(f"Error writing Project Charter file: {str(e)}", exc_info=True)
            logger.error("❌ Error writing file: {{e}}")
            raise

