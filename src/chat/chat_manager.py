from typing import Dict, List, Optional
from src.orchestrator.agent import WebNavigatorAgent
from src.chat.conversation import Conversation
from src.llm.ollama_client import OllamaClient

class ChatManager:
    def __init__(self):
        self.agent = WebNavigatorAgent()
        self.llm = OllamaClient()
        self.conversations: Dict[str, Conversation] = {}
        self.current_conversation_id: Optional[str] = None
    
    def start_new_conversation(self) -> str:
        """Start a new conversation and return its ID"""
        conversation = Conversation()
        self.conversations[conversation.conversation_id] = conversation
        self.current_conversation_id = conversation.conversation_id
        
        # Add welcome message
        welcome_msg = """🤖 **Web Navigator AI Assistant**

I can help you with:
- Searching the web for information
- Finding products and prices
- Getting latest news and updates
- Researching topics

Just tell me what you'd like me to search for!"""
        
        conversation.add_assistant_message(welcome_msg)
        return conversation.conversation_id
    
    def get_current_conversation(self) -> Optional[Conversation]:
        """Get the current conversation"""
        if self.current_conversation_id and self.current_conversation_id in self.conversations:
            return self.conversations[self.current_conversation_id]
        return None
    
    def process_message(self, user_input: str, conversation_id: str = None) -> Dict[str, any]:
        """Process a user message and return the response"""
        # Get or create conversation
        if conversation_id and conversation_id in self.conversations:
            conversation = self.conversations[conversation_id]
            self.current_conversation_id = conversation_id
        else:
            conversation_id = self.start_new_conversation()
            conversation = self.conversations[conversation_id]
        
        # Add user message to conversation
        conversation.add_user_message(user_input)
        
        # Determine if this is a web navigation request
        if self._is_web_navigation_request(user_input):
            return self._handle_web_navigation(user_input, conversation)
        else:
            return self._handle_chat_message(user_input, conversation)
    
    def _is_web_navigation_request(self, user_input: str) -> bool:
        """Determine if the user wants web navigation"""
        navigation_keywords = [
            'search', 'find', 'look up', 'browse', 'navigate',
            'google', 'website', 'web', 'internet', 'online',
            'price', 'buy', 'shop', 'product', 'laptop', 'phone'
        ]
        
        user_input_lower = user_input.lower()
        return any(keyword in user_input_lower for keyword in navigation_keywords)
    
    # def _handle_web_navigation(self, user_input: str, conversation: Conversation) -> Dict[str, any]:
    #     """Handle web navigation requests"""
    #     try:
    #         # Show typing indicator
    #         thinking_msg = "🔍 Searching the web for you..."
    #         conversation.add_assistant_message(thinking_msg)
            
    #         # Execute the web navigation task
    #         result = self.agent.execute_task(user_input)
            
    #         if result["success"]:
    #             response = f"✅ **Search Completed**\n\n{result['final_summary']}\n\n*Search executed in {len(result.get('execution_log', []))} steps*"
                
    #             # Add metadata about the search
    #             metadata = {
    #                 "type": "web_navigation",
    #                 "success": True,
    #                 "actions_count": result.get("actions_executed", 0),
    #                 "has_data": "No data" not in result.get("extracted_data", "")
    #             }
    #         else:
    #             response = f"❌ **Search Failed**\n\nSorry, I couldn't complete your search. Error: {result.get('error', 'Unknown error')}"
    #             metadata = {"type": "web_navigation", "success": False}
            
    #         # Update the last message with actual results
    #         conversation.messages[-1]["content"] = response
    #         conversation.messages[-1]["metadata"] = metadata
            
    #         return {
    #             "conversation_id": conversation.conversation_id,
    #             "response": response,
    #             "type": "web_navigation",
    #             "success": result.get("success", False),
    #             "metadata": metadata
    #         }
            
    #     except Exception as e:
    #         error_response = f"❌ **Error**\n\nSorry, I encountered an error: {str(e)}"
    #         conversation.add_assistant_message(error_response, {"type": "error"})
            
    #         return {
    #             "conversation_id": conversation.conversation_id,
    #             "response": error_response,
    #             "type": "error",
    #             "success": False,
    #             "metadata": {"type": "error"}
    #         }
    # Add this method to the ChatManager class

    def _handle_web_navigation(self, user_input: str, conversation: Conversation) -> Dict[str, any]:
        """Handle web navigation requests with file output support"""
        try:
            # Show typing indicator
            thinking_msg = "🔍 Searching the web for you..."
            conversation.add_assistant_message(thinking_msg)
            
            # Execute the web navigation task
            result = self.agent.execute_task(user_input)
            
            if result["success"]:
                # Build response message
                response_text = result['final_summary']
                
                # Add metadata about the search
                metadata = {
                    "type": "web_navigation",
                    "success": True,
                    "actions_count": result.get("actions_executed", 0),
                    "has_data": "No data" not in result.get("extracted_data", ""),
                    "file_created": result.get("file_created", False),
                    "output_format": result.get("output_format", "text")
                }
                
                # Add file information if file was created
                if result.get("file_created"):
                    metadata["file_path"] = result["file_path"]
                    metadata["file_name"] = result["file_name"]
                    metadata["output_format"] = result["output_format"]
                
            else:
                response_text = f"❌ **Search Failed**\n\nSorry, I couldn't complete your search. Error: {result.get('error', 'Unknown error')}"
                metadata = {"type": "web_navigation", "success": False}
            
            # Update the last message with actual results
            conversation.messages[-1]["content"] = response_text
            conversation.messages[-1]["metadata"] = metadata
            
            # Prepare return data with file information
            return_data = {
                "conversation_id": conversation.conversation_id,
                "response": response_text,
                "type": "web_navigation",
                "success": result.get("success", False),
                "metadata": metadata
            }
            
            # Add file information to return data if file was created
            if result.get("file_created"):
                return_data["file_created"] = True
                return_data["file_path"] = result["file_path"]
                return_data["file_name"] = result["file_name"]
                return_data["output_format"] = result["output_format"]
            
            return return_data
            
        except Exception as e:
            error_response = f"❌ **Error**\n\nSorry, I encountered an error: {str(e)}"
            conversation.add_assistant_message(error_response, {"type": "error"})
            
            return {
                "conversation_id": conversation.conversation_id,
                "response": error_response,
                "type": "error",
                "success": False,
                "metadata": {"type": "error"}
            }
    
    def _handle_chat_message(self, user_input: str, conversation: Conversation) -> Dict[str, any]:
        """Handle regular chat messages"""
        try:
            # Create context from conversation history
            context = self._create_chat_context(conversation)
            
            prompt = f"""You are a helpful AI assistant that can also browse the web. 
            
Current conversation context:
{context}

User's latest message: {user_input}

Respond helpfully. If the user seems to want information that might require web search, suggest searching for them.
Keep responses concise and friendly."""

            response = self.llm.generate(prompt)
            
            conversation.add_assistant_message(response, {"type": "chat"})
            
            return {
                "conversation_id": conversation.conversation_id,
                "response": response,
                "type": "chat",
                "success": True,
                "metadata": {"type": "chat"}
            }
            
        except Exception as e:
            error_response = f"I apologize, but I'm having trouble responding right now. Error: {str(e)}"
            conversation.add_assistant_message(error_response, {"type": "error"})
            
            return {
                "conversation_id": conversation.conversation_id,
                "response": error_response,
                "type": "error",
                "success": False
            }
    
    def _create_chat_context(self, conversation: Conversation, max_messages: int = 6) -> str:
        """Create context from conversation history"""
        messages = conversation.get_conversation_history(max_messages)
        context = []
        
        for msg in messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            context.append(f"{role}: {msg['content']}")
        
        return "\n".join(context)
    
    def get_conversation_list(self) -> List[Dict]:
        """Get list of all conversations"""
        return [
            {
                "id": conv_id,
                "created_at": conv.created_at.isoformat(),
                "updated_at": conv.updated_at.isoformat(),
                "message_count": len(conv.messages)
            }
            for conv_id, conv in self.conversations.items()
        ]
    
    def switch_conversation(self, conversation_id: str) -> bool:
        """Switch to a different conversation"""
        if conversation_id in self.conversations:
            self.current_conversation_id = conversation_id
            return True
        return False
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation"""
        if conversation_id in self.conversations:
            if self.current_conversation_id == conversation_id:
                self.current_conversation_id = None
            del self.conversations[conversation_id]
            return True
        return False

