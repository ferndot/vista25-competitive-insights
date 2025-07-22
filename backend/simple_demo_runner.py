"""
Simple demo runner for the hackathon
Fetches news, extracts signals, saves to Supabase
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from agents.signal_detector import SignalDetector
from services.news_fetcher import NewsFetcher
from simple_supabase import SimpleSupabase

load_dotenv()


def run_demo(companies: list[str], days_back: int = 7):
    """Run the signal detection pipeline"""

    print("🚀 COMPETITIVE INTELLIGENCE DEMO")
    print("=" * 60)

    # Initialize components
    detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])
    fetcher = NewsFetcher()
    db = SimpleSupabase()

    # Check database is ready
    if not db.check_table_exists():
        print("\n❌ Database not set up! Run the SQL from simple_supabase.py first")
        return

    # Process each company
    total_signals = 0

    for company in companies:
        print(f"\n🔍 Scanning {company}...")

        # Fetch news
        articles = fetcher.fetch_multiple_sources(company, days_back)
        print(f"   📰 Found {len(articles)} articles")

        # Extract signals
        signals_found = 0

        for article in articles[:10]:  # Limit to 10 per company for demo
            try:
                # Extract signal
                signal = detector.extract(company, article["text"])

                if signal:
                    # Convert to simple dict for Supabase
                    signal_data = {
                        "company_name": company,
                        "signal_type": signal.type.value,
                        "impact": signal.impact.value,
                        "title": signal.title,
                        "action": signal.action,
                        "confidence": signal.confidence.value,
                        "person": signal.person,
                        "amount": signal.amount,
                        "source_url": article.get("link"),
                        "detected_at": datetime.now().isoformat(),
                    }

                    # Save to Supabase
                    result = db.save_signal(signal_data)

                    if result:
                        signals_found += 1
                        print(f"   ✅ {signal.type.value}: {signal.title}")
                        print(f"      → {signal.action}")

            except Exception as e:
                print(f"   ⚠️  Error processing article: {e}")
                continue

        total_signals += signals_found
        print(f"   📊 Found {signals_found} signals for {company}")

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Found {total_signals} total signals")
    print("\n🔗 View in Supabase:")
    print("   1. Go to your Supabase project")
    print("   2. Click 'Table Editor' → 'signals'")
    print("   3. See all the detected signals!")

    # Show a few examples
    print("\n📈 Recent High-Impact Signals:")
    recent = db.get_recent_signals(limit=5)
    for sig in recent:
        if sig.get("impact") == "high":
            print(f"   🚨 {sig['company_name']}: {sig['title']}")


if __name__ == "__main__":
    # Companies to monitor
    demo_companies = ["Salesforce", "Databricks", "Stripe", "OpenAI", "Figma"]

    # Run it!
    run_demo(demo_companies, days_back=7)
