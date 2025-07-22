"""
Simple Supabase integration for hackathon
No migrations, just straightforward table operations
"""

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SimpleSupabase:
    """Dead simple Supabase client for the hackathon"""

    def __init__(self):
        url = os.environ.get("NEXT_PUBLIC_SUPABASE_URL")
        key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

        if not url or not key:
            raise ValueError("Missing Supabase credentials in .env")

        self.client: Client = create_client(url, key)
        print("✅ Connected to Supabase")

    def setup_table(self, drop_existing=False):
        """
        Create the signals table.
        Run this ONCE in Supabase SQL editor:
        """

        sql = (
            """
-- Drop existing table if needed (careful!)
"""
            + (
                """DROP TABLE IF EXISTS signals CASCADE;
"""
                if drop_existing
                else ""
            )
            + """
-- Create signals table
CREATE TABLE IF NOT EXISTS signals (
    id SERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    signal_type TEXT NOT NULL,
    impact TEXT NOT NULL,
    title TEXT NOT NULL,
    action TEXT NOT NULL,
    confidence TEXT,
    person TEXT,
    amount TEXT,
    source_url TEXT,
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Simple index for company lookups
CREATE INDEX IF NOT EXISTS idx_company ON signals(company_name);
CREATE INDEX IF NOT EXISTS idx_detected ON signals(detected_at DESC);
"""
        )

        print("\n📋 COPY THIS SQL TO SUPABASE:")
        print("=" * 60)
        print(sql)
        print("=" * 60)
        print("\n1. Go to your Supabase project")
        print("2. Click 'SQL Editor' in the sidebar")
        print("3. Paste the SQL above and click 'Run'\n")

        return sql

    def save_signal(self, signal_data: dict) -> dict:
        """Save a signal to Supabase"""

        try:
            result = self.client.table("signals").insert(signal_data).execute()
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"❌ Error saving signal: {e}")
            return {}

    def get_recent_signals(self, limit: int = 50) -> list[dict]:
        """Get recent signals"""

        try:
            result = (
                self.client.table("signals")
                .select("*")
                .order("detected_at", desc=True)
                .limit(limit)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"❌ Error fetching signals: {e}")
            return []

    def get_company_signals(self, company_name: str) -> list[dict]:
        """Get all signals for a specific company"""

        try:
            result = (
                self.client.table("signals")
                .select("*")
                .eq("company_name", company_name)
                .order("detected_at", desc=True)
                .execute()
            )
            return result.data
        except Exception as e:
            print(f"❌ Error fetching company signals: {e}")
            return []

    def check_table_exists(self) -> bool:
        """Check if signals table exists"""

        try:
            result = (
                self.client.table("signals").select("count", count="exact").execute()
            )
            print(f"✅ Signals table exists with {result.count} records")
            return True
        except:
            print("❌ Signals table not found")
            return False


# Quick test script
if __name__ == "__main__":
    db = SimpleSupabase()

    # Check if table exists
    if not db.check_table_exists():
        print("\n⚠️  Table doesn't exist!")
        db.setup_table()
    else:
        # Test saving a signal
        test_signal = {
            "company_name": "Test Corp",
            "signal_type": "funding",
            "impact": "high",
            "title": "Test Corp raises $50M Series B",
            "action": "Schedule expansion discussion",
            "confidence": "high",
            "amount": "$50M",
        }

        result = db.save_signal(test_signal)
        if result:
            print(f"\n✅ Test signal saved with ID: {result.get('id')}")

        # Get recent signals
        signals = db.get_recent_signals(limit=5)
        print(f"\n📊 Found {len(signals)} recent signals")
        for sig in signals:
            print(f"  - {sig['company_name']}: {sig['title']}")
