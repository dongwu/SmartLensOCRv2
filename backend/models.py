"""
Database models and operations for SmartLensOCR backend.
Provides type-safe database interactions and query builders.
"""

from datetime import datetime
from typing import Optional, List
import sqlite3
from contextlib import contextmanager
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "smartlensocr.db")


@contextmanager
def get_db():
    """Get database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


class User:
    """User model and database operations"""
    
    @staticmethod
    def create(user_id: str, email: str, credits: int = 5) -> dict:
        """Create a new user"""
        with get_db() as conn:
            conn.execute(
                "INSERT INTO users (id, email, credits, isPro) VALUES (?, ?, ?, ?)",
                (user_id, email, credits, 0)
            )
            conn.commit()
        return User.get_by_id(user_id)
    
    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        """Get user by ID"""
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        """Get user by email"""
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE email = ?", (email.lower(),)
            ).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def update_credits(user_id: str, amount: int) -> Optional[dict]:
        """Update user credits"""
        with get_db() as conn:
            user = conn.execute(
                "SELECT credits FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            
            if not user:
                return None
            
            new_credits = max(0, user['credits'] + amount)
            conn.execute(
                "UPDATE users SET credits = ? WHERE id = ?",
                (new_credits, user_id)
            )
            conn.commit()
        
        return User.get_by_id(user_id)
    
    @staticmethod
    def list_all() -> List[dict]:
        """Get all users"""
        with get_db() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [dict(row) for row in rows]


class Transaction:
    """Transaction model and database operations"""
    
    @staticmethod
    def create(user_id: str, amount: int, type_: str, description: str = "") -> dict:
        """Create a new transaction"""
        with get_db() as conn:
            cursor = conn.execute(
                "INSERT INTO transactions (user_id, amount, type, description) VALUES (?, ?, ?, ?)",
                (user_id, amount, type_, description)
            )
            conn.commit()
            trans_id = cursor.lastrowid
        
        return Transaction.get_by_id(trans_id)
    
    @staticmethod
    def get_by_id(trans_id: int) -> Optional[dict]:
        """Get transaction by ID"""
        with get_db() as conn:
            row = conn.execute(
                "SELECT * FROM transactions WHERE id = ?", (trans_id,)
            ).fetchone()
            return dict(row) if row else None
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 100) -> List[dict]:
        """Get transactions for a user"""
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]
    
    @staticmethod
    def get_total_credits(user_id: str) -> int:
        """Get total credits spent by user"""
        with get_db() as conn:
            row = conn.execute(
                "SELECT SUM(ABS(amount)) as total FROM transactions WHERE user_id = ? AND type = 'debit'",
                (user_id,)
            ).fetchone()
            return row['total'] or 0


class ProcessingLog:
    """Log for document processing operations"""
    
    @staticmethod
    def create(user_id: str, operation: str, status: str, details: str = "") -> dict:
        """Create a processing log entry"""
        with get_db() as conn:
            conn.execute(
                "INSERT INTO processing_logs (user_id, operation, status, details) VALUES (?, ?, ?, ?)",
                (user_id, operation, status, details)
            )
            conn.commit()
    
    @staticmethod
    def get_by_user(user_id: str, limit: int = 50) -> List[dict]:
        """Get processing logs for a user"""
        with get_db() as conn:
            rows = conn.execute(
                "SELECT * FROM processing_logs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
                (user_id, limit)
            ).fetchall()
            return [dict(row) for row in rows]


def init_database():
    """Initialize database tables"""
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                credits INTEGER DEFAULT 5,
                isPro INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.execute("""
            CREATE TABLE IF NOT EXISTS processing_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                operation TEXT NOT NULL,
                status TEXT NOT NULL,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Create indexes for better query performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_transactions_user ON transactions(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_processing_logs_user ON processing_logs(user_id)")
        
        conn.commit()
