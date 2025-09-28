# from src.llm.ollama_client import OllamaClient

# class Summarizer:
#     def __init__(self):
#         self.llm = OllamaClient()
    
#     def summarize_results(self, extracted_data: str, original_query: str) -> str:
#         """Summarize extracted data with better shopping result handling"""
#         if not extracted_data or "No results" in extracted_data:
#             return self._create_fallback_response(extracted_data, original_query)
        
#         # Use specialized prompts for shopping queries
#         if any(word in original_query.lower() for word in ['laptop', 'phone', 'buy', 'price', 'product']):
#             summary = self._summarize_shopping_results(extracted_data, original_query)
#         else:
#             summary = self._summarize_general_results(extracted_data, original_query)
        
#         return summary if summary else self._create_structured_fallback(extracted_data, original_query)
    
#     def _summarize_shopping_results(self, extracted_data: str, original_query: str) -> str:
#         """Specialized summarization for shopping results"""
#         prompt = f"""Analyze these product search results for: "{original_query}"

# Extracted data:
# {extracted_data[:2000]}

# Please provide a structured summary with:
# 1. Top 5 products found
# 2. Prices for each product
# 3. Key specifications if available
# 4. Where to buy (store/source)
# 5. Ratings if available

# Format the response clearly with product rankings:"""
        
#         try:
#             return self.llm.generate(prompt, max_tokens=800)
#         except:
#             return None
    
#     def _summarize_general_results(self, extracted_data: str, original_query: str) -> str:
#         """General summarization for non-shopping queries"""
#         prompt = f"""Summarize these search results for: "{original_query}"

# Search results:
# {extracted_data[:2000]}

# Provide a concise summary focusing on the most relevant information:"""
        
#         try:
#             return self.llm.generate(prompt, max_tokens=1024)
#         except:
#             return None
    
#     def _create_fallback_response(self, extracted_data: str, original_query: str) -> str:
#         """Create a response when no data is found"""
#         if "Error" in extracted_data:
#             return f"I encountered an error while searching for '{original_query}'. The search may have been blocked or the page structure may have changed."
        
#         return f"Sorry, I couldn't find any relevant information for '{original_query}'. The search might need different search terms or the results may not be accessible."
    
#     def _create_structured_fallback(self, extracted_data: str, original_query: str) -> str:
#         """Create a structured fallback when LLM summarization fails"""
#         lines = extracted_data.split('\n')
#         relevant_lines = [line for line in lines if len(line.strip()) > 20]
        
#         if relevant_lines:
#             return f"Here's what I found for '{original_query}':\n\n" + "\n".join(relevant_lines[:10])
#         else:
#             return f"I found some information for '{original_query}' but couldn't process it properly. The raw data suggests results were found but in an unexpected format."
import os
import json
import re
from datetime import datetime
from src.llm.ollama_client import OllamaClient

class Summarizer:
    def __init__(self, output_dir: str = "outputs"):
        self.llm = OllamaClient()
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)
    
    def summarize_results(self, extracted_data: str, original_query: str) -> dict:
        """Summarize extracted data and return both text and file info"""
        if not extracted_data or "No results" in extracted_data:
            fallback_text = self._create_fallback_response(extracted_data, original_query)
            return {
                "text": fallback_text,
                "file_path": None,
                "format": "text"
            }
        
        # Check if user requested file format
        output_format = self._detect_output_format(original_query)
        
        # Use specialized prompts based on query type and format
        if any(word in original_query.lower() for word in ['laptop', 'phone', 'buy', 'price', 'product']):
            result = self._summarize_shopping_results(extracted_data, original_query, output_format)
        else:
            result = self._summarize_general_results(extracted_data, original_query, output_format)
        
        return result if result else self._create_structured_fallback(extracted_data, original_query, output_format)
    
    def _detect_output_format(self, query: str) -> str:
        """Detect if user wants output in specific file format"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['json', 'file', 'export', 'download', 'save']):
            if 'json' in query_lower:
                return 'json'
            elif 'csv' in query_lower:
                return 'csv'
            elif 'pdf' in query_lower:
                return 'pdf'
            elif 'txt' in query_lower or 'text' in query_lower:
                return 'txt'
            else:
                return 'json'  # default file format
        
        return 'text'  # plain text output
    
    def _summarize_shopping_results(self, extracted_data: str, original_query: str, output_format: str) -> dict:
        """Specialized summarization for shopping results"""
        if output_format == 'text':
            prompt = f"""Analyze these product search results for: "{original_query}"

