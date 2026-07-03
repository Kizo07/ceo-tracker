"""
Sentiment analysis service using FinBERT.
"""
import logging
from typing import Dict, Optional, List
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch

logger = logging.getLogger(__name__)


class SentimentService:
    """
    Sentiment analysis service using FinBERT model.
    Classifies financial text as positive, negative, or neutral.
    """

    # FinBERT label mapping
    LABEL_MAP = {
        "positive": "positive",
        "negative": "negative",
        "neutral": "neutral",
        # Some FinBERT variants use different labels
        "LABEL_0": "neutral",
        "LABEL_1": "positive",
        "LABEL_2": "negative",
    }

    def __init__(self, model_name: str = "ProsusAI/finbert"):
        """
        Initialize the sentiment analysis service.

        Args:
            model_name: Hugging Face model name for FinBERT
        """
        self.model_name = model_name
        self.pipeline = None
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the FinBERT model and tokenizer."""
        try:
            logger.info(f"Loading FinBERT model: {self.model_name}")

            # Check if CUDA is available
            device = 0 if torch.cuda.is_available() else -1

            # Create the sentiment analysis pipeline
            self.pipeline = pipeline(
                "sentiment-analysis",
                model=self.model_name,
                tokenizer=self.model_name,
                device=device,
                return_all_scores=True,
            )

            logger.info(f"FinBERT model loaded successfully on device: {device}")

        except Exception as e:
            logger.error(f"Failed to load FinBERT model: {e}")
            raise

    def _neutral_result(self) -> Dict:
        """Return a neutral sentiment result."""
        return {
            "sentiment": "neutral",
            "confidence": 0.0,
            "scores": {"positive": 0.0, "negative": 0.0, "neutral": 1.0}
        }

    def analyze_sentiment(self, text: str) -> Dict:
        """
        Analyze sentiment of a single text snippet.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with sentiment label and confidence scores
        """
        if not text or not self.pipeline:
            return self._neutral_result()

        try:
            # Truncate text if too long (FinBERT max 512 tokens)
            max_length = 500
            if len(text) > max_length:
                text = text[:max_length]

            # Get predictions
            # With return_all_scores=True, we get a list of all label scores
            predictions = self.pipeline(text)

            # Handle different return formats
            if isinstance(predictions, list) and len(predictions) > 0:
                if isinstance(predictions[0], list):
                    # return_all_scores=True gives list of lists
                    results = predictions[0]
                elif isinstance(predictions[0], dict):
                    # Single result dict
                    results = predictions
                else:
                    # Unexpected format
                    logger.error(f"Unexpected prediction format: {type(predictions[0])}")
                    return self._neutral_result()
            else:
                logger.error(f"Unexpected predictions type: {type(predictions)}")
                return self._neutral_result()

            # Convert to our format
            scores = {}
            highest_score = 0
            predicted_sentiment = "neutral"

            for result in results:
                if not isinstance(result, dict):
                    logger.error(f"Result is not a dict: {type(result)}")
                    continue

                label = result.get("label", "")
                score = result.get("score", 0.0)

                # Map label
                mapped_label = self.LABEL_MAP.get(label, label.lower())
                scores[mapped_label] = score

                if score > highest_score:
                    highest_score = score
                    predicted_sentiment = mapped_label

            return {
                "sentiment": predicted_sentiment,
                "confidence": highest_score,
                "scores": scores
            }

        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return self._neutral_result()

    def analyze_batch(self, texts: List[str]) -> List[Dict]:
        """
        Analyze sentiment for multiple texts.

        Args:
            texts: List of input texts to analyze

        Returns:
            List of sentiment analysis results
        """
        if not texts or not self.pipeline:
            return []

        results = []
        for text in texts:
            results.append(self.analyze_sentiment(text))
        return results

    def get_detailed_sentiment(self, text: str) -> Dict:
        """
        Get detailed sentiment analysis with all scores.

        Args:
            text: Input text to analyze

        Returns:
            Dictionary with full sentiment breakdown
        """
        if not text or not self.pipeline:
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0,
            }

        try:
            max_length = 500
            if len(text) > max_length:
                text = text[:max_length]

            results = self.pipeline(text)[0]

            sentiment_data = {
                "sentiment": "neutral",
                "confidence": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0,
            }

            highest_score = 0

            for result in results:
                label = self.LABEL_MAP.get(result["label"], result["label"].lower())
                sentiment_data[label] = result["score"]

                if result["score"] > highest_score:
                    highest_score = result["score"]
                    sentiment_data["sentiment"] = label
                    sentiment_data["confidence"] = result["score"]

            return sentiment_data

        except Exception as e:
            logger.error(f"Error in detailed sentiment analysis: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.0,
                "positive": 0.0,
                "negative": 0.0,
                "neutral": 0.0,
            }


# Singleton instance
_sentiment_service: Optional[SentimentService] = None


def get_sentiment_service() -> SentimentService:
    """Get or create the singleton Sentiment service instance."""
    global _sentiment_service
    if _sentiment_service is None:
        _sentiment_service = SentimentService()
    return _sentiment_service
