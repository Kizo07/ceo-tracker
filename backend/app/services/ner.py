"""
Named Entity Recognition (NER) service for extracting company mentions.
"""
import spacy
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class NERService:
    """
    Named Entity Recognition service using spaCy.
    Extracts organization names from text and matches them to known companies.
    """

    def __init__(self, model_name: str = "en_core_web_sm"):
        """
        Initialize the NER service with a spaCy model.

        Args:
            model_name: Name of the spaCy model to use
        """
        self.model_name = model_name
        self.nlp = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the spaCy model."""
        try:
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Loaded spaCy model: {self.model_name}")
        except OSError:
            logger.warning(f"Model {self.model_name} not found. Attempting to download...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", self.model_name], check=True)
            self.nlp = spacy.load(self.model_name)
            logger.info(f"Downloaded and loaded spaCy model: {self.model_name}")

    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract all organizations from the given text.

        Args:
            text: Input text to analyze

        Returns:
            List of detected organization entities with position and label info
        """
        if not text or not self.nlp:
            return []

        doc = self.nlp(text)
        entities = []

        for ent in doc.ents:
            if ent.label_ in ["ORG", "ORGANIZATION"]:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                })

        return entities

    def extract_company_mentions(
        self,
        text: str,
        known_companies: Dict[str, str],
        context_window: int = 3
    ) -> List[Dict]:
        """
        Extract mentions of known companies from text.

        Args:
            text: Input text to analyze
            known_companies: Dictionary mapping company names to tickers
            context_window: Number of sentences to include as context

        Returns:
            List of company mentions with context
        """
        if not text:
            return []

        doc = self.nlp(text)
        mentions = []

        # Split text into sentences for context extraction
        sentences = list(doc.sents)

        for ent in doc.ents:
            if ent.label_ not in ["ORG", "ORGANIZATION"]:
                continue

            # Normalize entity text for matching
            entity_text = ent.text.strip().lower()
            entity_text_clean = entity_text.replace(" corporation", "").replace(" inc.", "").replace(" inc", "").strip()

            # Check if this entity matches any known company
            matched_company = None
            for company_name, ticker in known_companies.items():
                company_lower = company_name.lower()
                if entity_text_clean == company_lower or entity_text in company_lower or company_lower in entity_text:
                    matched_company = company_name
                    break

            if matched_company:
                # Find sentence index for context
                sentence_idx = self._find_sentence_index(ent, sentences)

                # Extract context window
                context_sentences = self._get_context_window(
                    sentences, sentence_idx, context_window
                )
                context = " ".join([s.text for s in context_sentences])

                mentions.append({
                    "company": matched_company,
                    "ticker": known_companies[matched_company],
                    "matched_text": ent.text,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "context": context.strip(),
                })

        return mentions

    def _find_sentence_index(self, entity, sentences: List) -> int:
        """Find the index of the sentence containing the entity."""
        for i, sent in enumerate(sentences):
            if sent.start <= entity.start <= sent.end:
                return i
        return 0

    def _get_context_window(self, sentences: List, idx: int, window: int) -> List:
        """Get a window of sentences around the given index."""
        start = max(0, idx - window)
        end = min(len(sentences), idx + window + 1)
        return sentences[start:end]


# Known companies for MVP (Top 5)
KNOWN_COMPANIES = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Alphabet": "GOOGL",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Facebook": "META",
    "Tesla": "TSLA",
    "Berkshire Hathaway": "BRK.B",
    "Broadcom": "AVGO",
    "Costco": "COST",
    "Visa": "V",
    "Johnson & Johnson": "JNJ",
    "Walmart": "WMT",
    "JPMorgan Chase": "JPM",
    "JPMorgan": "JPM",
    "UnitedHealth": "UNH",
    "Procter & Gamble": "PG",
    "Mastercard": "MA",
    "Eli Lilly": "LLY",
    "Exxon Mobil": "XOM",
    # Additional companies CEOs might mention
    "Marvell Technology": "MRVL",
    "Marvell Technologies": "MRVL",
    "AMD": "AMD",
    "Intel": "INTC",
    "Qualcomm": "QCOM",
    "Texas Instruments": "TXN",
    "Analog Devices": "ADI",
    "Microchip Technology": "MCHP",
    "Skyworks": "SWKS",
    "Qorvo": "QRVO",
}


# Singleton instance
_ner_service: Optional[NERService] = None


def get_ner_service() -> NERService:
    """Get or create the singleton NER service instance."""
    global _ner_service
    if _ner_service is None:
        _ner_service = NERService()
    return _ner_service