Extracted data:
{extracted_data[:2000]}

Please provide a structured summary with:
1. Top 5 products found
2. Prices for each product
3. Key specifications if available
4. Where to buy (store/source)
5. Ratings if available

Format the response clearly with product rankings:"""
            
            try:
                summary_text = self.llm.generate(prompt, max_tokens=800)
                return {
                    "text": summary_text,
                    "file_path": None,
                    "format": "text"
                }
            except:
                return None
        else:
            # File format requested
            return self._create_shopping_file(extracted_data, original_query, output_format)
    
    def _summarize_general_results(self, extracted_data: str, original_query: str, output_format: str) -> dict:
        """General summarization for non-shopping queries"""
        if output_format == 'text':
            prompt = f"""Summarize these search results for: "{original_query}"

Search results:
{extracted_data[:2000]}

Provide a concise summary focusing on the most relevant information:"""
            
            try:
                summary_text = self.llm.generate(prompt, max_tokens=1024)
                return {
                    "text": summary_text,
                    "file_path": None,
                    "format": "text"
                }
            except:
                return None
        else:
            # File format requested
            return self._create_general_file(extracted_data, original_query, output_format)
    
    def _create_shopping_file(self, extracted_data: str, original_query: str, format_type: str) -> dict:
        """Create structured file for shopping results"""
        try:
            # Extract product information using LLM
            prompt = f"""Extract product information from this data and return ONLY valid JSON:

Query: "{original_query}"
Data: {extracted_data[:2000]}

Return JSON format:
{{
    "query": "original query",
    "products": [
        {{
            "name": "product name",
            "price": "price",
            "rating": "rating",
            "store": "store/source",
            "specifications": "key specs"
        }}
    ],
    "summary": "brief overall summary"
}}

Extract maximum 5 products:"""
            
            json_response = self.llm.generate(prompt, max_tokens=1000)
            
            # Clean and parse JSON
            json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
            if json_match:
                products_data = json.loads(json_match.group())
                file_path = self._save_to_file(products_data, original_query, format_type)
                
                summary_text = f"✅ I've found {len(products_data.get('products', []))} products and saved the results to a {format_type.upper()} file.\n\n"
                summary_text += products_data.get('summary', 'Results have been exported successfully.')
                
                return {
                    "text": summary_text,
                    "file_path": file_path,
                    "format": format_type,
                    "data": products_data
                }
        
        except Exception as e:
            print(f"File creation error: {e}")
        
        return None
    
    def _create_general_file(self, extracted_data: str, original_query: str, format_type: str) -> dict:
        """Create structured file for general results"""
        try:
            prompt = f"""Extract key information from this search data and return ONLY valid JSON:

Query: "{original_query}"
Data: {extracted_data[:2000]}

Return JSON format:
{{
    "query": "original query",
    "results": [
        {{
            "title": "result title",
            "description": "key information",
            "source": "source if available",
            "relevance": "relevance score"
        }}
    ],
    "summary": "comprehensive summary",
    "key_findings": ["key point 1", "key point 2"]
}}

