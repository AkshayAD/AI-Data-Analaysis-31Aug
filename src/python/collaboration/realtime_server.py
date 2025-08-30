#!/usr/bin/env python3
"""
Real-time collaboration server for multi-user sessions
Implements WebSocket connections for live updates
"""

import asyncio
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, List, Set, Any, Optional
from dataclasses import dataclass, asdict
import hashlib

try:
    import websockets
    from websockets.server import WebSocketServerProtocol
except ImportError:
    websockets = None
    WebSocketServerProtocol = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class User:
    """Represents a connected user"""
    id: str
    name: str
    email: str
    avatar: Optional[str] = None
    role: str = "viewer"  # viewer, editor, admin
    connected_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        if not self.connected_at:
            self.connected_at = datetime.now()
        if not self.last_activity:
            self.last_activity = datetime.now()
        if not self.avatar:
            # Generate avatar from email hash
            email_hash = hashlib.md5(self.email.lower().encode()).hexdigest()
            self.avatar = f"https://www.gravatar.com/avatar/{email_hash}?d=identicon"

@dataclass
class Workspace:
    """Represents a collaborative workspace"""
    id: str
    name: str
    owner_id: str
    created_at: datetime
    updated_at: datetime
    data: Dict[str, Any]
    active_users: Set[str]
    settings: Dict[str, Any]
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now()
        if not self.updated_at:
            self.updated_at = datetime.now()
        if not self.active_users:
            self.active_users = set()
        if not self.settings:
            self.settings = {
                'public': False,
                'max_users': 10,
                'auto_save': True,
                'version_control': True
            }

@dataclass
class Message:
    """WebSocket message structure"""
    type: str  # join, leave, update, chat, cursor, selection
    user_id: str
    workspace_id: str
    data: Any
    timestamp: datetime = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now()
    
    def to_json(self) -> str:
        """Convert message to JSON"""
        return json.dumps({
            'type': self.type,
            'user_id': self.user_id,
            'workspace_id': self.workspace_id,
            'data': self.data,
            'timestamp': self.timestamp.isoformat()
        })

