import pytest
from unittest.mock import patch, MagicMock

from modules.preprocessing import preprocess
from modules.validation import validate_input


class TestPreprocessingValidationIntegration:

    def test_valid_input_through_pipeline(self):
        text = "Sản phẩm này rất tốt"
        is_valid, _ = validate_input(text)
        assert is_valid is True

        processed = preprocess(text)
        assert len(processed) > 0

    def test_invalid_input_rejected(self):
        text = "abc"
        is_valid, error = validate_input(text)
        assert is_valid is False


class TestEndToEndFlow:

    @patch('modules.sentiment.load_sentiment_model')
    def test_full_flow(self, mock_model):
        from modules.sentiment import classify

        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'POS', 'score': 0.95}]
        mock_model.return_value = mock_pipeline

        text = "Sản phẩm rất tốt"

        is_valid, _ = validate_input(text)
        assert is_valid is True

        processed = preprocess(text)
        assert len(processed) > 0

        result = classify(processed)
        assert result['sentiment'] == 'POSITIVE'