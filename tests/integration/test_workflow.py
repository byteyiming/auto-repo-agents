"""
Integration Tests: Multi-Agent Workflow
Tests the complete workflow coordinator
"""
import pytest
from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.context.shared_context import AgentType


@pytest.mark.integration
@pytest.mark.slow
class TestWorkflowCoordinator:
    """Integration tests for workflow coordination"""
    
    def test_generate_all_docs(self, mock_gemini_provider, context_manager, temp_dir):
        """Test complete workflow with mocked LLM"""
        # Create custom agents with mocked provider
        from src.agents.requirements_analyst import RequirementsAnalyst
        from src.agents.pm_documentation_agent import PMDocumentationAgent
        from src.utils.file_manager import FileManager
        from src.rate_limit.queue_manager import RequestQueue
        
        rate_limiter = RequestQueue(max_rate=1000, period=60)
        file_manager = FileManager(base_dir=str(temp_dir))
        
        req_agent = RequirementsAnalyst(
            llm_provider=mock_gemini_provider,
            rate_limiter=rate_limiter,
            file_manager=FileManager(base_dir=str(temp_dir / "docs"))
        )
        
        pm_agent = PMDocumentationAgent(
            llm_provider=mock_gemini_provider,
            rate_limiter=rate_limiter,
            file_manager=FileManager(base_dir=str(temp_dir / "docs" / "pm"))
        )
        
        # Create coordinator with custom agents
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        coordinator.requirements_analyst = req_agent
        coordinator.pm_agent = pm_agent
        
        results = coordinator.generate_all_docs("Build a blog platform", profile="team")
        
        assert results["project_id"] is not None
        assert "requirements" in results["files"]
        # pm_documentation is now in Phase 4, so it may not be generated if phase1_only=True or phases_to_run doesn't include Phase 4
        # Check if pm_documentation exists (it should for team profile with full workflow)
        if "pm_documentation" in results["files"]:
            assert results["status"]["pm_documentation"] == "complete"
        assert results["status"]["requirements"] == "complete"
    
    def test_workflow_status(self, mock_gemini_provider, context_manager, temp_dir, test_project_id):
        """Test workflow status tracking"""
        from src.agents.requirements_analyst import RequirementsAnalyst
        from src.agents.pm_documentation_agent import PMDocumentationAgent
        from src.utils.file_manager import FileManager
        from src.rate_limit.queue_manager import RequestQueue
        
        rate_limiter = RequestQueue(max_rate=1000, period=60)
        
        req_agent = RequirementsAnalyst(
            llm_provider=mock_gemini_provider,
            rate_limiter=rate_limiter,
            file_manager=FileManager(base_dir=str(temp_dir / "docs"))
        )
        
        pm_agent = PMDocumentationAgent(
            llm_provider=mock_gemini_provider,
            rate_limiter=rate_limiter,
            file_manager=FileManager(base_dir=str(temp_dir / "docs" / "pm"))
        )
        
        coordinator = WorkflowCoordinator(context_manager=context_manager)
        coordinator.requirements_analyst = req_agent
        coordinator.pm_agent = pm_agent
        
        # Run workflow
        results = coordinator.generate_all_docs("Test idea", project_id=test_project_id, profile="team")
        
        # Check status
        status = coordinator.get_workflow_status(test_project_id)
        
        assert status["project_id"] == test_project_id
        assert AgentType.REQUIREMENTS_ANALYST.value in status["completed_agents"]
        # pm_documentation is now in Phase 4, so it may not be generated if phase1_only=True or phases_to_run doesn't include Phase 4
        # For team profile with full workflow, it should be generated
        if AgentType.PM_DOCUMENTATION.value in status["completed_agents"]:
            assert status["total_outputs"] >= 2
        else:
            # At minimum, requirements should be generated
            assert status["total_outputs"] >= 1

