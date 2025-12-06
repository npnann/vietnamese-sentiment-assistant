import os
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from modules.storage import (
    close_all_connections,
    close_connection,
    get_history,
    get_total_count,
    save_result,
)


@pytest.fixture
def temp_db():
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
        db_path = tmp.name

    import modules.storage
    original_path = modules.storage.DB_PATH
    modules.storage.DB_PATH = Path(db_path)

    yield db_path

    close_all_connections()
    os.unlink(db_path)
    modules.storage.DB_PATH = original_path


@pytest.fixture
def sample_result():
    return {
        'text': 'Sản phẩm này rất tốt',
        'sentiment': 'POSITIVE',
        'confidence': 0.95,
        'timestamp': datetime.now().isoformat()
    }


def test_save_result(temp_db, sample_result):
    result = save_result(sample_result)
    assert result is True

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sentiments")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row[1] == sample_result['text']
    assert row[2] == sample_result['sentiment']
    assert row[3] == sample_result['confidence']
    assert row[4] == sample_result['timestamp']


def test_save_result_invalid_data(temp_db):
    invalid_result = {'text': 'test'}
    result = save_result(invalid_result)
    assert result is False


def test_get_history_empty(temp_db):
    history = get_history()
    assert history == []


def test_get_history_with_data(temp_db, sample_result):
    for i in range(5):
        result = sample_result.copy()
        result['text'] = f'Test text {i}'
        result['timestamp'] = datetime.now().isoformat()
        save_result(result)

    history = get_history(limit=10)
    assert len(history) == 5
    assert 'Test text 4' in history[0]['text']
    assert 'Test text 0' in history[4]['text']


def test_get_history_pagination(temp_db, sample_result):
    for i in range(10):
        result = sample_result.copy()
        result['text'] = f'Test text {i}'
        result['timestamp'] = datetime.now().isoformat()
        save_result(result)

    page1 = get_history(limit=5, offset=0)
    assert len(page1) == 5

    page2 = get_history(limit=5, offset=5)
    assert len(page2) == 5

    page1_texts = {item['text'] for item in page1}
    page2_texts = {item['text'] for item in page2}
    assert len(page1_texts.intersection(page2_texts)) == 0


def test_get_total_count(temp_db, sample_result):
    assert get_total_count() == 0

    for i in range(7):
        result = sample_result.copy()
        result['text'] = f'Test text {i}'
        save_result(result)

    assert get_total_count() == 7


def test_connection_management(temp_db, sample_result):
    save_result(sample_result)
    close_connection()

    result = save_result(sample_result)
    assert result is True

    close_all_connections()

    result = save_result(sample_result)
    assert result is True


def test_database_schema(temp_db):
    save_result({
        'text': 'test',
        'sentiment': 'POSITIVE',
        'confidence': 0.9,
        'timestamp': datetime.now().isoformat()
    })

    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='sentiments'"
    )
    table_exists = cursor.fetchone()
    assert table_exists is not None

    cursor.execute("PRAGMA table_info(sentiments)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    expected_columns = ['id', 'text', 'sentiment', 'confidence', 'timestamp']
    for col in expected_columns:
        assert col in column_names

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_timestamp'"
    )
    index_exists = cursor.fetchone()
    assert index_exists is not None

    conn.close()