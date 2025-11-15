"""
Celery tasks for document generation
"""
import asyncio
import time
from typing import Any, Dict, List, Optional

from celery import Task

from src.coordination.coordinator import WorkflowCoordinator
from src.context.context_manager import ContextManager
from src.tasks.celery_app import celery_app
from src.utils.logger import get_logger
from src.web.websocket_manager import websocket_manager

logger = get_logger(__name__)


def send_websocket_notification(project_id: str, message: Dict[str, Any]) -> None:
    """
    Send WebSocket notification to connected clients.
    This runs in an async context to send messages.
    """
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(websocket_manager.send_progress(project_id, message))
        loop.close()
    except Exception as exc:
        logger.warning(f"Failed to send WebSocket notification for project {project_id}: {exc}")


@celery_app.task(
    bind=True,
    name="omnidoc.generate_documents",
    max_retries=3,
    default_retry_delay=60,  # Retry after 60 seconds
    soft_time_limit=3600,  # 1 hour soft timeout
    time_limit=3700,  # 1 hour 10 seconds hard timeout
)
def generate_documents_task(
    self: Task,
    project_id: str,
    user_idea: str,
    selected_documents: List[str],
    provider_name: Optional[str] = None,
    codebase_path: Optional[str] = None,
) -> Dict:
    """
    Celery task to generate documents for a project
    
    Args:
        project_id: Project identifier
        user_idea: User's project idea
        selected_documents: List of document IDs to generate
        provider_name: Optional LLM provider name
        codebase_path: Optional codebase path
        
    Returns:
        Dictionary with generation results
    """
    context_manager = ContextManager()
    
    task_start_time = time.time()
    try:
        logger.info(
            "Starting document generation task [Project: %s] [Documents: %d] [Attempt: %d/%d] [Provider: %s]",
            project_id,
            len(selected_documents),
            self.request.retries + 1,
            self.max_retries + 1,
            provider_name or "default"
        )
        
        # Send WebSocket notification
        send_websocket_notification(project_id, {
            "type": "status",
            "status": "started",
            "message": "Document generation started",
            "project_id": project_id,
        })
        
        # Update task state
        self.update_state(state="PROGRESS", meta={"status": "initializing", "project_id": project_id})
        
        # Create coordinator
        if provider_name:
            logger.debug("Creating WorkflowCoordinator with provider: %s [Project: %s]", provider_name, project_id)
            coordinator = WorkflowCoordinator(
                context_manager=context_manager,
                provider_name=provider_name
            )
        else:
            logger.debug("Creating WorkflowCoordinator with default provider [Project: %s]", project_id)
            coordinator = WorkflowCoordinator(context_manager=context_manager)
        
        # Create progress callback to send WebSocket updates
        async def progress_callback(message: Dict[str, Any]) -> None:
            """Send progress updates via WebSocket"""
            logger.debug(
                "Progress update [Project: %s] [Type: %s] [Document: %s]",
                project_id,
                message.get("type"),
                message.get("document_id", "N/A")
            )
            send_websocket_notification(project_id, message)
        
        # Run generation asynchronously with progress callback
        logger.info("Starting document generation workflow [Project: %s]", project_id)
        generation_start_time = time.time()
        results = asyncio.run(
            coordinator.async_generate_all_docs(
                user_idea=user_idea,
                project_id=project_id,
                selected_documents=selected_documents,
                codebase_path=codebase_path,
                progress_callback=progress_callback,
            )
        )
        generation_duration = time.time() - generation_start_time
        
        logger.info(
            "Document generation workflow completed [Project: %s] [Duration: %.2fs] [Documents: %d]",
            project_id,
            generation_duration,
            len(results.get("files", {}))
        )
        
        # Update project status
        context_manager.update_project_status(
            project_id=project_id,
            status="complete",
            completed_agents=list(results.get("files", {}).keys()),
            results=results,
            selected_documents=selected_documents,
        )
        
        # Send success notification
        send_websocket_notification(project_id, {
            "type": "status",
            "status": "complete",
            "message": f"Successfully generated {len(results.get('files', {}))} documents",
            "project_id": project_id,
            "files_count": len(results.get("files", {})),
        })
        
        total_duration = time.time() - task_start_time
        logger.info(
            "✅ Document generation task completed [Project: %s] [Total duration: %.2fs] [Generation: %.2fs] [Documents: %d]",
            project_id,
            total_duration,
            generation_duration,
            len(results.get("files", {}))
        )
        return {
            "status": "complete",
            "project_id": project_id,
            "files_count": len(results.get("files", {})),
        }
        
    except Exception as exc:
        error_message = str(exc)
        total_duration = time.time() - task_start_time
        error_type = type(exc).__name__
        
        logger.error(
            "❌ Document generation failed [Project: %s] [Duration: %.2fs] [Error: %s] [Type: %s]",
            project_id,
            total_duration,
            error_message,
            error_type,
            exc_info=True
        )
        
        # Check if this is a retryable error
        is_retryable = isinstance(exc, (ConnectionError, TimeoutError, OSError))
        retries_left = self.max_retries - self.request.retries
        
        if is_retryable and retries_left > 0:
            # Retry with exponential backoff
            retry_delay = 60 * (2 ** self.request.retries)  # Exponential backoff: 60s, 120s, 240s
            logger.warning(
                "Retrying task [Project: %s] [Attempt: %d/%d] [Delay: %ds] [Error: %s]",
                project_id,
                self.request.retries + 1,
                self.max_retries,
                retry_delay,
                error_type
            )
            
            # Send retry notification
            send_websocket_notification(project_id, {
                "type": "status",
                "status": "retrying",
                "message": f"Generation failed, retrying in {retry_delay} seconds...",
                "project_id": project_id,
                "error": error_message,
                "retry_attempt": self.request.retries + 1,
                "max_retries": self.max_retries,
            })
            
            # Schedule retry
            raise self.retry(exc=exc, countdown=retry_delay)
        else:
            # Final failure - no more retries
            logger.error(
                "Task failed permanently [Project: %s] [Total duration: %.2fs] [Retries exhausted: %d/%d] [Error: %s]",
                project_id,
                total_duration,
                self.request.retries,
                self.max_retries,
                error_type
            )
            
            # Update project status with error
            context_manager.update_project_status(
                project_id=project_id,
                status="failed",
                error=error_message,
                selected_documents=selected_documents,
            )
            
            # Send failure notification
            send_websocket_notification(project_id, {
                "type": "status",
                "status": "failed",
                "message": "Document generation failed",
                "project_id": project_id,
                "error": error_message,
            })
            
            # Re-raise to mark task as failed
            raise