class CollaborationServer:
    """WebSocket server for real-time collaboration"""
    
    def __init__(self, host: str = "localhost", port: int = 8765):
        self.host = host
        self.port = port
        self.connections: Dict[str, WebSocketServerProtocol] = {}
        self.users: Dict[str, User] = {}
        self.workspaces: Dict[str, Workspace] = {}
        self.user_workspaces: Dict[str, str] = {}  # user_id -> workspace_id
        
    async def register_user(self, websocket: WebSocketServerProtocol, user_data: Dict):
        """Register a new user connection"""
        user = User(
            id=str(uuid.uuid4()),
            name=user_data.get('name', 'Anonymous'),
            email=user_data.get('email', 'anonymous@example.com'),
            role=user_data.get('role', 'viewer')
        )
        
        self.users[user.id] = user
        self.connections[user.id] = websocket
        
        logger.info(f"User {user.name} ({user.id}) connected")
        
        # Send user info back
        await websocket.send(json.dumps({
            'type': 'connected',
            'user': asdict(user),
            'timestamp': datetime.now().isoformat()
        }))
        
        return user
    
    async def unregister_user(self, user_id: str):
        """Unregister user connection"""
        if user_id in self.users:
            user = self.users[user_id]
            logger.info(f"User {user.name} ({user_id}) disconnected")
            
            # Remove from workspace
            if user_id in self.user_workspaces:
                workspace_id = self.user_workspaces[user_id]
                if workspace_id in self.workspaces:
                    workspace = self.workspaces[workspace_id]
                    workspace.active_users.discard(user_id)
                    
                    # Notify other users
                    await self.broadcast_to_workspace(
                        workspace_id,
                        Message(
                            type='user_left',
                            user_id=user_id,
                            workspace_id=workspace_id,
                            data={'user': asdict(user)}
                        ),
                        exclude_user=user_id
                    )
                
                del self.user_workspaces[user_id]
            
            # Clean up
            del self.users[user_id]
            if user_id in self.connections:
                del self.connections[user_id]
    
    async def join_workspace(self, user_id: str, workspace_id: str) -> bool:
        """User joins a workspace"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        
        # Create workspace if doesn't exist
        if workspace_id not in self.workspaces:
            workspace = Workspace(
                id=workspace_id,
                name=f"Workspace {workspace_id[:8]}",
                owner_id=user_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                data={},
                active_users={user_id},
                settings={}
            )
            self.workspaces[workspace_id] = workspace
        else:
            workspace = self.workspaces[workspace_id]
            
            # Check permissions
            if len(workspace.active_users) >= workspace.settings.get('max_users', 10):
                return False
            
            workspace.active_users.add(user_id)
        
        self.user_workspaces[user_id] = workspace_id
        
        # Notify all users in workspace
        await self.broadcast_to_workspace(
            workspace_id,
            Message(
                type='user_joined',
                user_id=user_id,
                workspace_id=workspace_id,
                data={
                    'user': asdict(user),
                    'active_users': list(workspace.active_users),
                    'workspace': {
                        'id': workspace.id,
                        'name': workspace.name,
                        'owner_id': workspace.owner_id,
                        'settings': workspace.settings
                    }
                }
            )
        )
        
        logger.info(f"User {user.name} joined workspace {workspace_id}")
        return True
    
    async def broadcast_to_workspace(
        self, 
        workspace_id: str, 
        message: Message,
        exclude_user: Optional[str] = None
    ):
        """Broadcast message to all users in workspace"""
        if workspace_id not in self.workspaces:
            return
        
        workspace = self.workspaces[workspace_id]
        message_json = message.to_json()
        
        # Send to all active users
        for user_id in workspace.active_users:
            if user_id != exclude_user and user_id in self.connections:
                try:
                    await self.connections[user_id].send(message_json)
                except Exception as e:
                    logger.error(f"Error sending to user {user_id}: {e}")
    
    async def handle_data_update(self, user_id: str, update_data: Dict):
        """Handle data update from user"""
        if user_id not in self.user_workspaces:
            return
        
        workspace_id = self.user_workspaces[user_id]
        if workspace_id not in self.workspaces:
            return
        
        workspace = self.workspaces[workspace_id]
        
        # Check permissions
        user = self.users[user_id]
        if user.role not in ['editor', 'admin', 'owner']:
            return
        
        # Update workspace data
        update_type = update_data.get('type', 'general')
        
        if update_type == 'data':
            workspace.data.update(update_data.get('data', {}))
        elif update_type == 'analysis':
            if 'analysis_results' not in workspace.data:
                workspace.data['analysis_results'] = {}
            workspace.data['analysis_results'].update(update_data.get('results', {}))
        elif update_type == 'visualization':
            if 'visualizations' not in workspace.data:
                workspace.data['visualizations'] = []
            workspace.data['visualizations'].append(update_data.get('chart', {}))
        
        workspace.updated_at = datetime.now()
        
        # Broadcast update to all users
        await self.broadcast_to_workspace(
            workspace_id,
            Message(
                type='data_update',
                user_id=user_id,
                workspace_id=workspace_id,
                data={
                    'update_type': update_type,
                    'update': update_data,
                    'user': asdict(user)
                }
            ),
            exclude_user=user_id
        )
    
    async def handle_cursor_update(self, user_id: str, cursor_data: Dict):
        """Handle cursor position update"""
        if user_id not in self.user_workspaces:
            return
        
        workspace_id = self.user_workspaces[user_id]
        
        # Broadcast cursor position to others
        await self.broadcast_to_workspace(
            workspace_id,
            Message(
                type='cursor_update',
                user_id=user_id,
                workspace_id=workspace_id,
                data=cursor_data
            ),
            exclude_user=user_id
        )
    
    async def handle_chat_message(self, user_id: str, chat_data: Dict):
        """Handle chat message"""
        if user_id not in self.user_workspaces:
            return
        
        workspace_id = self.user_workspaces[user_id]
        user = self.users[user_id]
        
        # Broadcast chat message
        await self.broadcast_to_workspace(
            workspace_id,
            Message(
                type='chat',
                user_id=user_id,
                workspace_id=workspace_id,
                data={
                    'message': chat_data.get('message', ''),
                    'user': asdict(user)
                }
            )
        )
    
    async def handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Handle client connection"""
        user_id = None
        
        try:
            # Wait for registration
            registration = await websocket.recv()
            reg_data = json.loads(registration)
            
            if reg_data.get('type') == 'register':
                user = await self.register_user(websocket, reg_data.get('user', {}))
                user_id = user.id
                
                # Join workspace if specified
                workspace_id = reg_data.get('workspace_id')
                if workspace_id:
                    await self.join_workspace(user_id, workspace_id)
            
            # Handle messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    msg_type = data.get('type')
                    
                    if msg_type == 'join_workspace':
                        await self.join_workspace(user_id, data.get('workspace_id'))
                    
                    elif msg_type == 'data_update':
                        await self.handle_data_update(user_id, data.get('data', {}))
                    
                    elif msg_type == 'cursor':
                        await self.handle_cursor_update(user_id, data.get('cursor', {}))
                    
                    elif msg_type == 'chat':
                        await self.handle_chat_message(user_id, data.get('chat', {}))
                    
                    elif msg_type == 'ping':
                        # Update last activity
                        if user_id in self.users:
                            self.users[user_id].last_activity = datetime.now()
                        await websocket.send(json.dumps({'type': 'pong'}))
                    
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON from user {user_id}")
                except Exception as e:
                    logger.error(f"Error handling message from {user_id}: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Error in client handler: {e}")
        finally:
            if user_id:
                await self.unregister_user(user_id)
    
    async def start(self):
        """Start the WebSocket server"""
        if not websockets:
            logger.error("websockets library not installed. Install with: pip install websockets")
            return
        
        logger.info(f"Starting collaboration server on {self.host}:{self.port}")
        
        async with websockets.serve(self.handle_client, self.host, self.port):
            logger.info(f"Server running on ws://{self.host}:{self.port}")
            await asyncio.Future()  # Run forever

def main():
    """Run the collaboration server"""
    server = CollaborationServer(host="0.0.0.0", port=8765)
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        logger.info("Server stopped")

if __name__ == "__main__":
    main()