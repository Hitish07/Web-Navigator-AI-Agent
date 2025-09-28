from datetime import datetime
from typing import List, Dict, Any

class Conversation:
    def __init__(self, conversation_id: str = None):
        self.conversation_id = conversation_id or f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.messages: List[Dict[str, Any]] = []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the conversation"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    def add_user_message(self, content: str):
        """Add a user message"""
        self.add_message("user", content)
    
    def add_assistant_message(self, content: str, metadata: Dict = None):
        """Add an assistant message"""
        self.add_message("assistant", content, metadata)
    
    def get_conversation_history(self, limit: int = None) -> List[Dict]:
        """Get conversation history"""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def get_last_user_message(self) -> str:
        """Get the last user message"""
        for message in reversed(self.messages):
            if message["role"] == "user":
                return message["content"]
        return ""
    
    def clear(self):
        """Clear the conversation"""
        self.messages.clear()
        self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """Convert conversation to dictionary"""
        return {
            "conversation_id": self.conversation_id,
            "messages": self.messages,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "message_count": len(self.messages)
        }