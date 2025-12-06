# Vietnamese Sentiment Assistant

A Streamlit application for sentiment analysis of Vietnamese text using PhoBERT Transformer.

## Setup Instructions

1. Clone this repository:
```bash
git clone https://github.com/npnann/vietnamese-sentiment-assistant.git
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
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
└── data/
    └── sentiments.db        # SQLite database
```