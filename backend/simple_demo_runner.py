"""
Updated demo runner that saves source type to database
"""

import os
from datetime import datetime
from dotenv import load_dotenv

from agents.signal_detector import SignalDetector
from data.google_news import GoogleNewsSource
from data.sec_source import SECFilingsSource
from services.news_fetcher import NewsFetcher
from simple_supabase import SimpleSupabase

load_dotenv()


def run_demo(companies: list[str], days_back: int = 7):
    """Run the signal detection pipeline"""

    print("🚀 COMPETITIVE INTELLIGENCE DEMO")
    print("=" * 60)

    # Initialize components
    detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])
    fetcher = NewsFetcher(sources_list=[GoogleNewsSource(), SECFilingsSource()])
    db = SimpleSupabase()

    # Check database is ready
    if not db.check_table_exists():
        print("\n❌ Database not set up! Run the SQL from simple_supabase.py first")
        return

    # Process each company
    total_signals = 0
    source_stats = {}

    for company in companies:
        print(f"\n🔍 Scanning {company}...")

        # Fetch from all sources
        print(f"   🔄 Fetching articles...")
        all_articles = fetcher.fetch_multiple_sources(company, days_back)
        print(f"   📰 Found {len(all_articles)} unique articles (after deduplication)")

        # Show breakdown by source type if you want
        source_counts = {}
        for article in all_articles:
            source = article.source_type.value
            source_counts[source] = source_counts.get(source, 0) + 1

        for source, count in source_counts.items():
            print(f"      • {source}: {count} articles")

        # Extract signals
        signals_found = 0

        for article in all_articles[:15]:  # Increased limit
            try:
                # Extract signal
                signal = detector.extract(company, article.text, article.source_type)

                if signal:
                    # Track source statistics
                    source_type = article.source_type.value
                    source_stats[source_type] = source_stats.get(source_type, 0) + 1

                    # Convert to dict for Supabase with source information
                    signal_data = {
                        "company_name": company,
                        "signal_type": signal.type.value,
                        "impact": signal.impact.value,
                        "title": signal.title,
                        "action": signal.action,
                        "confidence": signal.confidence.value,
                        "person": signal.person,
                        "amount": signal.amount,
                        "source_url": article.link,
                        "detected_at": datetime.now().isoformat(),
                        # Save source type to 'source' column
                        "source": article.source_type.value,  # This is what goes in the 'source' column
                        # Don't include fields that don't exist in the table
                        # "source_platform": article.platform,   # Remove if column doesn't exist
                        # "source_name": article.platform_name,  # Remove if column doesn't exist
                    }

                    # Save to Supabase
                    result = db.save_signal(signal_data)

                    if result:
                        signals_found += 1
                        # Show source type in output
                        source_emoji = {
                            'news': '📰',
                            'regulatory': '📋',
                            'social': '💬',
                            'industry': '📊'
                        }.get(source_type, '📄')

                        print(f"   {source_emoji} [{source_type.upper()}] {signal.type.value}: {signal.title}")
                        print(f"      → {signal.action}")
                        print(f"      Source: {article.platform_name}")

            except Exception as e:
                print(f"   ⚠️  Error processing article: {e}")
                continue

        total_signals += signals_found
        print(f"   📊 Found {signals_found} signals for {company}")

    # Summary
    print("\n" + "=" * 60)
    print(f"✅ COMPLETE: Found {total_signals} total signals")

    # Show source breakdown
    if source_stats:
        print("\n📊 Signals by Source Type:")
        for source_type, count in sorted(source_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_signals * 100) if total_signals > 0 else 0
            print(f"   • {source_type}: {count} ({percentage:.1f}%)")

    print("\n🔗 View in Supabase:")
    print("   1. Go to your Supabase project")
    print("   2. Click 'Table Editor' → 'signals'")
    print("   3. Filter by 'source' column to see different source types!")

    # Show a few examples grouped by source
    print("\n📈 Recent Signals by Source Type:")
    recent = db.get_recent_signals(limit=20)

    # Group by source type
    by_source = {}
    for sig in recent:
        source = sig.get("source", "unknown")
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(sig)

    # Show one example from each source type
    for source_type, signals in by_source.items():
        if signals and signals[0].get("impact") == "high":
            sig = signals[0]
            print(f"\n   [{source_type.upper()}] {sig['company_name']}: {sig['title']}")


if __name__ == "__main__":
    # Companies to monitor - mix of public and private
    demo_companies = [
        "Microsoft",     # Public - will have SEC filings
        "Salesforce",    # Public - will have SEC filings
        "Stripe",        # Private - news only
        "OpenAI",        # Private - news only
        "Databricks"     # Private - news only
    ]

    # Run it!
    run_demo(demo_companies, days_back=30)  # 30 days to ensure we get SEC filings