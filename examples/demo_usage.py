from src.orchestrator.agent import WebNavigatorAgent

def demo():
    """Demo the Web Navigator Agent with sample queries"""
    agent = WebNavigatorAgent()
    
    sample_queries = [
        "search for latest AI news",
        "find weather in New York",
        "search for python programming tutorials",
    ]
    
    for query in sample_queries:
        print(f"\n{'='*60}")
        print(f"DEMO: {query}")
        print(f"{'='*60}")
        
        result = agent.execute_task(query)
        
        if result["success"]:
            print("SUCCESS!")
            print(f"Summary: {result['final_summary'][:200]}...")
        else:
            print(f"FAILED: {result['error']}")
        
        print(f"{'='*60}\n")

if __name__ == "__main__":
    demo()
