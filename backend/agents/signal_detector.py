import os

from datetime import datetime
from dotenv import load_dotenv

from utils import azure_chat_model

load_dotenv()
from models.signal import (
    Signal,
    SignalWithMetadata,
    SignalType,
    ImpactLevel,
    Confidence,
)


class SignalDetector:
    """Extracts business signals from text using structured LLM output"""

    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        # self.llm = ChatOpenAI(
        #     model=model,
        #     temperature=0.1,
        #     api_key=api_key
        # ).with_structured_output(Signal)
        self.llm = azure_chat_model().with_structured_output(Signal)

    def extract(self, company_name: str, text: str) -> Signal | None:
        """Extract signal from text about a company"""

        prompt = f"""
        Analyze this text about {company_name} and extract business signals.

        Text: {text}

        Signal Types:
        {chr(10).join(f"- {st.value}: {st.description}" for st in SignalType)}

        Impact Levels:
        {chr(10).join(f"- {il.value}: {il.description}" for il in ImpactLevel)}

        Confidence Levels:
        {chr(10).join(f"- {c.value}: {c.description}" for c in Confidence)}

        Focus on actionable intelligence for Customer Success.
        If no clear signal exists, use signal_type 'none'.
        Make the title specific and the action concrete with a clear timeline.
        """

        try:
            signal = self.llm.invoke(prompt)

            # Filter out low-confidence or no-signal results
            if signal.signal_type == SignalType.none or signal.confidence == Confidence.low:
                return None

            return signal

        except Exception as e:
            print(f"Extraction failed: {e}")
            return None

    def extract_with_metadata(
        self,
        company_name: str,
        text: str,
        source_url: str | None = None,
    ) -> SignalWithMetadata | None:
        """Extract signal and add metadata"""

        signal = self.extract(company_name, text)
        if not signal:
            return None

        return SignalWithMetadata(
            **signal.dict(),
            company_name=company_name,
            source_url=source_url,
        )


# Quick test
if __name__ == "__main__":
    detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])

    test_text = """
    Acme Corp CEO John Smith announced his resignation today after 
    5 years at the helm. The board has started searching for a replacement.
    """

    signal = detector.extract("Acme Corp", test_text)
    if signal:
        print(f"Type: {signal.signal_type}")
        print(f"Impact: {signal.impact}")
        print(f"Title: {signal.title}")
        print(f"Action: {signal.action}")
        print(f"Person: {signal.person}")
        print(f"Confidence: {signal.confidence.value}")
