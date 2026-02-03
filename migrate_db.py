#!/usr/bin/env python3
"""Database migration script for career operating system features."""
from app import app
from database.models import create_table

if __name__ == '__main__':
    with app.app_context():
        create_table()
        print("✓ Database migration complete - career operating system tables created")
