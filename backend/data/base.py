from abc import ABC, abstractmethod
from bs4 import BeautifulSoup
from models.model import Result


class DataSource(ABC):
    """Abstract base class for data sources"""
    
    platform_name: str = None
    platform_id: str = None
    
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    
    @abstractmethod
    def fetch(self, company_name: str, days_back: int = 7) -> list[Result]:
        """Fetch data from the source"""
        pass
    
    def _clean_html(self, html_text: str) -> str:
        """Remove HTML tags and clean text"""
        if not html_text:
            return ""

        soup = BeautifulSoup(html_text, "html.parser")
        text = soup.get_text()

        # Clean up whitespace
        text = " ".join(text.split())

        return text
