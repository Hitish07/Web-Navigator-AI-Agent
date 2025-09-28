class PromptTemplates:
    @staticmethod
    def get_planning_prompt(user_input: str) -> str:
        return f"""
        Analyze the user's web navigation request and break it down into specific browser actions.
        User Request: "{user_input}"
        
        Return a JSON array of actions. Each action MUST have:
        - "action": type of action (navigate, click, type, wait, extract, scroll)
        - "selector": CSS selector or XPath (REQUIRED for extract actions)
        - "value": input value or parameter (if applicable)
        - "description": human-readable description
        
        IMPORTANT: For extract actions, ALWAYS include a valid CSS selector.
        
        Example for "search for laptops under 50k":
        [
            {{
                "action": "navigate",
                "value": "https://www.google.com",
                "description": "Navigate to Google search"
            }},
            {{
                "action": "type",
                "selector": "textarea[name='q'], input[name='q']",
                "value": "laptops under 50000",
                "description": "Type search query"
            }},
            {{
                "action": "click",
                "selector": "input[value='Google Search'], button[type='submit']",
                "description": "Click search button"
            }},
            {{
                "action": "wait",
                "value": "5000",
                "description": "Wait for results to load"
            }},
            {{
                "action": "extract",
                "selector": ".g, .rc, .tF2Cxc",
                "description": "Extract search results"
            }}
        ]
        
        Return only valid JSON:
        """

    @staticmethod
    def get_summarization_prompt(data: str, original_query: str) -> str:
        return f"""
        Original user query: "{original_query}"
        
        Extracted web data: {data}
        
        Summarize and structure this information to answer the user's query.
        Focus on providing clear, concise, and relevant information.
        
        Provide the final answer in a well-formatted way:
        """