
import os
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# SQLite is used for the current PythonAnywhere deployment.
# PostgreSQL support is retained for future deployment.
DATABASE_URL = os.getenv("DATABASE_URL") or None

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "blood_network.db"


class PostgreSQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        query = query.replace("?", "%s")
        if params is None:
            return self.cursor.execute(query)
        return self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()


class PostgreSQLConnectionWrapper:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        return PostgreSQLCursorWrapper(self.connection.cursor())

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db_connection():
    """Return a configured database connection."""
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        connection = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row,
            connect_timeout=10,
        )
        return PostgreSQLConnectionWrapper(connection)

    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(
        str(DATABASE_FILE),
        timeout=10,
    )
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 10000")
    return connection


def get_columns(cursor, table_name):
    """Return column names for an existing SQLite table."""
    # Table names passed here are fixed internal constants, not user input.
    cursor.execute(f"PRAGMA table_info({table_name})")
    return {row["name"] for row in cursor.fetchall()}


def create_sqlite_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER CHECK (age IS NULL OR age BETWEEN 18 AND 100),
            contact TEXT NOT NULL,
            blood_type TEXT NOT NULL
                CHECK (blood_type IN (
                    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
                )),
            location TEXT NOT NULL,
            availability TEXT NOT NULL DEFAULT 'Available'
                CHECK (availability IN ('Available', 'Unavailable')),
            last_donation TEXT,
            eligible INTEGER NOT NULL DEFAULT 1
                CHECK (eligible IN (0, 1)),
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_type TEXT NOT NULL
                CHECK (blood_type IN (
                    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
                )),
            urgency TEXT NOT NULL
                CHECK (urgency IN ('Normal', 'Urgent', 'Emergency')),
            location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK (status IN ('Pending', 'Fulfilled', 'Cancelled')),
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER NOT NULL,
            donation_date TEXT NOT NULL,
            hospital TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0
                CHECK (is_read IN (0, 1)),
            created_at TEXT NOT NULL
        )
    """)

    # Safe additive migrations: do not delete existing records.
    donor_columns = get_columns(cursor, "donors")
    if "user_id" not in donor_columns:
        cursor.execute("ALTER TABLE donors ADD COLUMN user_id INTEGER")

    request_columns = get_columns(cursor, "blood_requests")
    if "user_id" not in request_columns:
        cursor.execute(
            "ALTER TABLE blood_requests ADD COLUMN user_id INTEGER"
        )

    # Indexes for common searches and ownership lookups.
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_donors_user_id
        ON donors(user_id)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_donors_search
        ON donors(blood_type, location, availability, eligible)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_requests_user_status
        ON blood_requests(user_id, status)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_notifications_user
        ON notifications(user_id, is_read)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_donations_donor
        ON donations(donor_id, donation_date)
    """)


def create_postgresql_tables(connection):
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER CHECK (age IS NULL OR age BETWEEN 18 AND 100),
            contact TEXT NOT NULL,
            blood_type TEXT NOT NULL
                CHECK (blood_type IN (
                    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
                )),
            location TEXT NOT NULL,
            availability TEXT NOT NULL DEFAULT 'Available'
                CHECK (availability IN ('Available', 'Unavailable')),
            last_donation TEXT,
            eligible INTEGER NOT NULL DEFAULT 1
                CHECK (eligible IN (0, 1)),
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id SERIAL PRIMARY KEY,
            blood_type TEXT NOT NULL
                CHECK (blood_type IN (
                    'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
                )),
            urgency TEXT NOT NULL
                CHECK (urgency IN ('Normal', 'Urgent', 'Emergency')),
            location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
                CHECK (status IN ('Pending', 'Fulfilled', 'Cancelled')),
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id SERIAL PRIMARY KEY,
            donor_id INTEGER NOT NULL,
            donation_date TEXT NOT NULL,
            hospital TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            message TEXT NOT NULL,
            notification_type TEXT NOT NULL,
            is_read INTEGER NOT NULL DEFAULT 0
                CHECK (is_read IN (0, 1)),
            created_at TEXT NOT NULL
        )
    """)


def init_database():
    """Create missing tables and apply supported safe migrations."""
    connection = get_db_connection()

    try:
        if DATABASE_URL:
            create_postgresql_tables(connection)
        else:
            create_sqlite_tables(connection)

        connection.commit()
        print("Database setup completed successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    init_database()
