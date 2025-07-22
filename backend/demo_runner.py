# demo.py
from dotenv import load_dotenv

load_dotenv()
from agents.signal_detector import SignalDetector
from services.news_fetcher import NewsFetcher
from models.model import SignalType
import os


def run_demo():
    detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])
    fetcher = NewsFetcher()

    companies = ["Salesforce", "Stripe", "Databricks", "Figma", "OpenAI"]

    all_signals = []

    for company in companies:
        print(f"\nScanning {company}...")

        # Fetch news
        articles = fetcher.fetch_multiple_sources(company, days_back=7)

        # Extract signals
        for article in articles:
            signal = detector.extract_with_metadata(
                company, article.text, article.link, article.published
            )

            if signal:
                all_signals.append(signal)
                print(f"  🚨 Found: {signal.type.value} - {signal.title}")

    # Summary
    print(f"\n{'=' * 60}")
    print(
        f"SUMMARY: Found {len(all_signals)} signals across {len(companies)} companies"
    )

    # Group by type
    by_type = {}
    for sig in all_signals:
        by_type.setdefault(sig.type.value, []).append(sig)

    for type_name, signals in by_type.items():
        print(f"\n{type_name.upper()} ({len(signals)}):")
        for sig in signals:
            print(f"  - {sig.company_name}: {sig.title}")
            print(f"    Action: {sig.action}")


if __name__ == "__main__":
    run_demo()
