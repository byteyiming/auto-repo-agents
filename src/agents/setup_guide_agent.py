"""
Setup Guide Agent (Developer Setup Guide)
Level 3: Technical - For Programmers
Generates comprehensive setup and installation guides
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_setup_guide_prompt
from src.utils.logger import get_logger

logger = get_logger(__name__)


class SetupGuideAgent(BaseAgent):
    """
    Setup Guide Agent (Developer Setup Guide)
    
    Generates comprehensive setup and installation guides including:
    - Prerequisites
    - Installation Steps
    - Development Environment Setup
    - Database Setup
    - Running the Application
    - Project Structure
    - Configuration
    - Verification
    - Common Issues and Troubleshooting
    - Next Steps
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
        """Initialize Setup Guide Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/setup")
    
    def generate(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None,
        api_summary: Optional[str] = None
    ) -> str:
        """
        Generate Setup Guide from requirements and technical specs
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            api_summary: Optional API documentation summary
        
        Returns:
            Generated Setup Guide (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_setup_guide_prompt(requirements_summary, technical_summary, api_summary)
        
        logger.info(f"{self.agent_name} is generating Setup Guide...")
        
        stats = self.get_stats()
        
        try:
            setup_doc = self._call_llm(full_prompt)
            logger.info("Setup Guide generated successfully")
            logger.info("✅ Setup Guide generated!")
            return setup_doc
        except Exception as e:
            logger.error(f"Error generating Setup Guide: {str(e)}", exc_info=True)
            logger.error("❌ Error generating Setup Guide: {{e}}")
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None,
        api_summary: Optional[str] = None,
        output_filename: str = "setup_guide.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate Setup Guide and save to file
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            api_summary: Optional API documentation summary
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
        
        Returns:
            Absolute path to saved file
        """
        logger.info(f"Starting Setup Guide generation for: {output_filename}")
        # Generate documentation
        setup_doc = self.generate(requirements_summary, technical_summary, api_summary)
        logger.debug(f"Setup Guide document generated (length: {len(setup_doc)} characters)")
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, setup_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            logger.info(f"Setup Guide saved: {file_path} (size: {file_size} bytes)")
            logger.info("✅ File written successfully to {{file_path}}")
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.SETUP_GUIDE,
                    document_type="setup_guide",
                    content=setup_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
                logger.info(f"Setup Guide saved to shared context (project: {project_id})")
                logger.info("✅ Setup Guide saved to shared context (project: {{project_id}})")
            
            return file_path
        except Exception as e:
            logger.error(f"Error writing Setup Guide file: {str(e)}", exc_info=True)
            logger.error("❌ Error writing file: {{e}}")
            raise

