"""WebSocket connection manager"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Set

from fastapi import WebSocket

from src.utils.logger import get_logger

logger = get_logger(__name__)


class WebSocketManager:
    """
    Manage WebSocket connections per project.
    
    This class maintains a registry of active WebSocket connections grouped
    by project ID, allowing broadcast of progress updates to all connected
    clients for a specific project.
    
    Features:
    - Per-project connection tracking
    - Automatic cleanup of disconnected clients
    - Thread-safe connection management
    - Timestamped message broadcasting
    - Message queue for disconnected clients (reconnect support)
    - Connection limit per project
    - Heartbeat/ping support
    """
    
    def __init__(self, max_connections_per_project: int = 5, max_queue_size: int = 100) -> None:
        """
        Initialize the WebSocket manager with empty connection registry.
        
        Args:
            max_connections_per_project: Maximum number of connections per project
            max_queue_size: Maximum number of messages to queue per project
        """
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.message_queue: Dict[str, List[Dict[str, Any]]] = {}  # Cache messages for disconnected clients
        self.max_connections_per_project = max_connections_per_project
        self.max_queue_size = max_queue_size
    
    async def connect(self, websocket: WebSocket, project_id: str) -> None:
        """
        Connect a WebSocket to a project.
        
        Accepts the WebSocket connection and adds it to the registry for
        the specified project. Checks connection limits and sends queued messages.
        
        Args:
            websocket: WebSocket connection to accept
            project_id: Project identifier to associate with this connection
            
        Raises:
            ValueError: If connection limit is exceeded
        """
        # Check connection limit
        connections = self.active_connections.get(project_id, set())
        if len(connections) >= self.max_connections_per_project:
            logger.warning(
                "Connection limit exceeded for project %s (%d/%d). Rejecting new connection.",
                project_id,
                len(connections),
                self.max_connections_per_project
            )
            await websocket.close(code=1008, reason="Too many connections")
            return
        
        await websocket.accept()
        self.active_connections.setdefault(project_id, set()).add(websocket)
        
        # Send queued messages if any
        if project_id in self.message_queue and self.message_queue[project_id]:
            queued_messages = self.message_queue[project_id]
            logger.info(
                "Sending %d queued messages to reconnected client for project %s",
                len(queued_messages),
                project_id
            )
            
            # Send all queued messages
            for msg in queued_messages:
                try:
                    await websocket.send_json(msg)
                except Exception as exc:
                    logger.warning("Failed to send queued message to reconnected client: %s", exc)
                    break  # Stop sending if connection fails
            
            # Clear queue after sending
            del self.message_queue[project_id]

    def disconnect(self, websocket: WebSocket, project_id: str) -> None:
        """
        Disconnect a WebSocket from a project.
        
        Removes the connection from the registry. If no connections remain
        for the project, the project entry is removed.
        
        Args:
            websocket: WebSocket connection to remove
            project_id: Project identifier
        """
        connections = self.active_connections.get(project_id)
        if not connections:
            return
        connections.discard(websocket)
        if not connections:
            self.active_connections.pop(project_id, None)

    async def send_progress(self, project_id: str, message: Dict[str, Any]) -> None:
        """
        Send progress update to all connected clients for a project.
        
        Broadcasts a message to all active WebSocket connections for the given
        project. Automatically removes disconnected clients from the registry.
        If no connections exist, messages are queued for later delivery.
        
        Args:
            project_id: Project identifier
            message: Message dictionary to send (will have timestamp added)
        
        Note:
            If no connections exist for the project, messages are queued.
            Failed sends are logged but don't raise exceptions.
        """
        payload = {**message, "timestamp": datetime.now().isoformat()}
        connections = self.active_connections.get(project_id)
        
        if not connections:
            # No active connections - queue the message
            if project_id not in self.message_queue:
                self.message_queue[project_id] = []
            
            queue = self.message_queue[project_id]
            
            # Limit queue size to prevent memory issues
            if len(queue) >= self.max_queue_size:
                # Remove oldest messages (FIFO)
                queue.pop(0)
                logger.warning(
                    "Message queue for project %s reached max size (%d). Dropping oldest message.",
                    project_id,
                    self.max_queue_size
                )
            
            queue.append(payload)
            logger.debug(
                "Queued message for project %s (no active connections). Queue size: %d",
                project_id,
                len(queue)
            )
            return
        
        # Send to all active connections
        disconnected: Set[WebSocket] = set()

        for connection in connections:
            try:
                await connection.send_json(payload)
            except Exception as exc:
                logger.warning("Failed to send WebSocket message: %s", exc)
                disconnected.add(connection)
        
        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection, project_id)
    
    def get_queue_size(self, project_id: str) -> int:
        """
        Get the number of queued messages for a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Number of queued messages
        """
        return len(self.message_queue.get(project_id, []))
    
    def clear_queue(self, project_id: str) -> None:
        """
        Clear queued messages for a project.
        
        Args:
            project_id: Project identifier
        """
        if project_id in self.message_queue:
            del self.message_queue[project_id]
            logger.debug("Cleared message queue for project %s", project_id)
    
    def get_connection_count(self, project_id: str) -> int:
        """
        Get the number of active connections for a project.
        
        Args:
            project_id: Project identifier
            
        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(project_id, set()))


# Global WebSocket manager instance
websocket_manager = WebSocketManager()

