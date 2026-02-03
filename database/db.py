"""Database connection and initialization."""
import sqlite3
from flask import g
from config import DATABASE_PATH

DATABASE = DATABASE_PATH

def get_db():
    """Get database connection."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database connection."""
    import os
    db_dir = os.path.dirname(DATABASE)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)
    
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        print(f"Database initialized at {DATABASE}")

def close_db(e=None):
    """Close database connection."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()