#!/usr/bin/env python3
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich import print as rprint
from src.chat.chat_manager import ChatManager
import sys

class ConsoleChat:
    def __init__(self):
        self.console = Console()
        self.chat_manager = ChatManager()
        self.current_conv_id = None
    
    def display_welcome(self):
        """Display welcome message"""
        welcome_text = """
# 🤖 Web Navigator AI Chat Assistant

I combine AI chat with web browsing capabilities. I can search the web for you and provide summarized results!

**Commands:**
- Type your message to chat
- `new` - Start new conversation
- `list` - Show conversations
- `exit` or `quit` - Exit the program
- `help` - Show this help message
"""
        self.console.print(Panel(Markdown(welcome_text), style="blue"))
    
    def display_message(self, role: str, content: str, is_markdown: bool = True):
        """Display a message in the console"""
        if role == "user":
            style = "green"
            prefix = "👤 You"
        else:
            style = "cyan"
            prefix = "🤖 Assistant"
        
        if is_markdown and role == "assistant":
            content = Markdown(content)
        
        panel = Panel(
            content,
            title=f"[b]{prefix}[/b]",
            title_align="left",
            style=style,
            border_style=style
        )
        self.console.print(panel)
    
    def start_chat(self):
        """Start the chat interface"""
        self.display_welcome()
        
        # Start first conversation
        self.current_conv_id = self.chat_manager.start_new_conversation()
        conversation = self.chat_manager.get_current_conversation()
        
        # Display welcome message
        if conversation and conversation.messages:
            self.display_message("assistant", conversation.messages[0]["content"])
        
        while True:
            try:
                # Get user input
                user_input = Prompt.ask("\n[bold yellow]💬 Your message[/bold yellow]")
                
                # Handle commands
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.console.print("[yellow]👋 Goodbye![/yellow]")
                    break
                
                elif user_input.lower() == 'new':
                    self.current_conv_id = self.chat_manager.start_new_conversation()
                    conversation = self.chat_manager.get_current_conversation()
                    if conversation and conversation.messages:
                        self.display_message("assistant", conversation.messages[0]["content"])
                    continue
                
                elif user_input.lower() == 'list':
                    self._show_conversations()
                    continue
                
                elif user_input.lower() == 'help':
                    self.display_welcome()
                    continue
                
                # Process the message
                self.display_message("user", user_input, is_markdown=False)
                
                # Show typing indicator
                with self.console.status("[bold green]Thinking...", spinner="dots"):
                    result = self.chat_manager.process_message(user_input, self.current_conv_id)
                
                # Display response
                self.display_message("assistant", result["response"])
                
                # Show metadata if available
                if result.get("type") == "web_navigation":
                    if result.get("success"):
                        self.console.print(f"[green]✓ Web search completed successfully[/green]")
                    else:
                        self.console.print(f"[red]✗ Web search failed[/red]")
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]👋 Goodbye![/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def _show_conversations(self):
        """Show list of conversations"""
        conversations = self.chat_manager.get_conversation_list()
        
        if not conversations:
            self.console.print("[yellow]No conversations found.[/yellow]")
            return
        
        self.console.print("\n[bold]📚 Your Conversations:[/bold]")
        for i, conv in enumerate(conversations, 1):
            self.console.print(
                f"{i}. {conv['id']} "
                f"(Messages: {conv['message_count']}, "
                f"Updated: {conv['updated_at'][:19]})"
            )

def main():
    chat = ConsoleChat()
    chat.start_chat()

if __name__ == "__main__":
    main()