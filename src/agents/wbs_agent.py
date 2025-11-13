"""
Work Breakdown Structure (WBS) Agent
Generates detailed work breakdown structure for project planning
"""
from typing import Optional
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_wbs_prompt


class WBSAgent(BaseAgent):
    """
    Work Breakdown Structure Agent
    
    Generates detailed WBS documentation including:
    - Hierarchical task breakdown
    - Work packages and deliverables
    - Task dependencies and sequencing
    - Resource allocation
    - Time estimates
    - Milestones and checkpoints
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
        """Initialize WBS Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs/pm")
    
    def generate(
        self,
        requirements_summary: dict,
        project_charter_summary: Optional[str] = None,
        pm_summary: Optional[str] = None
    ) -> str:
        """
        Generate WBS documentation from requirements, project charter, and PM plan
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            project_charter_summary: Optional Project Charter content
            pm_summary: Optional PM documentation content
        
        Returns:
            Generated WBS documentation (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_wbs_prompt(requirements_summary, project_charter_summary, pm_summary)
        
        try:
            wbs_doc = self._call_llm(full_prompt)
            return wbs_doc
        except Exception as e:
            raise
    
    async def async_generate(
        self,
        requirements_summary: dict,
        project_charter_summary: Optional[str] = None,
        pm_summary: Optional[str] = None
    ) -> str:
        """
        Generate WBS documentation (async)
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            project_charter_summary: Optional Project Charter content
            pm_summary: Optional PM documentation content
        
        Returns:
            Generated WBS documentation (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_wbs_prompt(requirements_summary, project_charter_summary, pm_summary)
        
        try:
            wbs_doc = await self._async_call_llm(full_prompt)
            return wbs_doc
        except Exception as e:
            raise
    
    def generate_and_save(
        self,
        requirements_summary: dict,
        project_charter_summary: Optional[str] = None,
        pm_summary: Optional[str] = None,
        output_filename: str = "work_breakdown_structure.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate WBS documentation and save to file (sync version)
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            project_charter_summary: Optional Project Charter content
            pm_summary: Optional PM documentation content
            output_filename: Output filename
            project_id: Project ID for context
            context_manager: Context manager for saving output
        
        Returns:
            File path of saved document
        """
        # Generate WBS documentation
        wbs_content = self.generate(requirements_summary, project_charter_summary, pm_summary)
        
        # Save to file
        file_path = self.file_manager.write_file(output_filename, wbs_content)
        
        # Save to context if provided
        if context_manager and project_id:
            output = AgentOutput(
                agent_type=AgentType.WBS_AGENT,
                document_type="work_breakdown_structure",
                content=wbs_content,
                file_path=file_path,
                status=DocumentStatus.COMPLETE,
                generated_at=datetime.now()
            )
            context_manager.save_agent_output(project_id, output)
        
        return file_path
    
    async def async_generate_and_save(
        self,
        requirements_summary: dict,
        project_charter_summary: Optional[str] = None,
        pm_summary: Optional[str] = None,
        output_filename: str = "work_breakdown_structure.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate WBS documentation and save to file (async version)
        
        Args:
            requirements_summary: Summary from Requirements Analyst
            project_charter_summary: Optional Project Charter content
            pm_summary: Optional PM documentation content
            output_filename: Output filename
            project_id: Project ID for context
            context_manager: Context manager for saving output
        
        Returns:
            File path of saved document
        """
        # Generate WBS documentation (async)
        wbs_content = await self.async_generate(requirements_summary, project_charter_summary, pm_summary)
        
        # Save to file (can be async in future, but FileManager is sync for now)
        import asyncio
        loop = asyncio.get_event_loop()
        file_path = await loop.run_in_executor(
            None,
            lambda: self.file_manager.write_file(output_filename, wbs_content)
        )
        
        # Save to context if provided
        if context_manager and project_id:
            output = AgentOutput(
                agent_type=AgentType.WBS_AGENT,
                document_type="work_breakdown_structure",
                content=wbs_content,
                file_path=file_path,
                status=DocumentStatus.COMPLETE,
                generated_at=datetime.now()
            )
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: context_manager.save_agent_output(project_id, output)
            )
        
        return file_path

