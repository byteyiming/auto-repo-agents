"""
Requirements Analyst Agent
Uses OOP structure with BaseAgent inheritance
"""
from typing import Optional
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.rate_limit.queue_manager import RequestQueue
from src.context.context_manager import ContextManager
from src.context.shared_context import RequirementsDocument, AgentType, DocumentStatus, AgentOutput
from prompts.system_prompts import get_requirements_prompt
from pathlib import Path


class RequirementsAnalyst(BaseAgent):
    """
    Requirements Analyst Agent
    
    Analyzes user ideas and generates structured requirements documents
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
        """
        Initialize Requirements Analyst
        
        Args:
            provider_name: LLM provider name ("gemini", "openai", etc.) - defaults to env var or "gemini"
            model_name: Model name override (provider-specific)
            rate_limiter: Shared rate limiter (optional)
            file_manager: File manager instance (optional)
            api_key: API key (optional, loads from env vars if not provided)
            **provider_kwargs: Additional provider-specific configuration
        
        Examples:
            >>> # Use default Gemini
            >>> agent = RequirementsAnalyst()
            
            >>> # Use OpenAI
            >>> agent = RequirementsAnalyst(provider_name="openai")
            
            >>> # Use specific GPT model
            >>> agent = RequirementsAnalyst(
            ...     provider_name="openai",
            ...     default_model="gpt-4o"
            ... )
        """
        # Initialize base agent with provider support
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        # Initialize file manager
        self.file_manager = file_manager or FileManager(base_dir="docs")
        
        # Context manager (optional, will be set when project_id is provided)
        self.context_manager: Optional[ContextManager] = None
        self.project_id: Optional[str] = None
    
    def generate(self, user_idea: str) -> str:
        """
        Generate requirements document from user idea
        
        Args:
            user_idea: User's project idea/requirement
            
        Returns:
            Generated requirements document (Markdown)
        """
        # Get prompt from centralized prompts config
        full_prompt = get_requirements_prompt(user_idea)
        
        print(f"🤖 {self.agent_name} is analyzing: '{user_idea}'...")
        print("⏳ This may take a moment (rate limited to stay within free tier)...")
        
        # Check rate limit stats
        stats = self.get_stats()
        print(f"📊 Rate limit status: {stats['requests_in_window']}/{stats['max_rate']} requests in window")
        
        try:
            requirements_doc = self._call_llm(full_prompt)
            print("✅ Requirements document generated!")
            return requirements_doc
        except Exception as e:
            print(f"❌ Error generating requirements: {e}")
            raise
    
    def generate_and_save(
        self,
        user_idea: str,
        output_filename: str = "requirements.md",
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate requirements and save to file
        
        Args:
            user_idea: User's project idea
            output_filename: Filename to save (will be saved in base_dir)
            project_id: Optional project ID for context sharing
            context_manager: Optional context manager for saving to shared context
            
        Returns:
            Absolute path to saved file
        """
        # Store context info if provided
        if project_id and context_manager:
            self.project_id = project_id
            self.context_manager = context_manager
        
        # Generate requirements
        requirements_doc = self.generate(user_idea)
        
        # Save to file
        try:
            file_path = self.file_manager.write_file(output_filename, requirements_doc)
            file_size = self.file_manager.get_file_size(output_filename)
            print(f"✅ File written successfully to {file_path}")
            print(f"📄 File saved: {output_filename} ({file_size} bytes)")
            
            # Save to context if available (with improved parsing)
            if self.project_id and self.context_manager:
                self._save_to_context(requirements_doc, file_path, user_idea)
            
            return file_path
        except Exception as e:
            print(f"❌ Error writing file: {e}")
            raise
    
    def _save_to_context(self, requirements_doc: str, file_path: str, user_idea: str):
        """Save requirements to shared context with intelligent parsing"""
        if not self.project_id or not self.context_manager:
            return

        try:
            # Create project if it doesn't exist
            self.context_manager.create_project(self.project_id, user_idea)

            # Parse requirements document intelligently
            req_doc = self.parser.parse_markdown(requirements_doc, user_idea)

            # Save parsed requirements to context
            self.context_manager.save_requirements(self.project_id, req_doc)

            # Save agent output
            output = AgentOutput(
                agent_type=AgentType.REQUIREMENTS_ANALYST,
                document_type="requirements",
                content=requirements_doc,
                file_path=file_path,
                status=DocumentStatus.COMPLETE
            )
            self.context_manager.save_agent_output(self.project_id, output)

            print(f"✅ Requirements parsed and saved to shared context (project: {self.project_id})")
            print(f"   📊 Extracted: {len(req_doc.core_features)} features, "
                  f"{len(req_doc.user_personas)} personas, "
                  f"{len(req_doc.business_objectives)} objectives")
        except Exception as e:
            print(f"⚠️  Warning: Could not save to context: {e}")
            import traceback
            traceback.print_exc()
