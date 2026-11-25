#!/usr/bin/env python3
"""Database setup script for lamp_tracker."""

import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "lamp_tracker.db")


def create_database():
    """Create the lamp_tracker database with all required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Create Outages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Outages (
            lamp_id INTEGER NOT NULL,
            found_dtm TEXT NOT NULL,
            report_dtm TEXT NOT NULL,
            checked_dtm TEXT NOT NULL,
            fixed_dtm TEXT NOT NULL,
            most_recent_contact_dtm TEXT NOT NULL,
            work_order_id TEXT NOT NULL,
            PRIMARY KEY (lamp_id, found_dtm),
            FOREIGN KEY (lamp_id) REFERENCES Lamps(id)
        )
    """)

    # Create Lamps table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Lamps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            change_dtm TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            osm_object_id TEXT NOT NULL,
            verizon_pole_id TEXT,
            apco_pole_id TEXT,
            lynchburg_id TEXT,
            addr_housenumber TEXT,
            addr_street TEXT,
            addr_city TEXT,
            addr_state TEXT,
            addr_postcode TEXT
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database '{DB_PATH}' created successfully.")


def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def create_sample_users():
    """Create sample users for testing."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert a sample user (admin)
    password_hash = hash_password("admin123")
    cursor.execute(
        "INSERT INTO Users (name, password_hash, role) VALUES (?, ?, ?)",
        ("admin", password_hash, "admin")
    )

    # Insert a sample user (operator)
    password_hash = hash_password("operator123")
    cursor.execute(
        "INSERT INTO Users (name, password_hash, role) VALUES (?, ?, ?)",
        ("operator", password_hash, "operator")
    )

    conn.commit()
    conn.close()
    print("Sample users created successfully.")


if __name__ == "__main__":
    create_database()
    create_sample_users()
