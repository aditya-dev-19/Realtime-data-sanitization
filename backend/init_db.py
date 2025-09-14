#!/usr/bin/env python3
"""
Initialize the database with the required tables.
"""
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.database import init_db

def main():
    print("Initializing database...")
    init_db()
    print("Database initialization complete!")

if __name__ == "__main__":
    main()
