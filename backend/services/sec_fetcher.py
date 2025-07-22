import logging
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s")

class SECFetcher:
    """
    A SEC filings fetcher that returns a standardized 'article' format.
    """
    BASE_URL = "https://www.sec.gov/cgi-bin/browse-edgar"
    HEADERS = {
        # Replace with your application name and contact email
        "User-Agent": "Vista25Insights/1.0 (mailto:itai@yourdomain.com)"
    }

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.session.headers.update(self.HEADERS)

    def fetch_recent_filings(self, company_name: str, cik: Optional[str] = None) -> List[Dict]:
        """
        Fetch up to 20 of the most recent SEC filings for a given company,
        and return them as a list of "article" dicts.

        Each article has keys:
        - title: Filing title
        - link: URL to the filing index page
        - published: ISO timestamp of filing
        - pub_date: human-readable date (YYYY-MM-DD)
        - source: always 'SEC Filing'
        - text: concatenation of title and summary
        """
        articles: List[Dict] = []

        # Normalize or lookup CIK
        if cik:
            cik = str(cik).zfill(10)
        else:
            cik = self._search_cik(company_name)
            if not cik:
                logger.warning(f"Could not find CIK for {company_name}")
                return articles

        logger.info(f"Fetching SEC filings for {company_name} (CIK: {cik})")
        params = {
            "action": "getcompany",
            "CIK": cik,
            "owner": "exclude",
            "count": "20",
            "output": "atom",
        }

        resp = self.session.get(self.BASE_URL, params=params)
        resp.raise_for_status()

        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text or "No title"
            link = entry.find("atom:link", ns).attrib.get("href", "")
            published = entry.find("atom:updated", ns).text or ""
            # Convert to date
            try:
                dt = datetime.fromisoformat(published)
                pub_date = dt.strftime("%Y-%m-%d")
            except Exception:
                pub_date = published.split('T')[0] if 'T' in published else published

            summary_elem = entry.find("atom:summary", ns)
            summary = summary_elem.text.strip() if summary_elem is not None else ""

            article = {
                "title": title,
                "link": link,
                "published": published,
                "pub_date": pub_date,
                "source": "SEC Filing",
                "text": f"{title}. {summary}",
            }
            articles.append(article)

        if not articles:
            logger.info(f"Found 0 SEC filings for {company_name}")

        return articles

    def _search_cik(self, company_name: str) -> Optional[str]:
        """
        Fallback CIK lookup by company name.
        """
        params = {"action": "getcompany", "company": company_name, "owner": "exclude", "count": "1"}
        try:
            resp = self.session.get(self.BASE_URL, params=params)
            resp.raise_for_status()
            text = resp.text
            marker = "CIK="
            idx = text.find(marker)
            if idx != -1:
                raw = text[idx + len(marker): idx + len(marker) + 10]
                cik = ''.join(filter(str.isdigit, raw))
                return cik.zfill(10)
        except Exception as e:
            logger.error(f"Error searching CIK for {company_name}: {e}")
        return None


if __name__ == "__main__":
    fetcher = SECFetcher()
    companies = [
        ("Salesforce", "0001108524"),
        ("Microsoft",  "0000789019"),
        ("Apple",      "320193"),
    ]
    for name, cik in companies:
        print("=" * 60)
        print(f"SEC Filings for {name}:")
        print("=" * 60)
        articles = fetcher.fetch_recent_filings(name, cik)
        for art in articles:
            print(f"- {art['pub_date']} | {art['title']} | {art['source']}")
            print(f"  Link: {art['link']}")
            print(f"  Text: {art['text']}\n")
