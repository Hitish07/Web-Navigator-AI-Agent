import json
import re
from typing import List, Dict, Any
from src.llm.ollama_client import OllamaClient
from src.llm.prompt_templates import PromptTemplates

class TaskPlanner:
    def __init__(self):
        self.llm = OllamaClient()
    
    def parse_user_instruction(self, user_input: str) -> List[Dict[str, Any]]:
        """Parse natural language instruction into browser actions"""
        planning_prompt = PromptTemplates.get_planning_prompt(user_input)
        
        try:
            # Get plan from LLM
            plan_response = self.llm.generate(planning_prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', plan_response, re.DOTALL)
            if json_match:
                actions_json = json_match.group()
                actions = json.loads(actions_json)
                return self._validate_actions(actions)
            else:
                # Fallback plan for common queries
                return self._create_fallback_plan(user_input)
                
        except Exception as e:
            print(f"Planning error: {e}")
            return self._create_fallback_plan(user_input)
    
    def _validate_actions(self, actions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and fix action parameters"""
        validated_actions = []
        
        for action in actions:
            # Ensure required fields exist
            if "action" not in action:
                continue
                
            # Add missing description
            if "description" not in action:
                action["description"] = f"Perform {action['action']} action"
            
            # Ensure extract actions have a selector
            if action["action"] == "extract" and "selector" not in action:
                action["selector"] = ".g, .rc, .tF2Cxc"
            
            validated_actions.append(action)
        
        return validated_actions if validated_actions else self._create_fallback_plan("search")
    
    def _create_fallback_plan(self, user_input: str) -> List[Dict[str, Any]]:
        """Create a basic plan when LLM parsing fails"""
        search_query = self._clean_search_query(user_input)
        
        return [
            {
                "action": "navigate",
                "value": "https://www.google.com",
                "description": "Navigate to Google search"
            },
            {
                "action": "type",
                "selector": "textarea[name='q'], input[name='q']",
                "value": search_query,
                "description": f"Type search query: {search_query}"
            },
            {
                "action": "click", 
                "selector": "input[value='Google Search'], button[type='submit']",
                "description": "Execute search"
            },
            {
                "action": "wait",
                "value": "5000",
                "description": "Wait for results to load"
            },
            {
                "action": "extract",
                "selector": ".g, .rc, .tF2Cxc, .MjjYud",
                "description": "Extract search results"
            }
        ]
    
    def _clean_search_query(self, user_input: str) -> str:
        """Clean and optimize the search query"""
        # Remove common command phrases
        phrases_to_remove = [
            "search for", "find", "look up", "show me", "list", 
            "give me", "what is", "who is", "where is"
        ]
        
        query = user_input.lower()
        for phrase in phrases_to_remove:
            query = query.replace(phrase, "")
        
        # Clean up the query
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query