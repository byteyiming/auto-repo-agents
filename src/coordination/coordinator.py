"""
Workflow Coordinator
Orchestrates multi-agent documentation generation workflow
"""
from typing import Optional, Dict, List
from datetime import datetime
from pathlib import Path
import uuid
import os
import re

from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType, DocumentStatus, SharedContext, AgentOutput
from src.utils.logger import get_logger
from src.config.settings import get_settings, get_environment

logger = get_logger(__name__)
from src.agents.requirements_analyst import RequirementsAnalyst
from src.agents.pm_documentation_agent import PMDocumentationAgent
from src.agents.technical_documentation_agent import TechnicalDocumentationAgent
from src.agents.api_documentation_agent import APIDocumentationAgent
from src.agents.developer_documentation_agent import DeveloperDocumentationAgent
from src.agents.stakeholder_communication_agent import StakeholderCommunicationAgent
from src.agents.user_documentation_agent import UserDocumentationAgent
from src.agents.test_documentation_agent import TestDocumentationAgent
from src.agents.quality_reviewer_agent import QualityReviewerAgent
from src.agents.format_converter_agent import FormatConverterAgent
from src.agents.claude_cli_documentation_agent import ClaudeCLIDocumentationAgent
from src.agents.project_charter_agent import ProjectCharterAgent
from src.agents.user_stories_agent import UserStoriesAgent
from src.agents.database_schema_agent import DatabaseSchemaAgent
from src.agents.setup_guide_agent import SetupGuideAgent
from src.agents.marketing_plan_agent import MarketingPlanAgent
from src.agents.business_model_agent import BusinessModelAgent
from src.agents.support_playbook_agent import SupportPlaybookAgent
from src.agents.legal_compliance_agent import LegalComplianceAgent
from src.agents.document_improver_agent import DocumentImproverAgent
from src.agents.code_analyst_agent import CodeAnalystAgent
from src.utils.file_manager import FileManager
from src.utils.cross_referencer import CrossReferencer
from src.utils.parallel_executor import ParallelExecutor, TaskStatus
from src.utils.async_parallel_executor import AsyncParallelExecutor, TaskStatus as AsyncTaskStatus
from src.rate_limit.queue_manager import RequestQueue
from src.utils.document_organizer import format_documents_by_level, get_documents_summary, get_document_level, get_document_display_name
from src.coordination.workflow_dag import (
    get_phase2_tasks_for_profile,
    build_task_dependencies,
    build_kwargs_for_task,
    get_agent_for_task,
    Phase2Task
)
import asyncio


