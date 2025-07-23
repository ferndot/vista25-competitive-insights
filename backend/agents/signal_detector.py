import os

from datetime import datetime
from dotenv import load_dotenv

from utils import azure_chat_model

load_dotenv()
from models.model import (
    Signal,
    SignalWithMetadata,
    SignalType,
    ImpactLevel,
    Confidence,
)


class SignalDetector:
    """Extracts business signals from text using structured LLM output"""

    def __init__(self, api_key: str, model: str = "gpt-4.1"):
        self.llm = azure_chat_model().with_structured_output(Signal)

    def extract(self, company_name: str, text: str, source_type: str) -> Signal | None:
        """Extract signal from text about a company, using source-specific context."""

        prompt = f"""
        You are an expert financial analyst identifying significant business signals from text.
        Analyze the following text about {company_name} from a '{source_type}' source and extract one key business signal.

        **Text to Analyze:**
        ---
        {text}
        ---

        **Instructions & Context:**
        1.  **Identify the Core Signal**: What is the single most important event? (e.g., executive departure, new funding, acquisition, financial results).
        2.  **Consider the Source**:
            * If the source is 'news', focus on the main event reported.
            * If the source is 'regulatory' (like an SEC filing), pay close attention to the filing type (e.g., 8-K, 10-K) and specific "Items" mentioned. An 8-K Item 5.02, for example, is a mandatory report of a leadership change.
        3.  **Define an Action**: Suggest a concrete next step a business team (like Sales or Customer Success) could take.
        4.  **Be Specific**: The title should be specific (e.g., "CFO John Doe Departs," not "Leadership Change"). Extract any person or monetary amount.
        5.  **Assess Impact Conservatively**: **This is crucial.** Default to a lower impact unless the event is a direct and immediate threat or opportunity. A 'high' impact signal is rare and reserved for events like company acquisitions or the departure of your executive sponsor. Most signals are 'medium' or 'low'.
        6.  **No Signal**: If the text has no clear, significant business event, you MUST use the signal type 'none'.

        **Structured Output Definitions:**
        Signal Types:
        {chr(10).join(f"- {st.value}: {st.description}" for st in SignalType)}

        Impact Levels:
        {chr(10).join(f"- {il.value}: {il.description}" for il in ImpactLevel)}

        Confidence Levels:
        {chr(10).join(f"- {c.value}: {c.description}" for c in Confidence)}

        Extract the signal based on your analysis.
        """

        try:
            signal = self.llm.invoke(prompt)

            # Filter out no-signal results
            if signal.type == SignalType.none:
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
        article_date: str | None = None,
    ) -> SignalWithMetadata | None:
        """Extract signal and add metadata"""

        signal = self.extract(company_name, text, )
        if not signal:
            return None

        # Convert article_date string to datetime if provided
        article_datetime = None
        if article_date:
            try:
                article_datetime = datetime.fromisoformat(article_date)
            except:
                pass

        return SignalWithMetadata(
            **signal.model_dump(),
            company_name=company_name,
            source_url=source_url,
            article_date=article_datetime,
        )


if __name__ == "__main__":
    detector = SignalDetector(api_key=os.environ["OPENAI_API_KEY"])

    test_text = """
    Acme Corp CEO John Smith announced his resignation today after 
    5 years at the helm. The board has started searching for a replacement.
    """

    signal = detector.extract("Acme Corp", test_text)
    if signal:
        print(f"Type: {signal.type}")
        print(f"Impact: {signal.impact}")
        print(f"Title: {signal.title}")
        print(f"Action: {signal.action}")
        print(f"Person: {signal.person}")
        print(f"Confidence: {signal.confidence.value}")
