"""
API Documentation Agent
Generates comprehensive API documentation
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_api_prompt


class APIDocumentationAgent(BaseAgent):
    """
    API Documentation Agent
    
    Generates API documentation including:
    - API overview and versioning
    - Authentication methods
    - All endpoints with examples
    - Data models and schemas
    - Rate limiting
    - Error handling
    - SDKs and code examples
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
        """Initialize API Documentation Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/api")
    
    def generate(
        self, 
        requirements_summary: dict, 
        technical_summary: Optional[str] = None,
        database_schema_summary: Optional[str] = None
    ) -> str:
        """
        Generate API documentation from requirements and technical specs
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            database_schema_summary: Optional database schema summary with detailed SQL schemas
        
        Returns:
            Generated API documentation (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_api_prompt(requirements_summary, technical_summary, database_schema_summary)
        
        try:
            api_doc = self._call_llm(full_prompt)
            return api_doc
        except Exception as e:
            raise
    
    async def async_generate(
        self, 
        requirements_summary: dict, 
        technical_summary: Optional[str] = None,
        database_schema_summary: Optional[str] = None
    ) -> str:
        """
        Generate API documentation from requirements and technical specs (async)
        
        Overrides base class to use native async LLM calls for better performance.
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            database_schema_summary: Optional database schema summary with detailed SQL schemas
        
        Returns:
            Generated API documentation (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_api_prompt(requirements_summary, technical_summary, database_schema_summary)
        
        try:
            # Use async LLM call for better performance
            api_doc = await self._async_call_llm(full_prompt)
            return api_doc
        except Exception as e:
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None,
        database_schema_summary: Optional[str] = None,
        output_filename: str = "api_documentation.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate API documentation and save to file (sync version)
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            database_schema_summary: Optional database schema summary with detailed SQL schemas
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
            
        Returns:
            Absolute path to saved file
        """
        # Generate documentation
        api_doc = self.generate(requirements_summary, technical_summary, database_schema_summary)
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, api_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            
            # Save to context if available
            if project_id and context_manager:
                output = AgentOutput(
                    agent_type=AgentType.API_DOCUMENTATION,
                    document_type="api_documentation",
                    content=api_doc,
                    file_path=file_path,
                    status=DocumentStatus.COMPLETE,
                    generated_at=datetime.now()
                )
                context_manager.save_agent_output(project_id, output)
            
            return file_path
        except Exception as e:
            raise
    
    async def async_generate_and_save(
        self,
        requirements_summary: dict,
        technical_summary: Optional[str] = None,
        database_schema_summary: Optional[str] = None,
        output_filename: str = "api_documentation.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate API documentation and save to file (async version)
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            technical_summary: Optional technical documentation summary
            database_schema_summary: Optional database schema summary with detailed SQL schemas
            output_filename: Filename to save
            project_id: Project ID for context sharing
            context_manager: Context manager for saving
            
        Returns:
            Absolute path to saved file
        """
        import asyncio
        # Generate documentation (async)
        api_doc = await self.async_generate(requirements_summary, technical_summary, database_schema_summary)
        
        # Save to file (file I/O is fast, but we can make it async too if needed)
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(
            None,
            lambda: self.file_manager.write_file(output_filename, api_doc)
        )
        
        # Save to context (async)
        if project_id and context_manager:
            output = AgentOutput(
                agent_type=AgentType.API_DOCUMENTATION,
                document_type="api_documentation",
                content=api_doc,
                file_path=file_path,
                status=DocumentStatus.COMPLETE,
                generated_at=datetime.now()
            )
        await loop.run_in_executor(
            None,
            lambda: context_manager.save_agent_output(project_id, output)
        )
        
        return file_path

