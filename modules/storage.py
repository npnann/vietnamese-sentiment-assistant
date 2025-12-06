import sqlite3
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path("data/sentiments.db")

_connection_pool = {}
_pool_lock = threading.Lock()


def _get_connection() -> sqlite3.Connection:
    thread_id = threading.current_thread().ident
    
    with _pool_lock:
        if thread_id in _connection_pool:
            try:
                _connection_pool[thread_id].execute("SELECT 1")
            except sqlite3.Error:
                del _connection_pool[thread_id]
        
        if thread_id not in _connection_pool:
            DB_PATH.parent.mkdir(exist_ok=True)
            
            conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            _connection_pool[thread_id] = conn
            
            _init_database(conn)
        
        return _connection_pool[thread_id]


def _init_database(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            sentiment TEXT NOT NULL,
            confidence REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp ON sentiments(timestamp)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_sentiment ON sentiments(sentiment)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_text ON sentiments(text)
    """)
    
    conn.commit()


def save_result(result: Dict[str, Any]) -> bool:
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO sentiments (text, sentiment, confidence, timestamp) VALUES (?, ?, ?, ?)",
            (result["text"], result["sentiment"], result["confidence"], result["timestamp"])
        )
        
        conn.commit()
        return True
    except (sqlite3.Error, KeyError):
        return False


def get_history(
    limit: int = 50, 
    offset: int = 0,
    search_query: Optional[str] = None,
    sentiment_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM sentiments WHERE 1=1"
        params: List[Any] = []
        
        if search_query:
            query += " AND text LIKE ?"
            params.append(f"%{search_query}%")
        
        if sentiment_filter:
            query += " AND sentiment = ?"
            params.append(sentiment_filter)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error:
        return []


def get_total_count() -> int:
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sentiments")
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error:
        return 0


def get_filtered_count(
    search_query: Optional[str] = None,
    sentiment_filter: Optional[str] = None
) -> int:
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        query = "SELECT COUNT(*) FROM sentiments WHERE 1=1"
        params: List[Any] = []
        
        if search_query:
            query += " AND text LIKE ?"
            params.append(f"%{search_query}%")
        
        if sentiment_filter:
            query += " AND sentiment = ?"
            params.append(sentiment_filter)
        
        cursor.execute(query, params)
        result = cursor.fetchone()
        return result[0] if result else 0
    except sqlite3.Error:
        return 0


def close_connection() -> None:
    thread_id = threading.current_thread().ident
    
    with _pool_lock:
        if thread_id in _connection_pool:
            _connection_pool[thread_id].close()
            del _connection_pool[thread_id]


def close_all_connections() -> None:
    with _pool_lock:
        for conn in _connection_pool.values():
            conn.close()
        _connection_pool.clear()