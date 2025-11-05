"""
Database Schema Agent
Level 3: Technical - For Programmers
Generates Database Schema documentation
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_database_schema_prompt
from src.utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseSchemaAgent(BaseAgent):
    """
    Database Schema Agent
    
    Generates Database Schema documentation including:
    - Database Overview
    - Entity Relationship Diagram (ERD)
    - Database Tables with detailed columns
    - Data Models
    - Indexes and Performance
    - Database Migrations
    - Data Integrity
    - Security and Access Control
    - Database Scripts (CREATE TABLE, etc.)
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
        """Initialize Database Schema Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/database")
    
    def generate(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None
    ) -> str:
        """
        Generate Database Schema from requirements and technical specs
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
        
        Returns:
            Generated Database Schema document (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_database_schema_prompt(requirements_summary, technical_summary)
        
        logger.info(f"{self.agent_name} is generating Database Schema...")
        
        stats = self.get_stats()
        
        try:
            schema_doc = self._call_llm(full_prompt)
            logger.info("Database Schema generated successfully")
            logger.info("✅ Database Schema generated!")
            return schema_doc
        except Exception as e:
            logger.error(f"Error generating Database Schema: {str(e)}", exc_info=True)
            logger.error("❌ Error generating Database Schema: {{e}}")
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None,
        output_filename: str = "database_schema.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate Database Schema and save to file
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
        
        Returns:
            Absolute path to saved file
        """
        logger.info(f"Starting Database Schema generation for: {output_filename}")
        # Generate documentation
        schema_doc = self.generate(requirements_summary, technical_summary)
        logger.debug(f"Database Schema document generated (length: {len(schema_doc)} characters)")
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, schema_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            logger.info(f"Database Schema saved: {file_path} (size: {file_size} bytes)")
            logger.info("✅ File written successfully to {{file_path}}")
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.DATABASE_SCHEMA,
                    document_type="database_schema",
                    content=schema_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
                logger.info(f"Database Schema saved to shared context (project: {project_id})")
                logger.info("✅ Database Schema saved to shared context (project: {{project_id}})")
            
            return file_path
        except Exception as e:
            logger.error(f"Error writing Database Schema file: {str(e)}", exc_info=True)
            logger.error("❌ Error writing file: {{e}}")
            raise

