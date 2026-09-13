import os
import sqlite3


DATABASE_URL = os.environ.get("DATABASE_URL")


class PostgreSQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, params=None):
        # Convert SQLite-style ? placeholders to PostgreSQL %s
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

    def close(self):
        self.connection.close()


def get_db_connection():
    """
    Use Neon PostgreSQL when DATABASE_URL is available.
    Otherwise use the local SQLite database.
    """

    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        connection = psycopg.connect(
            DATABASE_URL,
            row_factory=dict_row
        )

        return PostgreSQLConnectionWrapper(connection)

    os.makedirs("database", exist_ok=True)

    connection = sqlite3.connect(
        "database/blood_network.db"
    )

    connection.row_factory = sqlite3.Row

    return connection


def init_database():
    connection = get_db_connection()

    if DATABASE_URL:
        create_postgresql_tables(connection)
    else:
        create_sqlite_tables(connection)

    connection.commit()
    connection.close()

    print("Database setup completed successfully!")


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
            age INTEGER,
            contact TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            location TEXT NOT NULL,
            availability TEXT DEFAULT 'Available',
            last_donation TEXT,
            eligible INTEGER DEFAULT 1,
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_type TEXT NOT NULL,
            urgency TEXT NOT NULL,
            location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
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
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
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
            age INTEGER,
            contact TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            location TEXT NOT NULL,
            availability TEXT DEFAULT 'Available',
            last_donation TEXT,
            eligible INTEGER DEFAULT 1,
            user_id INTEGER
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id SERIAL PRIMARY KEY,
            blood_type TEXT NOT NULL,
            urgency TEXT NOT NULL,
            location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT DEFAULT 'Pending'
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
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)


if __name__ == "__main__":
    init_database()