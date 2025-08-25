import requests
from typing import List
from bs4 import BeautifulSoup
from source.core.config import Settings

class GoogleSearchTool:
    """
    Tìm kiếm Google và trích xuất nội dung trang web cho chatbot.
    """
    def __init__(self, setting: Settings):
        self.api_key = setting.GOOGLE_SEARCH_API
        self.cse_id = setting.TOOL_SEARCH

    def search(self, query: str, num_results: int = 5) -> List[str]:
        """Tìm kiếm Google, trả về danh sách link."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "q": query,
            "key": self.api_key,
            "cx": self.cse_id,
            "num": num_results
        }
        response = requests.get(url, params=params)
        if response.status_code != 200:
            raise Exception(f"Search failed: {response.text}")
        results = response.json()
        return [item["link"] for item in results.get("items", [])]

    def extract_text_from_url(self, url: str) -> str:
        """Trích xuất nội dung text từ một URL."""
        headers = {
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
            )
        }
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=10,
                verify=False
            )
            if response.status_code != 200:
                return f"[Failed to fetch {url}] Status code: {response.status_code}"
            soup = BeautifulSoup(response.text, 'html.parser')
            for script_or_style in soup(["script", "style"]):
                script_or_style.extract()
            text = soup.get_text(separator=' ', strip=True)
            return text
        except requests.exceptions.SSLError as ssl_err:
            return f"[SSL Error fetching {url}]: {str(ssl_err)}"
        except requests.exceptions.ProxyError as proxy_err:
            return f"[Proxy Error fetching {url}]: {str(proxy_err)}"
        except requests.exceptions.RequestException as req_err:
            return f"[Request Exception fetching {url}]: {str(req_err)}"
        except Exception as e:
            return f"[General Error fetching {url}]: {str(e)}"

    def extract_texts_from_links(self, links: List[str]) -> List[str]:
        """Trích xuất nội dung text từ danh sách link."""
        return [self.extract_text_from_url(url) for url in links]
