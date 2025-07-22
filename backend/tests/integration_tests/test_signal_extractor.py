import os
from dotenv import load_dotenv
import pytest
from datetime import datetime

from agents.signal_detector import SignalDetector
from models.model import SignalType, ImpactLevel, Confidence

# Load environment variables
load_dotenv()

# Skip tests if no API key
pytestmark = pytest.mark.skipif(
    not os.getenv("AZURE_OPENAI_API_KEY"), reason="AZURE_OPENAI_API_KEY not set"
)


class TestSignalDetector:
    @pytest.fixture
    def detector(self):
        """Create a detector instance with API key from env"""
        api_key = os.getenv("OPENAI_API_KEY")
        return SignalDetector(api_key=api_key)

    def test_leadership_change_detection(self, detector):
        """Test detection of CEO departure signal"""
        text = """
        Acme Corp announced today that CEO John Smith will step down 
        effective immediately after 5 years leading the company. The board 
        has begun searching for a replacement. CFO Mary Johnson will serve 
        as interim CEO during the transition.
        """

        signal = detector.extract("Acme Corp", text)

        assert signal is not None
        assert signal.type == SignalType.leadership
        assert signal.impact == ImpactLevel.high
        assert signal.confidence in [Confidence.high, Confidence.medium]
        assert "John Smith" in signal.person
        assert "CEO" in signal.person
        assert "48" in signal.action or "immediate" in signal.action.lower()

    def test_funding_round_detection(self, detector):
        """Test detection of funding signal"""
        text = """
        TechStartup Inc closed a $50 million Series B funding round led by 
        Sequoia Capital. The company plans to use the funds to expand its 
        engineering team and enter the European market. This brings total 
        funding to $75 million.
        """

        signal = detector.extract("TechStartup Inc", text)

        assert signal is not None
        assert signal.type == SignalType.funding
        assert signal.impact in [ImpactLevel.high, ImpactLevel.medium]
        assert signal.amount == "$50M" or "$50 million" in signal.amount
        # Fixed: Check for any of these keywords in the action
        action_lower = signal.action.lower()
        assert any(
            keyword in action_lower
            for keyword in ["expand", "upsell", "strategy", "growth"]
        )

    def test_acquisition_detection(self, detector):
        """Test detection of M&A signal"""
        text = """
        In a surprise move, MegaCorp announced it will acquire CloudStartup 
        for $2.3 billion in cash and stock. The deal is expected to close 
        in Q2 2024 pending regulatory approval.
        """

        signal = detector.extract("CloudStartup", text)

        assert signal is not None
        assert signal.type == SignalType.acquisition
        assert signal.impact == ImpactLevel.high
        assert "$2.3" in signal.amount or "2.3 billion" in signal.amount

    def test_layoffs_detection(self, detector):
        """Test detection of layoffs signal"""
        text = """
        TechCo announced a 15% reduction in workforce affecting 1,200 employees
        as part of a restructuring plan. The company cited challenging market
        conditions and the need to focus on core products.
        """

        signal = detector.extract("TechCo", text)

        assert signal is not None
        assert signal.type == SignalType.layoffs
        assert signal.impact == ImpactLevel.high
        assert "budget" in signal.action.lower() or "check" in signal.action.lower()

    def test_no_signal_detection(self, detector):
        """Test that irrelevant news returns None"""
        text = """
        Acme Corp reported quarterly earnings in line with expectations.
        Revenue remained flat compared to last quarter with no significant
        changes in operations or strategy.
        """

        signal = detector.extract("Acme Corp", text)

        # Since the LLM might interpret product releases as expansion signals,
        # we check that it's either None OR a low-confidence signal that would be filtered
        assert signal is None or signal.confidence == Confidence.low

    def test_low_confidence_filtered(self, detector):
        """Test that low confidence signals are filtered"""
        text = """
        Sources familiar with the matter suggest there might be some changes
        at TechCo, though details remain unclear and unconfirmed.
        """

        signal = detector.extract("TechCo", text)

        assert signal is None  # Should filter out low confidence

    def test_partnership_detection(self, detector):
        """Test detection of partnership signal"""
        text = """
        Acme Corp announced a strategic partnership with Microsoft to integrate
        AI capabilities into their platform. This multi-year agreement includes
        co-development of new features.
        """

        signal = detector.extract("Acme Corp", text)

        assert signal is not None
        assert signal.type == SignalType.partnership
        assert "Microsoft" in signal.title or "Microsoft" in signal.action

    def test_with_metadata(self, detector):
        """Test extraction with metadata"""
        text = (
            "CEO Jane Doe announced her resignation from TechCorp effective next month."
        )

        signal = detector.extract_with_metadata(
            "TechCorp",
            text,
            source_url="https://example.com/article",
            article_date="2024-01-15",
        )

        assert signal is not None
        assert signal.company_name == "TechCorp"
        assert signal.source_url == "https://example.com/article"
        assert signal.article_date.year == 2024
        assert signal.article_date.month == 1
        assert signal.article_date.day == 15

    @pytest.mark.parametrize(
        "company,text,expected_type",
        [
            (
                "Zoom",
                "Zoom announces 1,300 layoffs, about 15% of staff",
                SignalType.layoffs,
            ),
            ("Figma", "Adobe to acquire Figma for $20 billion", SignalType.acquisition),
            ("Stripe", "Stripe raises $6.5B at $50B valuation", SignalType.funding),
            (
                "Twitter",
                "Elon Musk completes $44 billion Twitter acquisition",
                SignalType.acquisition,
            ),
        ],
    )
    def test_real_world_examples(self, detector, company, text, expected_type):
        """Test with real-world news examples"""
        signal = detector.extract(company, text)

        assert signal is not None
        assert signal.type == expected_type
        assert signal.confidence in [Confidence.high, Confidence.medium]

    def test_product_expansion_vs_no_signal(self, detector):
        """Test distinction between meaningful expansion and routine product updates"""
        # This should be detected as expansion
        expansion_text = """
        Acme Corp announced major expansion into Asian markets with new offices
        in Tokyo and Singapore. The company expects to hire 500 employees and 
        invest $100M in the region over the next two years.
        """

        signal = detector.extract("Acme Corp", expansion_text)
        assert signal is not None
        assert signal.type == SignalType.expansion

        # This should NOT be detected as a meaningful signal
        routine_text = """
        Acme Corp updated their mobile app with bug fixes and minor UI improvements.
        The update is available now in app stores.
        """

        signal = detector.extract("Acme Corp", routine_text)
        assert signal is None or signal.confidence == Confidence.low


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"])
