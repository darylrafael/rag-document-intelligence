import sqlite3
import os
import logging

logger = logging.getLogger(__name__)

DB_PATH = os.environ.get("DB_PATH", "rag_system.db")

def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database tables if they do not exist."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Documents Table
        # Stores metadata for each uploaded and indexed document.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            file_type TEXT NOT NULL,
            chunk_count INTEGER NOT NULL,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            file_size_kb REAL NOT NULL,
            status TEXT NOT NULL
        )
        ''')
        
        # Queries Table
        # Stores history of all queries executed by users.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS queries (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            confidence_score INTEGER NOT NULL,
            doc_count INTEGER NOT NULL,
            answer TEXT,
            citations TEXT,
            timing TEXT
        )
        ''')

        # Run database migration to add new columns if table already exists
        for col, col_type in [("answer", "TEXT"), ("citations", "TEXT"), ("timing", "TEXT")]:
            try:
                cursor.execute(f"ALTER TABLE queries ADD COLUMN {col} {col_type}")
            except sqlite3.OperationalError:
                # Column already exists, safe to ignore
                pass
        
        # QueryDocuments Table
        # Join table to track which documents were referenced in which queries
        # for analytics (most queried documents).
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_documents (
            query_id TEXT NOT NULL,
            doc_id TEXT NOT NULL,
            PRIMARY KEY (query_id, doc_id),
            FOREIGN KEY (query_id) REFERENCES queries(id) ON DELETE CASCADE,
            FOREIGN KEY (doc_id) REFERENCES documents(id) ON DELETE CASCADE
        )
        ''')
        
        conn.commit()
        logger.info(f"Database initialized at {DB_PATH}")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        conn.close()

# Run initialization upon import
init_db()
