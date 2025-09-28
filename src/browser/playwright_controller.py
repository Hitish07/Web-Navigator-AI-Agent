from playwright.sync_api import sync_playwright
import json
import time
from typing import List, Dict, Any
from config.settings import settings

class PlaywrightController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
    
    def start_browser(self):
        """Start the browser instance"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=settings.BROWSER_HEADLESS
        )
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        self.page = self.context.new_page()
    
    def execute_action(self, action: Dict[str, Any]) -> str:
        """Execute a single browser action with proper error handling"""
        action_type = action["action"]
        result = ""
        
        try:
            if action_type == "navigate":
                url = action["value"]
                if not url.startswith(('http://', 'https://')):
                    url = 'https://' + url
                self.page.goto(url, wait_until="domcontentloaded")
                result = f"Navigated to {url}"
            
            elif action_type == "type":
                selector = action.get("selector", "textarea[name='q'], input[name='q']")
                value = action.get("value", "")
                self.page.fill(selector, value)
                result = f"Typed '{value}' into {selector}"
            
            elif action_type == "click":
                selector = action.get("selector", "input[value='Google Search'], button[type='submit']")
                self.page.click(selector)
                result = f"Clicked on {selector}"
            
            elif action_type == "wait":
                wait_time = int(action.get("value", "2000"))
                time.sleep(wait_time / 1000)
                result = f"Waited for {wait_time}ms"
            
            elif action_type == "extract":
                selector = action.get("selector", ".g, .rc, .tF2Cxc, .MjjYud, .sh-dlr__content")
                result = self.extract_google_results(selector)
            
            elif action_type == "scroll":
                self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                result = "Scrolled to bottom"
            
            else:
                result = f"Unknown action: {action_type}"
        
        except Exception as e:
            result = f"Error executing {action_type}: {str(e)}"
        
        return result
    
    def extract_google_results(self, selector: str = None) -> str:
        """Extract Google search results with multiple fallback strategies"""
        try:
            # Wait for results to load
            self.page.wait_for_timeout(3000)
            
            # Strategy 1: Try the provided selector
            if selector and selector.strip():
                result = self._extract_with_selector(selector)
                if result and "No data found" not in result:
                    return result
            
            # Strategy 2: Try common Google result selectors
            common_selectors = [
                ".g", ".rc", ".tF2Cxc", ".MjjYud",  # Organic results
                ".sh-dlr__content", ".pla-unit",    # Shopping results
                ".i0X6df", ".KZmu8e",              # More shopping
                "[data-sokoban-container]",         # Google container
                ".hlcw0c", ".yuRUbf"               # Additional containers
            ]
            
            for sel in common_selectors:
                result = self._extract_with_selector(sel)
                if result and "No data found" not in result:
                    return f"Found with selector '{sel}':\n{result}"
            
            # Strategy 3: Extract visible text from main content
            return self._extract_visible_text()
            
        except Exception as e:
            return f"Extraction error: {str(e)}"
    
    def _extract_with_selector(self, selector: str) -> str:
        """Extract data using a specific CSS selector"""
        try:
            elements = self.page.query_selector_all(selector)
            if not elements:
                return "No data found"
            
            extracted_data = []
            for i, element in enumerate(elements[:10]):  # Limit to first 10 elements
                try:
                    text = element.inner_text().strip()
                    if text and len(text) > 20:  # Filter out very short texts
                        extracted_data.append(f"Result {i+1}: {text}")
                except:
                    continue
            
            return "\n".join(extracted_data) if extracted_data else "No data found"
        
        except Exception as e:
            return f"Selector error: {str(e)}"
    
    def _extract_visible_text(self) -> str:
        """Extract visible text from the main content area"""
        try:
            # Try to get text from main content areas
            content_selectors = ["#search", "#rso", "#center_col", "main", "body"]
            
            for selector in content_selectors:
                element = self.page.query_selector(selector)
                if element:
                    text = element.inner_text().strip()
                    if len(text) > 100:  # Meaningful content
                        # Clean up the text
                        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 30]
                        return "Visible text content:\n" + "\n".join(lines[:15])
            
            return "No extractable content found"
        
        except Exception as e:
            return f"Visible text extraction error: {str(e)}"
    
    def close(self):
        """Close browser resources"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()