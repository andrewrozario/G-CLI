import json
import urllib.request
import urllib.parse
from bs4 import BeautifulSoup
from gaia_cmd.tools.executor.executor import ToolExecutor

class WebSearchTool:
    """Tool for searching the web and scraping documentation."""
    
    @staticmethod
    def get_schema() -> dict:
        return {
            "name": "web_search",
            "description": "Searches the web for documentation or answers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    }
                },
                "required": ["query"]
            }
        }
        
    def execute(self, params: dict) -> dict:
        query = params.get("query")
        if not query:
            return {"status": "error", "message": "query is required"}
            
        try:
            # A simple DuckDuckGo HTML search fallback (without external dependencies if possible, or using requests if available)
            # Since requests is in requirements.txt, we can use it.
            import requests
            url = "https://html.duckduckgo.com/html/"
            payload = {'q': query}
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            res = requests.post(url, data=payload, headers=headers)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            results = []
            for a in soup.find_all('a', class_='result__snippet', href=True):
                # Follow the DuckDuckGo redirect to get the actual URL
                link = a['href']
                if link.startswith('//duckduckgo.com/l/?'):
                    parsed = urllib.parse.urlparse(link)
                    query_params = urllib.parse.parse_qs(parsed.query)
                    link = query_params.get('uddg', [''])[0]
                results.append({"title": a.text.strip(), "url": link})
                if len(results) >= 3:
                    break
                    
            if not results:
                return {"status": "success", "output": "No results found."}
                
            # Scrape the first result
            best_url = results[0]["url"]
            page_res = requests.get(best_url, headers=headers, timeout=10)
            page_soup = BeautifulSoup(page_res.text, 'html.parser')
            
            # Extract main text
            text = " ".join([p.text for p in page_soup.find_all('p')])
            # Trim to 4000 characters
            text = text[:4000] + "..." if len(text) > 4000 else text
            
            return {
                "status": "success", 
                "output": f"Source: {best_url}\nContent:\n{text}"
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}
