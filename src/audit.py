import psycopg2
from datetime import datetime
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def init_audit_db():
    """Create audit_logs table if not exists."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            question TEXT NOT NULL,
            masked_context TEXT,
            answer TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def log_query(user_id: str, question: str, masked_context: str, answer: str) -> int:
    """Insert a log entry and return its ID."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO audit_logs (user_id, question, masked_context, answer) VALUES (%s, %s, %s, %s) RETURNING id",
        (user_id, question, masked_context, answer)
    )
    audit_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return audit_id