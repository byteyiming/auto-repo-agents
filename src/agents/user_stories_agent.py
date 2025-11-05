"""
User Stories Agent
Level 2: Product - For Product Managers
Generates User Stories and Epics documentation
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_user_stories_prompt
from src.utils.logger import get_logger

logger = get_logger(__name__)


class UserStoriesAgent(BaseAgent):
    """
    User Stories Agent
    
    Generates User Stories and Epics documentation including:
    - Epics Overview
    - User Stories by Epic
    - User Stories Detail (with acceptance criteria)
    - User Story Mapping
    - Backlog Organization
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
        """Initialize User Stories Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/user_stories")
    
    def generate(self, requirements_summary: dict, project_charter_summary: Optional[str] = None) -> str:
        """
        Generate User Stories from requirements and project charter
        
        Args:
            requirements_summary: Summary from Requirements Analyst
                Should contain: user_idea, project_overview, core_features, user_personas
            project_charter_summary: Optional Project Charter content (Level 1 output)
        
        Returns:
            Generated User Stories document (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_user_stories_prompt(requirements_summary, project_charter_summary)
        
        logger.info(f"{self.agent_name} is generating User Stories and Epics...")
        
        stats = self.get_stats()
        
        try:
            user_stories_doc = self._call_llm(full_prompt)
            logger.info("User Stories generated successfully")
            logger.info("✅ User Stories generated!")
            return user_stories_doc
        except Exception as e:
            logger.error(f"Error generating User Stories: {str(e)}", exc_info=True)
            logger.error("❌ Error generating User Stories: {{e}}")
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        project_charter_summary: Optional[str] = None,
        output_filename: str = "user_stories.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate User Stories and save to file
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
        
        Returns:
            Absolute path to saved file
        """
        logger.info(f"Starting User Stories generation for: {output_filename}")
        # Generate documentation
        user_stories_doc = self.generate(requirements_summary, project_charter_summary)
        logger.debug(f"User Stories document generated (length: {len(user_stories_doc)} characters)")
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, user_stories_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            logger.info(f"User Stories saved: {file_path} (size: {file_size} bytes)")
            logger.info("✅ File written successfully to {{file_path}}")
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.USER_STORIES,
                    document_type="user_stories",
                    content=user_stories_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
                logger.info(f"User Stories saved to shared context (project: {project_id})")
                logger.info("✅ User Stories saved to shared context (project: {{project_id}})")
            
            return file_path
        except Exception as e:
            logger.error(f"Error writing User Stories file: {str(e)}", exc_info=True)
            logger.error("❌ Error writing file: {{e}}")
            raise

