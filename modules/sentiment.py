import streamlit as st
from transformers import pipeline
from datetime import datetime
from typing import Any, Dict


@st.cache_resource(show_spinner=False)
def load_sentiment_model():
    return pipeline('sentiment-analysis', model='wonrax/phobert-base-vietnamese-sentiment')

def classify(text: str) -> Dict[str, Any]:

    try:
        model = load_sentiment_model()
        result = model(text)
        print(f"Model output: {result}")
        
        label = result[0]['label']
        confidence = result[0]['score']

        label_mapping = {
            'POS': 'POSITIVE',
            'NEU': 'NEUTRAL',
            'NEG': 'NEGATIVE'
        }
        sentiment = label_mapping.get(label, 'NEUTRAL')

        text = text.replace('_', ' ')
        text = ' '.join(text.split())

        return {
            'text': text,
            'sentiment': sentiment,
            'confidence': float(confidence),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise RuntimeError(f"Sentiment classification failed: {str(e)}")