Extract the most important results:"""
            
            json_response = self.llm.generate(prompt, max_tokens=1000)
            
            json_match = re.search(r'\{.*\}', json_response, re.DOTALL)
            if json_match:
                general_data = json.loads(json_match.group())
                file_path = self._save_to_file(general_data, original_query, format_type)
                
                summary_text = f"✅ Search completed! Results saved to {format_type.upper()} file.\n\n"
                summary_text += general_data.get('summary', 'Export successful.')
                
                return {
                    "text": summary_text,
                    "file_path": file_path,
                    "format": format_type,
                    "data": general_data
                }
        
        except Exception as e:
            print(f"File creation error: {e}")
        
        return None
    
    def _save_to_file(self, data: dict, query: str, format_type: str) -> str:
        """Save data to appropriate file format"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_query = re.sub(r'[^\w\s-]', '', query.lower().replace(' ', '_'))[:50]
        filename = f"{safe_query}_{timestamp}"
        
        if format_type == 'json':
            file_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format_type == 'txt':
            file_path = os.path.join(self.output_dir, f"{filename}.txt")
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self._format_text_output(data, query))
        
        elif format_type == 'csv':
            file_path = os.path.join(self.output_dir, f"{filename}.csv")
            self._save_as_csv(data, file_path)
        
        else:  # default to json
            file_path = os.path.join(self.output_dir, f"{filename}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return file_path
    
    def _format_text_output(self, data: dict, query: str) -> str:
        """Format data as readable text"""
        output = f"Search Results for: {query}\n"
        output += "=" * 50 + "\n\n"
        
        if 'products' in data:
            for i, product in enumerate(data['products'], 1):
                output += f"Product {i}:\n"
                output += f"  Name: {product.get('name', 'N/A')}\n"
                output += f"  Price: {product.get('price', 'N/A')}\n"
                output += f"  Rating: {product.get('rating', 'N/A')}\n"
                output += f"  Store: {product.get('store', 'N/A')}\n"
                output += f"  Specs: {product.get('specifications', 'N/A')}\n\n"
        
        elif 'results' in data:
            for i, result in enumerate(data['results'], 1):
                output += f"Result {i}:\n"
                output += f"  Title: {result.get('title', 'N/A')}\n"
                output += f"  Description: {result.get('description', 'N/A')}\n"
                output += f"  Source: {result.get('source', 'N/A')}\n\n"
        
        if 'summary' in data:
            output += f"Summary: {data['summary']}\n"
        
        return output
    
    def _save_as_csv(self, data: dict, file_path: str):
        """Save data as CSV format"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            if 'products' in data:
                writer.writerow(['Product Name', 'Price', 'Rating', 'Store', 'Specifications'])
                for product in data['products']:
                    writer.writerow([
                        product.get('name', ''),
                        product.get('price', ''),
                        product.get('rating', ''),
                        product.get('store', ''),
                        product.get('specifications', '')
                    ])
            
            elif 'results' in data:
                writer.writerow(['Title', 'Description', 'Source', 'Relevance'])
                for result in data['results']:
                    writer.writerow([
                        result.get('title', ''),
                        result.get('description', ''),
                        result.get('source', ''),
                        result.get('relevance', '')
                    ])
    
    def _create_fallback_response(self, extracted_data: str, original_query: str) -> str:
        """Create a response when no data is found"""
        if "Error" in extracted_data:
            return f"I encountered an error while searching for '{original_query}'. The search may have been blocked or the page structure may have changed."
        
        return f"Sorry, I couldn't find any relevant information for '{original_query}'. The search might need different search terms or the results may not be accessible."
    
    def _create_structured_fallback(self, extracted_data: str, original_query: str, output_format: str) -> dict:
        """Create a structured fallback when LLM summarization fails"""
        lines = extracted_data.split('\n')
        relevant_lines = [line for line in lines if len(line.strip()) > 20]
        
        if relevant_lines:
            text_content = f"Here's what I found for '{original_query}':\n\n" + "\n".join(relevant_lines[:10])
        else:
            text_content = f"I found some information for '{original_query}' but couldn't process it properly."
        
        return {
            "text": text_content,
            "file_path": None,
            "format": "text"
        }