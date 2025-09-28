# from typing import Dict, Any
# from src.browser.playwright_controller import PlaywrightController
# from src.orchestrator.task_planner import TaskPlanner
# from src.processing.summarizer import Summarizer

# class WebNavigatorAgent:
#     def __init__(self):
#         self.planner = TaskPlanner()
#         self.browser = PlaywrightController()
#         self.summarizer = Summarizer()
    
#     def execute_task(self, user_input: str) -> Dict[str, Any]:
#         """Main method to execute complete web navigation task"""
#         print(f"Processing: {user_input}")
        
#         # Step 1: Plan the actions
#         print("Planning actions...")
#         actions = self.planner.parse_user_instruction(user_input)
#         print(f"Planned {len(actions)} actions")
        
#         # Step 2: Initialize browser
#         print("Starting browser...")
#         self.browser.start_browser()
        
#         execution_log = []
#         extracted_data = ""
        
#         try:
#             # Step 3: Execute browser actions
#             for i, action in enumerate(actions):
#                 print(f"Executing action {i+1}: {action['description']}")
#                 result = self.browser.execute_action(action)
#                 execution_log.append({
#                     "action": action,
#                     "result": result
#                 })
                
#                 # Store extraction results
#                 if action["action"] == "extract":
#                     extracted_data = result
            
#             # Step 4: Process and summarize results
#             print("Summarizing results...")
#             final_summary = self.summarizer.summarize_results(extracted_data, user_input)
            
#             return {
#                 "success": True,
#                 "original_query": user_input,
#                 "actions_executed": len(actions),
#                 "extracted_data": extracted_data,
#                 "final_summary": final_summary,
#                 "execution_log": execution_log
#             }
            
#         except Exception as e:
#             return {
#                 "success": False,
#                 "error": str(e),
#                 "execution_log": execution_log
#             }
#         finally:
#             # Step 5: Cleanup
#             self.browser.close()
#             print("Browser closed.")

from typing import Dict, Any
import os
from src.browser.playwright_controller import PlaywrightController
from src.orchestrator.task_planner import TaskPlanner
from src.processing.summarizer import Summarizer

class WebNavigatorAgent:
    def __init__(self, output_dir: str = "outputs"):
        self.planner = TaskPlanner()
        self.browser = PlaywrightController()
        self.summarizer = Summarizer(output_dir)
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute_task(self, user_input: str) -> Dict[str, Any]:
        """Main method to execute complete web navigation task"""
        print(f"Processing: {user_input}")
        
        # Step 1: Plan the actions
        print("Planning actions...")
        actions = self.planner.parse_user_instruction(user_input)
        print(f"Planned {len(actions)} actions")
        
        # Step 2: Initialize browser
        print("Starting browser...")
        self.browser.start_browser()
        
        execution_log = []
        extracted_data = ""
        
        try:
            # Step 3: Execute browser actions
            for i, action in enumerate(actions):
                print(f"Executing action {i+1}: {action['description']}")
                result = self.browser.execute_action(action)
                execution_log.append({
                    "action": action,
                    "result": result
                })
                
                # Store extraction results
                if action["action"] == "extract":
                    extracted_data = result
            
            # Step 4: Process and summarize results
            print("Summarizing results...")
            summary_result = self.summarizer.summarize_results(extracted_data, user_input)
            
            response = {
                "success": True,
                "original_query": user_input,
                "actions_executed": len(actions),
                "extracted_data": extracted_data,
                "final_summary": summary_result["text"],
                "output_format": summary_result["format"],
                "execution_log": execution_log
            }
            
            # Add file information if file was created
            if summary_result["file_path"]:
                response["file_path"] = summary_result["file_path"]
                response["file_created"] = True
                response["file_name"] = os.path.basename(summary_result["file_path"])
            else:
                response["file_created"] = False
            
            return response
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "execution_log": execution_log,
                "file_created": False
            }
        finally:
            # Step 5: Cleanup
            self.browser.close()
            print("Browser closed.")