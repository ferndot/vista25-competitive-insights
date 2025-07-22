"""
Fixed SEC data source integration with Result model
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
from models.data_source import Result, SourceType
from data.base import DataSource
from services.sec_fetcher import SECFetcher
import re
from loguru import logger


class SECFilingsSource(DataSource):
    """SEC filings data source with enhanced signal detection"""

    platform_name = "SEC Filings"
    platform_id = "sec"

    # Known company CIK mappings for common companies
    KNOWN_CIKS = {
        # Tech companies
        "microsoft": "0000789019",
        "apple": "0000320193",
        "apple inc": "0000320193",
        "salesforce": "0001108524",
        "salesforce.com": "0001108524",
        "google": "0001652044",
        "alphabet": "0001652044",
        "meta": "0001326801",
        "facebook": "0001326801",
        "amazon": "0001018724",
        "netflix": "0001065280",
        "tesla": "0001318605",
        "nvidia": "0001045810",
        "oracle": "0001341439",
        "adobe": "0000796343",
        "paypal": "0001633917",
        "stripe": None,  # Private company
        "databricks": None,  # Private company
        "openai": None,  # Private company
        "figma": None,  # Private company

        # Other major companies
        "walmart": "0000104169",
        "jpmorgan": "0000019617",
        "berkshire hathaway": "0001067983",
        "johnson & johnson": "0000200406",
        "procter & gamble": "0000080424",
        "coca-cola": "0000021344",
        "disney": "0001744489",
        "nike": "0000320187",
        "mcdonald's": "0000063908",
        "starbucks": "0000829224",
    }

    # Map filing types to potential signal types
    FILING_SIGNAL_MAP = {
        "8-K": {
            "pattern": r"8-K",
            "signal_hints": ["leadership", "acquisition", "partnership", "material_change"],
            "importance": "high"
        },
        "10-Q": {
            "pattern": r"10-Q",
            "signal_hints": ["financial", "quarterly_update"],
            "importance": "medium"
        },
        "10-K": {
            "pattern": r"10-K",
            "signal_hints": ["financial", "annual_report"],
            "importance": "medium"
        },
        "DEF 14A": {
            "pattern": r"DEF 14A",
            "signal_hints": ["leadership", "executive_compensation"],
            "importance": "high"
        },
        "SC 13G": {
            "pattern": r"SC 13[DG]",
            "signal_hints": ["ownership_change", "major_investor"],
            "importance": "high"
        },
        "S-1": {
            "pattern": r"S-1",
            "signal_hints": ["ipo", "funding"],
            "importance": "high"
        },
        "S-4": {
            "pattern": r"S-4",
            "signal_hints": ["acquisition", "merger"],
            "importance": "high"
        }
    }

    # 8-K Item codes and their meanings
    FORM_8K_ITEMS = {
        "1.01": "Entry into Material Agreement",
        "1.02": "Termination of Material Agreement",
        "2.01": "Completion of Acquisition or Disposition",
        "2.05": "Costs Associated with Exit or Disposal Activities",
        "5.01": "Changes in Control",
        "5.02": "Departure/Appointment of Directors/Officers",
        "7.01": "Regulation FD Disclosure",
        "8.01": "Other Events"
    }

    def __init__(self):
        super().__init__()
        self.fetcher = SECFetcher()

    def _get_cik(self, company_name: str) -> Optional[str]:
        """Get CIK with fallback to known mappings"""

        # First check our known mappings
        normalized_name = company_name.lower().strip()

        # Check exact match
        if normalized_name in self.KNOWN_CIKS:
            return self.KNOWN_CIKS[normalized_name]

        # Check partial matches
        for known_name, cik in self.KNOWN_CIKS.items():
            if known_name in normalized_name or normalized_name in known_name:
                return cik

        # If not found, log it
        logger.warning(f"No known CIK for {company_name}, attempting lookup")

        # Fall back to search (but this is unreliable)
        return None

    def fetch(self, company_name: str, days_back: int = 7) -> List[Result]:
        """Fetch and enhance SEC filings with signal hints"""

        # Get CIK from our mapping
        cik = self._get_cik(company_name)

        if cik is None:
            logger.info(f"Skipping SEC filings for {company_name} - private company or CIK not found")
            return []

        # Get raw filings with the correct CIK
        filings = self.fetcher.fetch_recent_filings(company_name, cik)

        # Filter by date if needed
        cutoff_date = datetime.now() - timedelta(days=days_back)

        results = []
        for filing in filings:
            # Parse filing date
            try:
                # Handle ISO format with timezone
                pub_date_str = filing['published'].replace('Z', '+00:00')
                filing_date = datetime.fromisoformat(pub_date_str)

                if filing_date.date() < cutoff_date.date():
                    continue

            except:
                # If date parsing fails, try to parse pub_date string
                try:
                    filing_date = datetime.strptime(filing['pub_date'], "%Y-%m-%d")
                except:
                    # If all parsing fails, include the filing with current date
                    filing_date = datetime.now()

            # Enhance filing text with signal context
            enhanced_text = self._create_enhanced_text(filing, company_name)

            # Create Result object
            result = Result(
                title=filing.get('title', 'No title'),
                link=filing.get('link', ''),
                published=filing.get('published', ''),
                published_on=filing_date,
                source=SourceType.regulatory,  # SEC is regulatory source
                text=enhanced_text,
                platform=self.platform_id,
                platform_name=self.platform_name
            )

            # Store additional metadata in the result if needed
            # This can be accessed later for enhanced processing
            result._filing_type = self._detect_filing_type(filing.get('title', ''))[0]
            result._signal_hints = self._detect_filing_type(filing.get('title', ''))[1].get('signal_hints', [])

            results.append(result)

        logger.info(f"Found {len(results)} SEC filings for {company_name} in last {days_back} days")
        return results

    def _detect_filing_type(self, title: str) -> tuple[str, Dict]:
        """Detect filing signal_type and return associated metadata"""

        for filing_type, info in self.FILING_SIGNAL_MAP.items():
            if re.search(info['pattern'], title, re.IGNORECASE):
                return filing_type, info

        return "OTHER", {"signal_hints": ["regulatory"], "importance": "low"}

    def _extract_8k_items(self, text: str) -> List[str]:
        """Extract specific 8-K item numbers from filing text"""

        items_found = []

        # Look for patterns like "Item 5.02" or "Item 2.01"
        item_pattern = r"Item\s+(\d+\.\d+)"
        matches = re.findall(item_pattern, text, re.IGNORECASE)

        for item_num in matches:
            if item_num in self.FORM_8K_ITEMS:
                item_desc = self.FORM_8K_ITEMS[item_num]
                items_found.append(f"{item_num} - {item_desc}")

        return list(set(items_found))  # Remove duplicates

    def _create_enhanced_text(self, filing: Dict, company_name: str) -> str:
        """Create enhanced text optimized for signal extraction"""

        filing_type, filing_info = self._detect_filing_type(filing.get('title', ''))
        title = filing.get('title', '')
        original_text = filing.get('text', '')

        # Build enhanced text with context
        enhanced_parts = [
            f"{company_name} filed {filing_type}.",
            title,
        ]

        # Add signal hints as context
        if filing_info.get('signal_hints'):
            hints = ", ".join(filing_info['signal_hints']).replace('_', ' ')
            enhanced_parts.append(f"This filing may indicate: {hints}.")

        # For 8-K, try to extract specific items
        if filing_type == "8-K":
            items = self._extract_8k_items(original_text)
            if items:
                items_text = " Key items: " + "; ".join(items)
                enhanced_parts.append(items_text)

        # Add original text
        enhanced_parts.append(original_text)

        return " ".join(enhanced_parts)


# Test
if __name__ == "__main__":
    sec_source = SECFilingsSource()

    # Test with a public company
    results = sec_source.fetch("Microsoft", days_back=30)

    print(f"Found {len(results)} SEC filings")
    for result in results[:3]:
        print(f"\n📄 {result.title}")
        print(f"   Date: {result.published_on}")
        print(f"   Source Type: {result.source.value}")
        print(f"   Platform: {result.platform_name}")