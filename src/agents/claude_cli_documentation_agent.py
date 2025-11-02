"""
Claude CLI Documentation Agent
Generates a consolidated markdown file (claude.md) optimized for Claude CLI
to read and use for coding tasks based on all generated documentation.
"""
from typing import Optional, Dict
from datetime import datetime
from src.agents.base_agent import BaseAgent
from src.utils.file_manager import FileManager
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, AgentOutput
from src.rate_limit.queue_manager import RequestQueue
from prompts.system_prompts import get_claude_cli_prompt


class ClaudeCLIDocumentationAgent(BaseAgent):
    """
    Claude CLI Documentation Agent
    
    Generates a comprehensive claude.md file that consolidates:
    - Requirements and project overview
    - Technical architecture and design decisions
    - API endpoints and data models
    - Developer setup and workflow
    - Code examples and patterns
    - Testing strategies
    - Key implementation details
    
    Formatted specifically for Claude CLI to parse and use for coding tasks.
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
        """Initialize Claude CLI Documentation Agent"""
        super().__init__(
            provider_name=provider_name,
            model_name=model_name,
            rate_limiter=rate_limiter,
            api_key=api_key,
            **provider_kwargs
        )
        
        self.file_manager = file_manager or FileManager(base_dir="docs")
    
    def generate(
        self,
        all_documentation: Dict[AgentType, str],
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate claude.md from all documentation
        
        Args:
            all_documentation: Dict mapping agent types to their document content
            project_id: Optional project ID for context
            context_manager: Optional context manager
        
        Returns:
            Generated claude.md content
        """
        # Build comprehensive context from all documents
        context_summary = self._build_context_summary(all_documentation)
        
        # Create prompt for Claude CLI documentation
        system_prompt = get_claude_cli_prompt()
        
        user_prompt = f"""Based on all the generated documentation below, create a comprehensive claude.md file optimized for Claude CLI to read and use for coding tasks.

All Available Documentation:
{context_summary}

Generate the complete claude.md file now:"""

        print(f"🤖 ClaudeCLIDocumentationAgent is generating claude.md...")
        print(f"⏳ This may take a moment (rate limited)...")
        
        # Call LLM to generate claude.md
        claude_md_content = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt
        )
        
        return claude_md_content
    
    def _build_context_summary(self, all_documentation: Dict[AgentType, str]) -> str:
        """
        Build a comprehensive summary from all documentation
        
        Args:
            all_documentation: Dict of all documents
        
        Returns:
            Formatted summary string
        """
        summary_parts = []
        
        # Document type names
        doc_names = {
            AgentType.REQUIREMENTS_ANALYST: "Requirements Document",
            AgentType.PM_DOCUMENTATION: "Project Management Plan",
            AgentType.TECHNICAL_DOCUMENTATION: "Technical Specification",
            AgentType.API_DOCUMENTATION: "API Documentation",
            AgentType.DEVELOPER_DOCUMENTATION: "Developer Guide",
            AgentType.STAKEHOLDER_COMMUNICATION: "Stakeholder Summary",
            AgentType.USER_DOCUMENTATION: "User Guide",
            AgentType.TEST_DOCUMENTATION: "Test Plan",
            AgentType.QUALITY_REVIEWER: "Quality Review",
        }
        
        # Include full content (not truncated) for comprehensive claude.md
        for agent_type, content in all_documentation.items():
            doc_name = doc_names.get(agent_type, agent_type.value)
            summary_parts.append(f"\n## {doc_name}\n\n{content}\n")
        
        return "\n".join(summary_parts)
    
    def generate_and_save(
        self,
        all_documentation: Dict[AgentType, str],
        project_id: Optional[str] = None,
        context_manager: Optional[ContextManager] = None
    ) -> str:
        """
        Generate and save claude.md file
        
        Args:
            all_documentation: Dict of all documents
            project_id: Optional project ID
            context_manager: Optional context manager
        
        Returns:
            Path to saved claude.md file
        """
        # Generate claude.md content
        claude_md_content = self.generate(
            all_documentation=all_documentation,
            project_id=project_id,
            context_manager=context_manager
        )
        
        # Apply template if available
        if hasattr(self, 'template_engine') and self.template_engine:
            try:
                claude_md_content = self.template_engine.render_template(
                    "claude_cli_documentation.md",
                    {"content": claude_md_content}
                )
            except Exception:
                # Template not found or error, use raw content
                pass
        
        # Save to file
        file_path = self.file_manager.write_file("claude.md", claude_md_content)
        
        print(f"✅ Claude CLI documentation generated!")
        print(f"✅ File written successfully to {file_path}")
        print(f"📄 File saved: claude.md ({len(claude_md_content)} bytes)")
        
        # Save to context if available
        if project_id and context_manager:
            output = AgentOutput(
                agent_type=AgentType.CLAUDE_CLI_DOCUMENTATION,
                document_type="claude_cli_documentation",
                content=claude_md_content,
                file_path=file_path,
                status=DocumentStatus.COMPLETE,
                generated_at=datetime.now()
            )
            context_manager.save_agent_output(project_id, output)
            print(f"✅ Claude CLI documentation saved to shared context (project: {project_id})")
        
        return file_path

