# Vietnamese Sentiment Assistant

A Streamlit application for sentiment analysis of Vietnamese text using PhoBERT Transformer.

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
vietnamese-sentiment-assistant/
├── app.py                    # Streamlit entrypoint
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── pytest.ini               # Pytest configuration
├── .gitignore               # Git ignore patterns
├── .streamlit/
│   └── config.toml          # Streamlit theme configuration
├── modules/                 # Application modules
│   ├── __init__.py
│   ├── preprocessing.py     # Text preprocessing
│   ├── sentiment.py         # Sentiment analysis
│   ├── storage.py           # Database operations
│   └── validation.py        # Input validation
├── tests/                   # Test files
│   ├── __init__.py
│   ├── test_preprocessing.py
│   ├── test_sentiment.py
│   ├── test_storage.py
│   └── test_integration.py
└── data/
    └── sentiments.db        # SQLite database
```

## Running Tests

```bash
pytest tests/ -v --cov=modules
```

## Features

- Vietnamese text sentiment analysis (POSITIVE/NEUTRAL/NEGATIVE)
- Text preprocessing with Underthesea
- Local SQLite storage for history
- Custom Streamlit theme
- Input validation
- Responsive loading states