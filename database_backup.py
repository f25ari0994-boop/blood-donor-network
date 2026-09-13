import sqlite3
import os


# --------------------------------
# DATABASE PATH
# --------------------------------

DATABASE_PATH = os.path.join(
    "database",
    "blood_network.db"
)


# --------------------------------
# CREATE DATABASE FOLDER
# --------------------------------

os.makedirs(
    "database",
    exist_ok=True
)


# --------------------------------
# CONNECT TO DATABASE
# --------------------------------

connection = sqlite3.connect(
    DATABASE_PATH
)

cursor = connection.cursor()


# --------------------------------
# USERS TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    phone TEXT UNIQUE,
    password TEXT NOT NULL
)
""")


# --------------------------------
# DONORS TABLE
# --------------------------------

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


# --------------------------------
# BLOOD REQUESTS TABLE
# --------------------------------

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


# --------------------------------
# DONATIONS TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS donations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    donor_id INTEGER NOT NULL,
    donation_date TEXT NOT NULL,
    hospital TEXT NOT NULL,
    location TEXT NOT NULL
)
""")


# --------------------------------
# NOTIFICATIONS TABLE
# --------------------------------

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


# --------------------------------
# SAFE COLUMN MIGRATION
# --------------------------------

def add_column_if_missing(
    table_name,
    column_name,
    column_definition
):

    cursor.execute(
        f"PRAGMA table_info({table_name})"
    )

    columns = cursor.fetchall()

    existing_columns = [
        column[1]
        for column in columns
    ]

    if column_name not in existing_columns:

        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name}
            {column_definition}
            """
        )

        print(
            f"Added missing column: "
            f"{table_name}.{column_name}"
        )


# --------------------------------
# USERS MIGRATION
# --------------------------------

add_column_if_missing(
    "users",
    "phone",
    "TEXT"
)


# --------------------------------
# DONORS MIGRATION
# --------------------------------

add_column_if_missing(
    "donors",
    "age",
    "INTEGER"
)

add_column_if_missing(
    "donors",
    "availability",
    "TEXT DEFAULT 'Available'"
)

add_column_if_missing(
    "donors",
    "last_donation",
    "TEXT"
)

add_column_if_missing(
    "donors",
    "eligible",
    "INTEGER DEFAULT 1"
)

add_column_if_missing(
    "donors",
    "user_id",
    "INTEGER"
)


# --------------------------------
# SAVE CHANGES
# --------------------------------

connection.commit()
connection.close()


print("Database setup completed successfully!")