class WorkflowCoordinator:
    """
    Coordinates the multi-agent documentation generation workflow
    
    Workflow:
    1. Requirements Analyst → Requirements Doc
    2. PM Agent → Project Management Docs
    3. (Future: Technical, API, Developer, Stakeholder agents)
    """
    
    def __init__(
        self,
        context_manager: Optional[ContextManager] = None,
        rate_limiter: Optional[RequestQueue] = None,
        provider_name: Optional[str] = None,
        provider_config: Optional[Dict[str, str]] = None
    ):
        """
        Initialize workflow coordinator
        
        NOTE: All agents are FORCED to use Gemini (no local models).
        The provider_name and provider_config parameters are kept for backward compatibility
        but are IGNORED - all agents will use Gemini regardless.
        
        Args:
            context_manager: Context manager instance
            rate_limiter: Shared rate limiter for all agents
            provider_name: (IGNORED - kept for backward compatibility) All agents use "gemini"
            provider_config: (IGNORED - kept for backward compatibility) All agents use "gemini"
        """
        settings = get_settings()
        self.context_manager = context_manager or ContextManager()
        # Use rate limit from settings
        self.rate_limiter = rate_limiter or RequestQueue(
            max_rate=settings.rate_limit_per_minute, 
            period=60
        )
        self.file_manager = FileManager(base_dir=settings.docs_dir)
        logger.info(f"WorkflowCoordinator initialized (environment: {settings.environment.value})")
        
        # FORCE GEMINI FOR ALL AGENTS - NO LOCAL MODELS
        # Override any environment variables or parameters to ensure all agents use Gemini
        default_provider = os.getenv("LLM_PROVIDER") 
        provider_config = provider_config or {}
        
        # Verify Gemini API key is available
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key or gemini_api_key == "":
            logger.warning("⚠️  GEMINI_API_KEY not found. Please set it in .env file.")
            logger.warning("   All agents will use Gemini, but API calls will fail without a valid key.")
        else:
            logger.info("✅ Gemini API key found. All agents will use Gemini.")
        
        # All agents use Gemini (no hybrid mode, no local models, no exceptions)
        logger.info("🚀 FORCED: All agents using Gemini (no local models)")
        if provider_config:
            # Override any custom config to use Gemini
            logger.warning(f"⚠️  Custom provider_config provided: {provider_config}")
            logger.warning("   Overriding to Gemini for all agents (no local models)")
            provider_config = {}  # Clear custom config, force Gemini
        
        # Helper function to get provider for an agent (always returns gemini)
        def get_agent_provider(agent_key: str) -> str:
            """Get provider for a specific agent (always returns gemini - no local models)"""
            # Force Gemini for all agents, ignore any custom config
            return "gemini"
        
        # Initialize agents (shared rate limiter, with optional provider override)
        self.requirements_analyst = RequirementsAnalyst(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("requirements_analyst")
        )
        self.pm_agent = PMDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("pm_agent")
        )
        self.technical_agent = TechnicalDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("technical_agent")
        )
        self.api_agent = APIDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("api_agent")
        )
        self.developer_agent = DeveloperDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("developer_agent")
        )
        self.stakeholder_agent = StakeholderCommunicationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("stakeholder_agent")
        )
        self.user_agent = UserDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("user_agent")
        )
        self.test_agent = TestDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("test_agent")
        )
        self.quality_reviewer = QualityReviewerAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("quality_reviewer")
        )
        self.format_converter = FormatConverterAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("format_converter")
        )
        self.claude_cli_agent = ClaudeCLIDocumentationAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("claude_cli_agent")
        )
        self.cross_referencer = CrossReferencer()
        
        # Level 1: Strategic (Entrepreneur) - New agents
        self.project_charter_agent = ProjectCharterAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("project_charter_agent")
        )
        
        # Level 2: Product (Product Manager) - New agents
        self.user_stories_agent = UserStoriesAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("user_stories_agent")
        )
        
        # Level 3: Technical (Programmer) - New agents
        self.database_schema_agent = DatabaseSchemaAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("database_schema_agent")
        )
        self.setup_guide_agent = SetupGuideAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("setup_guide_agent")
        )
        
        # Business & Marketing agents
        self.marketing_plan_agent = MarketingPlanAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("marketing_plan_agent")
        )
        self.business_model_agent = BusinessModelAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("business_model_agent")
        )
        self.support_playbook_agent = SupportPlaybookAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("support_playbook_agent")
        )
        self.legal_compliance_agent = LegalComplianceAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("legal_compliance_agent")
        )
        
        # Document improvement agent (for auto-fix loop)
        self.document_improver = DocumentImproverAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("document_improver")
        )
        
        # Code Analyst Agent (for code-first workflow)
        self.code_analyst = CodeAnalystAgent(
            rate_limiter=self.rate_limiter,
            provider_name=get_agent_provider("code_analyst"),
            file_manager=self.file_manager
        )
        
        # Log provider configuration
        logger.info("✅ WorkflowCoordinator configured: ALL agents using Gemini (no local models)")
        logger.info("   Provider: gemini (forced, no overrides)")
        logger.info("   Model: gemini-2.0-flash (or GEMINI_DEFAULT_MODEL if set)")
        logger.info("   Local models: DISABLED")
        
        logger.info("WorkflowCoordinator initialized with all agents (ALL using Gemini - no local models)")
    
    def _run_agent_with_quality_loop(
        self,
        agent_instance,
        agent_type: AgentType,
        generate_kwargs: dict,
        output_filename: str,
        project_id: str,
        quality_threshold: float = 80.0
    ) -> tuple:
        """
        Runs an agent, checks its quality, and improves it if below the threshold.
        This implements the "Quality Gate" pattern for foundational documents.
        
        Args:
            agent_instance: Agent instance to run
            agent_type: AgentType enum value
            generate_kwargs: Keyword arguments to pass to agent.generate_and_save()
            output_filename: Output filename
            project_id: Project ID
            quality_threshold: Quality score threshold (default: 80.0)
        
        Returns:
            Tuple of (final_file_path, final_content)
        """
        logger.info(f"🔍 Running Quality Loop for {agent_type.value}...")
        
        # 1. GENERATE V1
        logger.info(f"  📝 Step 1: Generating V1 for {agent_type.value}...")
        try:
            v1_file_path = agent_instance.generate_and_save(
                **generate_kwargs,
                output_filename=output_filename,
                project_id=project_id,
                context_manager=self.context_manager
            )
            v1_content = self.file_manager.read_file(v1_file_path)
            logger.info(f"  ✅ V1 generated: {len(v1_content)} characters")
        except Exception as e:
            logger.error(f"  ❌ V1 generation failed for {agent_type.value}: {e}")
            raise
        
        # 2. CHECK V1 QUALITY
        logger.info(f"  🔍 Step 2: Checking V1 quality for {agent_type.value}...")
        score = 0
        try:
            # Get checklist for this agent type
            checklist = self.quality_reviewer.document_type_checker.get_checklist_for_agent(agent_type)
            
            if checklist:
                # Use document-type-specific quality checker
                quality_result_v1 = self.quality_reviewer.document_type_checker.check_quality_for_type(
                    v1_content,
                    document_type=agent_type.value
                )
                score = quality_result_v1.get("overall_score", 0)
                logger.info(f"  📊 V1 Quality Score: {score:.2f}/100 (threshold: {quality_threshold})")
            else:
                logger.warning(f"  ⚠️  No quality checklist found for {agent_type.value}, using base checker")
                # Fallback to base checker
                quality_result_v1 = self.quality_reviewer.quality_checker.check_quality(v1_content)
                score = quality_result_v1.get("overall_score", 0)
                logger.info(f"  📊 V1 Quality Score: {score:.2f}/100 (threshold: {quality_threshold})")
        except Exception as e:
            logger.warning(f"  ⚠️  Quality check failed for {agent_type.value}: {e}, assuming score 0 to trigger improvement")
            score = 0
        
        # 3. DECIDE AND IMPROVE
        if score >= quality_threshold:
            logger.info(f"  ✅ [{agent_type.value}] V1 quality ({score:.2f}/100) meets threshold ({quality_threshold}). Proceeding.")
            return v1_file_path, v1_content
        else:
            logger.warning(f"  ⚠️  [{agent_type.value}] V1 quality ({score:.2f}/100) is below threshold ({quality_threshold}). Triggering improvement loop...")
            
            # 3a. Get Actionable Feedback
            logger.info(f"  🔍 Step 3a: Generating quality feedback for {agent_type.value}...")
            try:
                feedback_report = self.quality_reviewer.generate(
                    {agent_type.value: v1_content}
                )
                logger.info(f"  ✅ Quality feedback generated: {len(feedback_report)} characters")
            except Exception as e:
                logger.warning(f"  ⚠️  Quality feedback generation failed: {e}, using simplified feedback")
                # Create a simple feedback if generation fails
                feedback_report = f"""
Quality Review for {agent_type.value}:

Current Score: {score:.2f}/100
Threshold: {quality_threshold}

Issues Found:
- Document quality is below the required threshold
- Please improve completeness, clarity, and structure
- Ensure all required sections are present and well-developed

Improvement Suggestions:
- Review and expand missing sections
- Improve clarity and readability
- Add more detailed explanations
- Ensure technical accuracy
"""
            
            # 3b. Improve V1 -> V2
            logger.info(f"  🔧 Step 3b: Improving {agent_type.value} (V1 -> V2)...")
            try:
                v2_file_path = self.document_improver.improve_and_save(
                    original_document=v1_content,
                    document_type=agent_type.value,
                    quality_feedback=feedback_report,
                    output_filename=output_filename,  # Overwrite original file
                    project_id=project_id,
                    context_manager=self.context_manager,
                    agent_type=agent_type
                )
                v2_content = self.file_manager.read_file(v2_file_path)
                logger.info(f"  ✅ V2 (Improved) generated: {len(v2_content)} characters")
                
                # Optionally check V2 quality (for logging)
                try:
                    checklist = self.quality_reviewer.document_type_checker.get_checklist_for_agent(agent_type)
                    if checklist:
                        quality_result_v2 = self.quality_reviewer.document_type_checker.check_quality_for_type(
                            v2_content,
                            document_type=agent_type.value
                        )
                        v2_score = quality_result_v2.get("overall_score", 0)
                        logger.info(f"  📊 V2 Quality Score: {v2_score:.2f}/100 (improvement: +{v2_score - score:.2f})")
                except Exception as e:
                    logger.debug(f"  ⚠️  V2 quality check skipped: {e}")
                
                logger.info(f"  🎉 [{agent_type.value}] Quality loop completed: V1 ({score:.2f}) -> V2 (improved)")
                return v2_file_path, v2_content
            except Exception as e:
                logger.error(f"  ❌ Improvement failed for {agent_type.value}: {e}")
                # If improvement fails, return V1 as fallback
                logger.warning(f"  ⚠️  Falling back to V1 for {agent_type.value}")
                return v1_file_path, v1_content
    
    async def _async_run_agent_with_quality_loop(
        self,
        agent_instance,
        agent_type: AgentType,
        generate_kwargs: dict,
        output_filename: str,
        project_id: str,
        quality_threshold: float = 80.0
    ) -> tuple:
        """
        Runs an agent asynchronously, checks its quality, and improves it if below the threshold.
        Async version of _run_agent_with_quality_loop.
        
        Args:
            agent_instance: Agent instance to run
            agent_type: AgentType enum value
            generate_kwargs: Keyword arguments to pass to agent.generate_and_save()
            output_filename: Output filename
            project_id: Project ID
            quality_threshold: Quality score threshold (default: 80.0)
        
        Returns:
            Tuple of (final_file_path, final_content)
        """
        logger.info(f"🔍 Running Quality Loop (async) for {agent_type.value}...")
        
        # 1. GENERATE V1 (async)
        logger.info(f"  📝 Step 1: Generating V1 (async) for {agent_type.value}...")
        try:
            # Use async_generate if available, otherwise run sync in executor
            if hasattr(agent_instance, 'async_generate'):
                # Try to use async version
                # For generate_and_save, we need to handle file I/O separately
                # For now, run sync version in executor
                loop = asyncio.get_event_loop()
                v1_file_path = await loop.run_in_executor(
                    None,
                    lambda: agent_instance.generate_and_save(
                        **generate_kwargs,
                        output_filename=output_filename,
                        project_id=project_id,
                        context_manager=self.context_manager
                    )
                )
            else:
                # Fallback to sync in executor
                loop = asyncio.get_event_loop()
                v1_file_path = await loop.run_in_executor(
                    None,
                    lambda: agent_instance.generate_and_save(
                        **generate_kwargs,
                        output_filename=output_filename,
                        project_id=project_id,
                        context_manager=self.context_manager
                    )
                )
            
            # Read file (can be async in future, but FileManager is sync for now)
            v1_content = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.file_manager.read_file(v1_file_path)
            )
            logger.info(f"  ✅ V1 generated (async): {len(v1_content)} characters")
        except Exception as e:
            logger.error(f"  ❌ V1 generation failed for {agent_type.value}: {e}")
            raise
        
        # 2. CHECK V1 QUALITY (async)
        logger.info(f"  🔍 Step 2: Checking V1 quality (async) for {agent_type.value}...")
        score = 0
        try:
            loop = asyncio.get_event_loop()
            checklist = await loop.run_in_executor(
                None,
                lambda: self.quality_reviewer.document_type_checker.get_checklist_for_agent(agent_type)
            )
            
            if checklist:
                quality_result_v1 = await loop.run_in_executor(
                    None,
                    lambda: self.quality_reviewer.document_type_checker.check_quality_for_type(
                        v1_content,
                        document_type=agent_type.value
                    )
                )
                score = quality_result_v1.get("overall_score", 0)
                logger.info(f"  📊 V1 Quality Score (async): {score:.2f}/100 (threshold: {quality_threshold})")
            else:
                quality_result_v1 = await loop.run_in_executor(
                    None,
                    lambda: self.quality_reviewer.quality_checker.check_quality(v1_content)
                )
                score = quality_result_v1.get("overall_score", 0)
                logger.info(f"  📊 V1 Quality Score (async): {score:.2f}/100 (threshold: {quality_threshold})")
        except Exception as e:
            logger.warning(f"  ⚠️  Quality check failed for {agent_type.value}: {e}, assuming score 0")
            score = 0
        
        # 3. DECIDE AND IMPROVE (async)
        if score >= quality_threshold:
            logger.info(f"  ✅ [{agent_type.value}] V1 quality ({score:.2f}/100) meets threshold. Proceeding.")
            return v1_file_path, v1_content
        else:
            logger.warning(f"  ⚠️  [{agent_type.value}] V1 quality ({score:.2f}/100) is below threshold. Triggering improvement...")
            
            # 3a. Get Actionable Feedback (async)
            logger.info(f"  🔍 Step 3a: Generating quality feedback (async) for {agent_type.value}...")
            try:
                loop = asyncio.get_event_loop()
                feedback_report = await loop.run_in_executor(
                    None,
                    lambda: self.quality_reviewer.generate({agent_type.value: v1_content})
                )
                logger.info(f"  ✅ Quality feedback generated (async): {len(feedback_report)} characters")
            except Exception as e:
                logger.warning(f"  ⚠️  Quality feedback generation failed: {e}, using simplified feedback")
                feedback_report = f"""
Quality Review for {agent_type.value}:

Current Score: {score:.2f}/100
Threshold: {quality_threshold}

Issues Found:
- Document quality is below the required threshold
- Please improve completeness, clarity, and structure
- Ensure all required sections are present and well-developed

Improvement Suggestions:
- Review and expand missing sections
- Improve clarity and readability
- Add more detailed explanations
- Ensure technical accuracy
"""
            
            # 3b. Improve V1 -> V2 (async)
            logger.info(f"  🔧 Step 3b: Improving {agent_type.value} (V1 -> V2, async)...")
            try:
                loop = asyncio.get_event_loop()
                v2_file_path = await loop.run_in_executor(
                    None,
                    lambda: self.document_improver.improve_and_save(
                        original_document=v1_content,
                        document_type=agent_type.value,
                        quality_feedback=feedback_report,
                        output_filename=output_filename,
                        project_id=project_id,
                        context_manager=self.context_manager,
                        agent_type=agent_type
                    )
                )
                v2_content = await loop.run_in_executor(
                    None,
                    lambda: self.file_manager.read_file(v2_file_path)
                )
                logger.info(f"  ✅ V2 (Improved, async) generated: {len(v2_content)} characters")
                
                # Optionally check V2 quality
                try:
                    checklist = await loop.run_in_executor(
                        None,
                        lambda: self.quality_reviewer.document_type_checker.get_checklist_for_agent(agent_type)
                    )
                    if checklist:
                        quality_result_v2 = await loop.run_in_executor(
                            None,
                            lambda: self.quality_reviewer.document_type_checker.check_quality_for_type(
                                v2_content,
                                document_type=agent_type.value
                            )
                        )
                        v2_score = quality_result_v2.get("overall_score", 0)
                        logger.info(f"  📊 V2 Quality Score (async): {v2_score:.2f}/100 (improvement: +{v2_score - score:.2f})")
                except Exception as e:
                    logger.debug(f"  ⚠️  V2 quality check skipped: {e}")
                
                logger.info(f"  🎉 [{agent_type.value}] Quality loop completed (async): V1 ({score:.2f}) -> V2 (improved)")
                return v2_file_path, v2_content
            except Exception as e:
                logger.error(f"  ❌ Improvement failed for {agent_type.value}: {e}")
                logger.warning(f"  ⚠️  Falling back to V1 for {agent_type.value}")
                return v1_file_path, v1_content
    
    def _generate_technical_doc(self, req_summary, project_id):
        """Helper for parallel technical doc generation"""
        return self.technical_agent.generate_and_save(
            requirements_summary=req_summary,
            output_filename="technical_spec.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def _generate_stakeholder_doc(self, req_summary, pm_path, project_id):
        """Helper for parallel stakeholder doc generation"""
        pm_summary = self._get_summary_from_file(pm_path)
        return self.stakeholder_agent.generate_and_save(
            requirements_summary=req_summary,
            pm_summary=pm_summary,
            output_filename="stakeholder_summary.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def _generate_user_doc(self, req_summary, project_id):
        """Helper for parallel user doc generation"""
        return self.user_agent.generate_and_save(
            requirements_summary=req_summary,
            output_filename="user_guide.md",
            project_id=project_id,
            context_manager=self.context_manager
        )
    
    def generate_all_docs(
        self,
        user_idea: str,
        project_id: Optional[str] = None,
        profile: str = "team",
        codebase_path: Optional[str] = None
    ) -> Dict:
        """
        Generate all documentation types from a user idea using HYBRID workflow:
        - Phase 1: Foundational documents with Quality Gate (iterative improvement)
        - Phase 2: Secondary documents in parallel (fast execution)
        - Phase 3: Final packaging (cross-ref, review, convert)
        - Phase 4: Code analysis and documentation update (optional, if codebase_path provided)
        
        Args:
            user_idea: User's project idea
            project_id: Optional project ID (generates one if not provided)
            profile: "team" or "individual" - determines which docs to generate
            codebase_path: Optional path to codebase directory. If provided, Phase 4 will:
                         - Analyze the codebase
                         - Update API and Developer documentation to match actual code
                         - Ensure documentation accuracy
        
        Returns:
            Dict with generated file paths and status
        """
        # --- SETUP ---
        if not project_id:
            project_id = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"🚀 Starting HYBRID Workflow - Project ID: {project_id}, Profile: {profile}")
        
        results = {
            "project_id": project_id,
            "user_idea": user_idea,
            "profile": profile,
            "files": {},
            "status": {}
        }
        
        # Store final, high-quality document content
        final_docs = {}
        document_file_paths = {}
        
        try:
            # --- PHASE 1: FOUNDATIONAL DOCUMENTS (Iterative Quality Loop) ---
            logger.info("=" * 80)
            logger.info("--- PHASE 1: Generating Foundational Documents (Quality Gate) ---")
            logger.info("=" * 80)
            
            # 1. REQUIREMENTS (with quality gate)
            req_path, req_content = self._run_agent_with_quality_loop(
                agent_instance=self.requirements_analyst,
                agent_type=AgentType.REQUIREMENTS_ANALYST,
                generate_kwargs={"user_idea": user_idea},
                output_filename="requirements/requirements.md",
                project_id=project_id,
                quality_threshold=80.0
            )
            results["files"]["requirements"] = req_path
            results["status"]["requirements"] = "complete_v2"
            final_docs[AgentType.REQUIREMENTS_ANALYST] = req_content
            document_file_paths[AgentType.REQUIREMENTS_ANALYST] = req_path
            
            # Get requirements summary from context
            context = self.context_manager.get_shared_context(project_id)
            if not context.requirements:
                raise ValueError("Requirements not found in context after generation")
            
            req_summary = context.get_requirements_summary()
            
            # 2. PROJECT CHARTER (Team only, with quality gate)
            charter_content = None
            if profile == "team":
                charter_path, charter_content = self._run_agent_with_quality_loop(
                    agent_instance=self.project_charter_agent,
                    agent_type=AgentType.PROJECT_CHARTER,
                    generate_kwargs={"requirements_summary": req_summary},
                    output_filename="charter/project_charter.md",
                    project_id=project_id,
                    quality_threshold=75.0
                )
                results["files"]["project_charter"] = charter_path
                results["status"]["project_charter"] = "complete_v2"
                final_docs[AgentType.PROJECT_CHARTER] = charter_content
                document_file_paths[AgentType.PROJECT_CHARTER] = charter_path
            else:
                results["status"]["project_charter"] = "skipped"
            
            # 3. USER STORIES (with quality gate)
            user_stories_output = self.context_manager.get_agent_output(project_id, AgentType.PROJECT_CHARTER)
            charter_summary_for_stories = user_stories_output.content if user_stories_output else charter_content
            
            stories_path, stories_content = self._run_agent_with_quality_loop(
                agent_instance=self.user_stories_agent,
                agent_type=AgentType.USER_STORIES,
                generate_kwargs={
                    "requirements_summary": req_summary,
                    "project_charter_summary": charter_summary_for_stories
                },
                output_filename="user_stories/user_stories.md",
                project_id=project_id,
                quality_threshold=75.0
            )
            results["files"]["user_stories"] = stories_path
            results["status"]["user_stories"] = "complete_v2"
            final_docs[AgentType.USER_STORIES] = stories_content
            document_file_paths[AgentType.USER_STORIES] = stories_path
            
            # 4. TECHNICAL DOCUMENTATION (with quality gate)
            # Note: PM documentation is generated in Phase 2, so we don't have it here
            # Technical doc can be generated without PM summary (it's optional)
            user_stories_output = self.context_manager.get_agent_output(project_id, AgentType.USER_STORIES)
            user_stories_summary = user_stories_output.content if user_stories_output else stories_content
            
            # PM summary is not available in Phase 1 (it's generated in Phase 2)
            # Technical documentation can work without it
            pm_summary_for_tech = None
            
            tech_path, tech_content = self._run_agent_with_quality_loop(
                agent_instance=self.technical_agent,
                agent_type=AgentType.TECHNICAL_DOCUMENTATION,
                generate_kwargs={
                    "requirements_summary": req_summary,
                    "user_stories_summary": user_stories_summary,
                    "pm_summary": pm_summary_for_tech  # None - PM doc is generated in Phase 2
                },
                output_filename="technical/technical_spec.md",
                project_id=project_id,
                quality_threshold=70.0  # Technical docs threshold can be slightly lower
            )
            results["files"]["technical_documentation"] = tech_path
            results["status"]["technical_documentation"] = "complete_v2"
            final_docs[AgentType.TECHNICAL_DOCUMENTATION] = tech_content
            document_file_paths[AgentType.TECHNICAL_DOCUMENTATION] = tech_path
            
            logger.info("=" * 80)
            logger.info("✅ PHASE 1 COMPLETE: Foundational documents generated with quality gates")
            logger.info("=" * 80)
            
            # Get technical summary for Phase 2
            technical_summary = tech_content
            
            # --- PHASE 2: PARALLEL GENERATION (DAG-based) ---
            logger.info("=" * 80)
            logger.info("--- PHASE 2: Generating Secondary Documents (Parallel DAG) ---")
            logger.info("=" * 80)
            
            # Get Phase 2 task configurations from DAG
            phase2_tasks = get_phase2_tasks_for_profile(profile=profile)
            logger.info(f"📋 Phase 2 DAG: {len(phase2_tasks)} tasks for profile '{profile}'")
            
            # Build dependency map (AgentType -> task_id dependencies)
            dependency_map = build_task_dependencies(phase2_tasks)
            
            # Prepare Phase 1 content for dependency extraction
            # Phase 1 documents are already complete, so we can use their content directly
            phase1_deps_content = {
                AgentType.REQUIREMENTS_ANALYST: req_content,
                AgentType.TECHNICAL_DOCUMENTATION: technical_summary,
                AgentType.PROJECT_CHARTER: charter_content if charter_content else None,
                AgentType.USER_STORIES: stories_content,
            }
            
            # Create async executor for Phase 2
            # Use AsyncParallelExecutor for true async parallel execution
            executor = AsyncParallelExecutor(max_workers=8)
            
            # Create async task execution coroutines for each Phase 2 task
            # These coroutines will extract dependencies from context when executed
            def create_async_task_coro(task: Phase2Task):
                """Create an async task coroutine that extracts dependencies and executes agent"""
                async def execute_async_task():
                    # Extract dependency content from context (for Phase 2 dependencies)
                    # Phase 1 dependencies are already available in phase1_deps_content
                    deps_content = phase1_deps_content.copy()
                    
                    # Get Phase 2 dependencies from context (these are completed in Phase 2)
                    # Note: We run sync context_manager calls in executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    for dep_type in task.dependencies:
                        if dep_type not in deps_content:
                            # This is a Phase 2 dependency, fetch from context (async-safe)
                            # Capture dep_type in closure to avoid lambda issues
                            dep_type_capture = dep_type
                            dep_output = await loop.run_in_executor(
                                None,
                                lambda dt=dep_type_capture: self.context_manager.get_agent_output(project_id, dt)
                            )
                            if dep_output:
                                deps_content[dep_type] = dep_output.content
                            else:
                                # Dependency not yet available (shouldn't happen if dependencies are correct)
                                logger.warning(f"  ⚠️  Dependency {dep_type.value} not found in context for {task.task_id}")
                                deps_content[dep_type] = None
                    
                    # Build kwargs for agent.generate_and_save (sync function, but fast)
                    kwargs = build_kwargs_for_task(
                        task=task,
                        coordinator=self,
                        req_summary=req_summary,
                        technical_summary=technical_summary,
                        charter_content=charter_content,
                        project_id=project_id,
                        context_manager=self.context_manager,
                        deps_content=deps_content
                    )
                    
                    # Get agent instance
                    agent = get_agent_for_task(self, task.agent_type)
                    if not agent:
                        raise ValueError(f"Agent not found for {task.agent_type.value}")
                    
                    # Execute agent.generate_and_save (async if available, otherwise sync in executor)
                    # Check if agent has async_generate_and_save method first
                    if hasattr(agent, 'async_generate_and_save') and asyncio.iscoroutinefunction(agent.async_generate_and_save):
                        # Native async method (best performance)
                        result = await agent.async_generate_and_save(**kwargs)
                    elif hasattr(agent, 'generate_and_save') and asyncio.iscoroutinefunction(agent.generate_and_save):
                        # Async generate_and_save method
                        result = await agent.generate_and_save(**kwargs)
                    else:
                        # Fallback: run sync method in executor
                        result = await loop.run_in_executor(
                            None,
                            lambda kw=kwargs: agent.generate_and_save(**kw)
                        )
                    return result
                
                return execute_async_task
            
            # Add all tasks to async executor
            for task in phase2_tasks:
                # Create the async coroutine for this task
                task_coro = create_async_task_coro(task)()
                dep_task_ids = dependency_map.get(task.task_id, [])
                
                executor.add_task(
                    task_id=task.task_id,
                    coro=task_coro,
                    dependencies=dep_task_ids
                )
                logger.debug(f"  📝 Added async task: {task.task_id} (depends on: {dep_task_ids})")
            
            # Execute parallel tasks asynchronously
            # Note: Since generate_all_docs is sync, we need to run the async executor
            # We use asyncio.run() which creates a new event loop and runs until complete
            logger.info(f"🚀 Executing {len(executor.tasks)} parallel async tasks with DAG dependencies...")
            try:
                # Check if we're in an async context
                try:
                    loop = asyncio.get_running_loop()
                    # We're in an async context, but generate_all_docs is sync
                    # This shouldn't happen, but if it does, we'll use a thread
                    logger.warning("  ⚠️  generate_all_docs is sync but called from async context, using thread pool")
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor_pool:
                        future = executor_pool.submit(asyncio.run, executor.execute())
                        parallel_results = future.result()
                except RuntimeError:
                    # No event loop is running, we can use asyncio.run()
                    parallel_results = asyncio.run(executor.execute())
            except Exception as e:
                logger.error(f"  ❌ Error executing async tasks: {e}", exc_info=True)
                # Fallback to sync execution if async fails
                logger.warning("  ⚠️  Falling back to sync ParallelExecutor")
                from src.utils.parallel_executor import ParallelExecutor as SyncParallelExecutor
                sync_executor = SyncParallelExecutor(max_workers=8)
                
                # Re-add tasks to sync executor
                def create_sync_task_executor(task: Phase2Task):
                    def execute_task():
                        deps_content = phase1_deps_content.copy()
                        for dep_type in task.dependencies:
                            if dep_type not in deps_content:
                                dep_output = self.context_manager.get_agent_output(project_id, dep_type)
                                if dep_output:
                                    deps_content[dep_type] = dep_output.content
                                else:
                                    logger.warning(f"  ⚠️  Dependency {dep_type.value} not found in context for {task.task_id}")
                                    deps_content[dep_type] = None
                        kwargs = build_kwargs_for_task(
                            task=task,
                            coordinator=self,
                            req_summary=req_summary,
                            technical_summary=technical_summary,
                            charter_content=charter_content,
                            project_id=project_id,
                            context_manager=self.context_manager,
                            deps_content=deps_content
                        )
                        agent = get_agent_for_task(self, task.agent_type)
                        if not agent:
                            raise ValueError(f"Agent not found for {task.agent_type.value}")
                        return agent.generate_and_save(**kwargs)
                    return execute_task
                
                for task in phase2_tasks:
                    task_executor = create_sync_task_executor(task)
                    dep_task_ids = dependency_map.get(task.task_id, [])
                    sync_executor.add_task(
                        task_id=task.task_id,
                        func=task_executor,
                        args=(),
                        dependencies=dep_task_ids
                    )
                parallel_results = sync_executor.execute()
            
            # Map AgentType to document type name for results
            # This mapping ensures consistency with the original implementation
            agent_type_to_doc_type = {
                AgentType.API_DOCUMENTATION: "api_documentation",
                AgentType.DATABASE_SCHEMA: "database_schema",
                AgentType.SETUP_GUIDE: "setup_guide",
                AgentType.DEVELOPER_DOCUMENTATION: "developer_documentation",
                AgentType.TEST_DOCUMENTATION: "test_documentation",
                AgentType.USER_DOCUMENTATION: "user_documentation",
                AgentType.LEGAL_COMPLIANCE: "legal_compliance",
                AgentType.SUPPORT_PLAYBOOK: "support_playbook",
                AgentType.PM_DOCUMENTATION: "pm_documentation",
                AgentType.STAKEHOLDER_COMMUNICATION: "stakeholder_documentation",
                AgentType.BUSINESS_MODEL: "business_model",
                AgentType.MARKETING_PLAN: "marketing_plan",
            }
            
            def get_doc_type_from_agent_type(agent_type: AgentType) -> str:
                """Convert AgentType to document type name for results"""
                return agent_type_to_doc_type.get(agent_type, agent_type.value)
            
            # Collect parallel task results
            for task in phase2_tasks:
                task_id = task.task_id
                file_path = parallel_results.get(task_id)
                agent_type = task.agent_type
                doc_type = get_doc_type_from_agent_type(agent_type)
                
                if file_path and executor.tasks[task_id].status == TaskStatus.COMPLETE:
                    results["files"][doc_type] = file_path
                    results["status"][doc_type] = "complete"
                    
                    # Read content and add to final_docs
                    try:
                        content = self.file_manager.read_file(file_path)
                        final_docs[agent_type] = content
                        document_file_paths[agent_type] = file_path
                        logger.info(f"  ✅ {doc_type}: {file_path}")
                    except Exception as e:
                        logger.warning(f"  ⚠️  Could not read {doc_type}: {e}")
                else:
                    error = executor.tasks[task_id].error if task_id in executor.tasks else "Unknown error"
                    logger.error(f"  ❌ Task {task_id} failed: {error}")
                    results["status"][doc_type] = "failed"
            
            logger.info("=" * 80)
            logger.info(f"✅ PHASE 2 COMPLETE: {len([r for r in parallel_results.values() if r])} documents generated in parallel")
            logger.info("=" * 80)
            
            # --- PHASE 3: FINAL PACKAGING (Cross-ref, Review, Convert) ---
            logger.info("=" * 80)
            logger.info("--- PHASE 3: Final Packaging and Conversion ---")
            logger.info("=" * 80)
            
            # 1. Cross-Referencing
            logger.info("📎 Step 1: Adding cross-references to all documents...")
            try:
                referenced_docs = self.cross_referencer.create_cross_references(
                    final_docs,
                    document_file_paths
                )
                
                # Save cross-referenced documents back to files
                updated_count = 0
                for agent_type, referenced_content in referenced_docs.items():
                    original_content = final_docs.get(agent_type)
                    if referenced_content != original_content:
                        original_file_path = document_file_paths[agent_type]
                        # Write directly to original absolute path to preserve folder structure
                        if Path(original_file_path).is_absolute():
                            Path(original_file_path).write_text(referenced_content, encoding='utf-8')
                            logger.debug(f"Updated cross-referenced file: {original_file_path}")
                        else:
                            self.file_manager.write_file(original_file_path, referenced_content)
                        # Update final_docs for quality review
                        final_docs[agent_type] = referenced_content
                        updated_count += 1
                
                logger.info(f"  ✅ Added cross-references to {updated_count} documents")
                
                # Generate document index
                try:
                    index_content = self.cross_referencer.generate_document_index(
                        final_docs,
                        document_file_paths,
                        project_name=req_summary.get('project_overview', 'Project')[:50]
                    )
                    index_path = self.file_manager.write_file("index.md", index_content)
                    results["files"]["document_index"] = index_path
                    logger.info(f"  ✅ Document index created: {index_path}")
                except Exception as e:
                    logger.warning(f"  ⚠️  Could not generate index: {e}")
            except Exception as e:
                logger.warning(f"  ⚠️  Cross-referencing failed: {e}")
            
            # 2. Final Quality Review (generate report only)
            # Note: In hybrid mode, Phase 1 documents already went through quality gates
            # This review is for overall assessment and secondary documents
            logger.info("📊 Step 2: Generating final quality review report...")
            try:
                # Convert final_docs to dict with string keys for quality reviewer
                all_documentation_for_review = {
                    agent_type.value: content
                    for agent_type, content in final_docs.items()
                }
                
                quality_review_path = self.quality_reviewer.generate_and_save(
                    all_documentation=all_documentation_for_review,
                    output_filename="quality_review.md",
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["quality_review"] = quality_review_path
                results["status"]["quality_review"] = "complete"
                logger.info(f"  ✅ Quality review report generated: {quality_review_path}")
            except Exception as e:
                logger.warning(f"  ⚠️  Quality review failed: {e}")
                results["status"]["quality_review"] = "failed"
            
            # 3. Claude CLI Documentation
            logger.info("📝 Step 3: Generating Claude CLI documentation...")
            try:
                claude_md_path = self.claude_cli_agent.generate_and_save(
                    all_documentation=final_docs,
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["claude_cli_documentation"] = claude_md_path
                results["status"]["claude_cli_documentation"] = "complete"
                logger.info(f"  ✅ Claude CLI documentation generated: {claude_md_path}")
            except Exception as e:
                logger.warning(f"  ⚠️  Claude CLI documentation generation failed: {e}")
                results["status"]["claude_cli_documentation"] = "failed"
            
            # 4. Format Conversion
            logger.info("📄 Step 4: Converting documents to multiple formats...")
            try:
                # Prepare documents dict with proper names for format converter
                documents_for_conversion = {
                    agent_type.value: content
                    for agent_type, content in final_docs.items()
                }
                
                format_results = self.format_converter.convert_all_documents(
                    documents=documents_for_conversion,
                    formats=["html", "pdf", "docx"],
                    project_id=project_id,
                    context_manager=self.context_manager
                )
                results["files"]["format_conversions"] = format_results
                results["status"]["format_conversions"] = "complete"
                
                total_conversions = sum(len(fmts) for fmts in format_results.values())
                logger.info(f"  ✅ Converted {len(format_results)} documents to {total_conversions} files (HTML, PDF, DOCX)")
            except Exception as e:
                logger.warning(f"  ⚠️  Format conversion failed: {e}, trying HTML-only as fallback")
                try:
                    documents_for_conversion = {
                        agent_type.value: content
                        for agent_type, content in final_docs.items()
                    }
                    format_results = self.format_converter.convert_all_documents(
                        documents=documents_for_conversion,
                        formats=["html"],
                        project_id=project_id,
                        context_manager=self.context_manager
                    )
                    results["files"]["format_conversions"] = format_results
                    results["status"]["format_conversions"] = "partial (HTML only)"
                    logger.info(f"  ✅ Converted {len(format_results)} documents to HTML")
                except Exception as e2:
                    logger.warning(f"  ⚠️  Format conversion failed: {e2}")
                    results["status"]["format_conversions"] = "skipped"
            
            logger.info("=" * 80)
            logger.info("✅ PHASE 3 COMPLETE: Final packaging and conversion completed")
            logger.info("=" * 80)
            
            # --- PHASE 4: CODE ANALYSIS AND DOCUMENTATION UPDATE (Optional) ---
            if codebase_path:
                logger.info("=" * 80)
                logger.info("--- PHASE 4: Code Analysis and Documentation Update ---")
                logger.info("=" * 80)
                logger.info(f"📁 Analyzing codebase at: {codebase_path}")
                
                try:
                    # Analyze codebase
                    logger.info("🔍 Step 1: Analyzing codebase structure...")
                    code_analysis = self.code_analyst.analyze_codebase(codebase_path)
                    logger.info(f"  ✅ Code analysis complete: {len(code_analysis.get('modules', []))} modules, "
                              f"{len(code_analysis.get('classes', []))} classes, "
                              f"{len(code_analysis.get('functions', []))} functions")
                    
                    # Update API Documentation with code analysis
                    logger.info("📝 Step 2: Updating API documentation based on actual code...")
                    try:
                        # Get existing API documentation
                        api_doc_content = final_docs.get(AgentType.API_DOCUMENTATION)
                        
                        # Generate updated API documentation from code
                        updated_api_doc = self.code_analyst.generate_code_documentation(
                            code_analysis=code_analysis,
                            existing_docs=api_doc_content
                        )
                        
                        # Save updated API documentation
                        api_doc_path = document_file_paths.get(AgentType.API_DOCUMENTATION)
                        if api_doc_path:
                            # Update the file
                            if Path(api_doc_path).is_absolute():
                                Path(api_doc_path).write_text(updated_api_doc, encoding='utf-8')
                            else:
                                self.file_manager.write_file(api_doc_path, updated_api_doc)
                            
                            # Update final_docs and context
                            final_docs[AgentType.API_DOCUMENTATION] = updated_api_doc
                            
                            # Update context
                            api_output = AgentOutput(
                                agent_type=AgentType.API_DOCUMENTATION,
                                document_type="api_documentation",
                                content=updated_api_doc,
                                file_path=api_doc_path,
                                status=DocumentStatus.COMPLETE,
                                generated_at=datetime.now(),
                                dependencies=[]
                            )
                            self.context_manager.save_agent_output(project_id, api_output)
                            
                            logger.info(f"  ✅ API documentation updated: {api_doc_path}")
                            results["status"]["api_documentation"] = "updated_with_code_analysis"
                        else:
                            logger.warning("  ⚠️  API documentation file path not found, creating new file")
                            api_doc_path = self.file_manager.write_file("api_documentation.md", updated_api_doc)
                            final_docs[AgentType.API_DOCUMENTATION] = updated_api_doc
                            document_file_paths[AgentType.API_DOCUMENTATION] = api_doc_path
                            results["files"]["api_documentation"] = api_doc_path
                            results["status"]["api_documentation"] = "created_from_code_analysis"
                    except Exception as e:
                        logger.warning(f"  ⚠️  API documentation update failed: {e}")
                    
                    # Update Developer Documentation with code analysis
                    logger.info("📝 Step 3: Updating developer documentation based on actual code...")
                    try:
                        # Get existing developer documentation
                        dev_doc_content = final_docs.get(AgentType.DEVELOPER_DOCUMENTATION)
                        
                        # Generate updated developer documentation from code
                        updated_dev_doc = self.code_analyst.generate_code_documentation(
                            code_analysis=code_analysis,
                            existing_docs=dev_doc_content
                        )
                        
                        # Save updated developer documentation
                        dev_doc_path = document_file_paths.get(AgentType.DEVELOPER_DOCUMENTATION)
                        if dev_doc_path:
                            # Update the file
                            if Path(dev_doc_path).is_absolute():
                                Path(dev_doc_path).write_text(updated_dev_doc, encoding='utf-8')
                            else:
                                self.file_manager.write_file(dev_doc_path, updated_dev_doc)
                            
                            # Update final_docs and context
                            final_docs[AgentType.DEVELOPER_DOCUMENTATION] = updated_dev_doc
                            
                            # Update context
                            dev_output = AgentOutput(
                                agent_type=AgentType.DEVELOPER_DOCUMENTATION,
                                document_type="developer_documentation",
                                content=updated_dev_doc,
                                file_path=dev_doc_path,
                                status=DocumentStatus.COMPLETE,
                                generated_at=datetime.now(),
                                dependencies=[]
                            )
                            self.context_manager.save_agent_output(project_id, dev_output)
                            
                            logger.info(f"  ✅ Developer documentation updated: {dev_doc_path}")
                            results["status"]["developer_documentation"] = "updated_with_code_analysis"
                        else:
                            logger.warning("  ⚠️  Developer documentation file path not found, creating new file")
                            dev_doc_path = self.file_manager.write_file("developer_guide.md", updated_dev_doc)
                            final_docs[AgentType.DEVELOPER_DOCUMENTATION] = updated_dev_doc
                            document_file_paths[AgentType.DEVELOPER_DOCUMENTATION] = dev_doc_path
                            results["files"]["developer_documentation"] = dev_doc_path
                            results["status"]["developer_documentation"] = "created_from_code_analysis"
                    except Exception as e:
                        logger.warning(f"  ⚠️  Developer documentation update failed: {e}")
                    
                    # Save code analysis results
                    logger.info("💾 Step 4: Saving code analysis results...")
                    try:
                        import json
                        code_analysis_json = json.dumps(code_analysis, indent=2, default=str)
                        code_analysis_path = self.file_manager.write_file("code_analysis.json", code_analysis_json)
                        results["files"]["code_analysis"] = code_analysis_path
                        results["status"]["code_analysis"] = "complete"
                        logger.info(f"  ✅ Code analysis saved: {code_analysis_path}")
                    except Exception as e:
                        logger.warning(f"  ⚠️  Failed to save code analysis: {e}")
                    
                    logger.info("=" * 80)
                    logger.info("✅ PHASE 4 COMPLETE: Code analysis and documentation update completed")
                    logger.info("=" * 80)
                    
                except Exception as e:
                    logger.error(f"  ❌ Phase 4 (Code Analysis) failed: {e}", exc_info=True)
                    results["status"]["code_analysis"] = "failed"
                    results["code_analysis_error"] = str(e)
            else:
                logger.debug("  Phase 4 skipped (no codebase_path provided)")
            
            # Optional: Auto-Fix Loop (can be enabled via ENABLE_AUTO_FIX=true)
            # Note: In hybrid mode, Phase 1 documents already went through quality gates
            # This auto-fix is primarily for secondary documents if needed
            # (Keeping the auto-fix code for backward compatibility, but it's optional in hybrid mode)
            try:
                from src.config.settings import get_settings
                settings = get_settings()
                
                enable_auto_fix = getattr(settings, 'enable_auto_fix', False) or os.getenv("ENABLE_AUTO_FIX", "false").lower() == "true"
                fix_threshold = float(os.getenv("AUTO_FIX_THRESHOLD", "70.0"))
                
                if enable_auto_fix:
                    logger.info("🔧 Optional Auto-Fix Loop: Analyzing quality review for secondary documents...")
                    quality_review_content = self.file_manager.read_file(quality_review_path)
                    
                    # Extract overall quality score
                    overall_score_pattern = r'Overall Quality Score:\s*(\d+)/100'
                    overall_scores = re.findall(overall_score_pattern, quality_review_content)
                    overall_score = int(overall_scores[0]) if overall_scores else 100
                    
                    # In hybrid mode, we typically don't need auto-fix for Phase 1 documents
                    # (they already went through quality gates), but we can improve Phase 2 documents
                    logger.info(f"  📊 Overall quality score: {overall_score}/100")
                    if overall_score < fix_threshold:
                        logger.info(f"  ⚠️  Overall score below threshold ({fix_threshold}), but Phase 1 documents already have quality gates")
                        logger.info(f"  💡 Consider reviewing quality_review.md for detailed feedback")
                    else:
                        logger.info(f"  ✅ Overall quality score meets threshold")
                else:
                    logger.debug("  Auto-Fix Loop disabled (ENABLE_AUTO_FIX=false)")
            except Exception as e:
                logger.debug(f"  Auto-Fix Loop check skipped: {e}")
            
            # Summary
            logger.info("=" * 80)
            logger.info(f"🚀 HYBRID Workflow COMPLETED for project {project_id}")
            logger.info("=" * 80)
            
            summary = get_documents_summary(results["files"])
            logger.info(f"Documents organized by level: Level 1: {len(summary['level_1_strategic']['documents'])}, "
                       f"Level 2: {len(summary['level_2_product']['documents'])}, "
                       f"Level 3: {len(summary['level_3_technical']['documents'])}, "
                       f"Cross-Level: {len(summary['cross_level']['documents'])}")
            
            results["documents_by_level"] = summary
            
            return results
            
        except Exception as e:
                logger.error(f"❌ CRITICAL ERROR in HYBRID workflow: {str(e)}", exc_info=True)
                results["error"] = str(e)
                return results
    
    async def async_generate_all_docs(
        self,
        user_idea: str,
        project_id: Optional[str] = None,
        profile: str = "team",
        codebase_path: Optional[str] = None
    ) -> Dict:
        """
        Generate all documentation types asynchronously (async version of generate_all_docs)
        
        This method uses async operations where possible, falling back to run_in_executor
        for sync operations. For Phase 2, it uses AsyncParallelExecutor for true async
        parallel execution.
        
        Args:
            user_idea: User's project idea
            project_id: Optional project ID (generates one if not provided)
            profile: "team" or "individual" - determines which docs to generate
            codebase_path: Optional path to codebase directory for Phase 4
        
        Returns:
            Dict with generated file paths and status
        """
        # For now, run sync version in executor (can be optimized later)
        # This maintains backward compatibility while allowing async callers
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: self.generate_all_docs(user_idea, project_id, profile, codebase_path)
        )
    
    def get_workflow_status(self, project_id: str) -> Dict:
        """Get current workflow status for a project"""
        context = self.context_manager.get_shared_context(project_id)
        
        return {
            "project_id": project_id,
            "workflow_status": {
                agent_type.value: status.value
                for agent_type, status in context.workflow_status.items()
            },
            "completed_agents": [
                agent_type.value
                for agent_type, status in context.workflow_status.items()
                if status == DocumentStatus.COMPLETE
            ],
            "total_outputs": len(context.agent_outputs)
        }

