import pytest
from unittest.mock import patch, MagicMock

from modules.sentiment import classify


class TestClassify:

    @patch('modules.sentiment.load_sentiment_model')
    def test_classify_positive(self, mock_model):
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'POS', 'score': 0.95}]
        mock_model.return_value = mock_pipeline

        result = classify("Sản phẩm rất tốt")

        assert result['sentiment'] == 'POSITIVE'
        assert result['confidence'] == 0.95
        assert 'timestamp' in result

    @patch('modules.sentiment.load_sentiment_model')
    def test_classify_negative(self, mock_model):
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'NEG', 'score': 0.88}]
        mock_model.return_value = mock_pipeline

        result = classify("Sản phẩm rất tệ")

        assert result['sentiment'] == 'NEGATIVE'
        assert result['confidence'] == 0.88

    @patch('modules.sentiment.load_sentiment_model')
    def test_classify_neutral(self, mock_model):
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'NEU', 'score': 0.75}]
        mock_model.return_value = mock_pipeline

        result = classify("Bình thường")

        assert result['sentiment'] == 'NEUTRAL'
        assert result['confidence'] == 0.75

    @patch('modules.sentiment.load_sentiment_model')
    def test_classify_error(self, mock_model):
        mock_model.side_effect = Exception("Model error")

        with pytest.raises(RuntimeError):
            classify("Test text")

    @patch('modules.sentiment.load_sentiment_model')
    def test_text_cleanup(self, mock_model):
        mock_pipeline = MagicMock()
        mock_pipeline.return_value = [{'label': 'POS', 'score': 0.90}]
        mock_model.return_value = mock_pipeline

        result = classify("Sản_phẩm  rất   tốt")

        assert '_' not in result['text']
        assert '  ' not in result['text']