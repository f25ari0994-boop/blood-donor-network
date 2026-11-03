
import os
import sqlite3
import logging
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL") or None

BASE_DIR = Path(__file__).resolve().parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_FILE = DATABASE_DIR / "blood_network.db"

logger = logging.getLogger(__name__)


# =========================================================
# 1. DATABASE CONNECTIONS
# =========================================================

class PostgreSQLCursorWrapper:
    def __init__(self, cursor):
        self.cursor = cursor

    def execute(self, query, parameters=()):
        query = query.replace("?", "%s")
        self.cursor.execute(query, parameters)
        return self

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    @property
    def lastrowid(self):
        return None


class PostgreSQLConnectionWrapper:
    def __init__(self, connection):
        self.connection = connection

    def cursor(self):
        return PostgreSQLCursorWrapper(
            self.connection.cursor()
        )

    def execute(self, query, parameters=()):
        cursor = self.cursor()
        cursor.execute(query, parameters)
        return cursor

    def commit(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def close(self):
        self.connection.close()


def get_db_connection():

    if DATABASE_URL:
        try:
            import psycopg
            from psycopg.rows import tuple_row

            connection = psycopg.connect(
                DATABASE_URL,
                row_factory=tuple_row
            )

            return PostgreSQLConnectionWrapper(connection)

        except ImportError as error:
            raise RuntimeError(
                "PostgreSQL requires psycopg. "
                "Install psycopg before using DATABASE_URL."
            ) from error

    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(
        DATABASE_FILE,
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    connection.execute(
        "PRAGMA busy_timeout = 10000"
    )

    return connection


# =========================================================
# 2. DATABASE COLUMN HELPERS
# =========================================================

def get_sqlite_columns(connection, table_name):

    cursor = connection.execute(
        f"PRAGMA table_info({table_name})"
    )

    return {
        row["name"]
        for row in cursor.fetchall()
    }


def get_postgresql_columns(connection, table_name):

    cursor = connection.execute(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = current_schema()
          AND table_name = ?
        """,
        (table_name,)
    )

    return {
        row[0]
        for row in cursor.fetchall()
    }


def add_sqlite_column(
    connection,
    table_name,
    column_name,
    definition
):

    columns = get_sqlite_columns(
        connection,
        table_name
    )

    if column_name not in columns:

        connection.execute(
            f"ALTER TABLE {table_name} "
            f"ADD COLUMN {column_name} {definition}"
        )


def add_postgresql_column(
    connection,
    table_name,
    column_name,
    definition
):

    connection.execute(
        f"ALTER TABLE {table_name} "
        f"ADD COLUMN IF NOT EXISTS "
        f"{column_name} {definition}"
    )


# =========================================================
# 3. UNIQUE INDEX HELPERS
# =========================================================

def create_unique_cnic_index_sqlite(connection):

    duplicate = connection.execute(
        """
        SELECT cnic
        FROM users
        WHERE cnic IS NOT NULL
          AND TRIM(cnic) != ''
        GROUP BY cnic
        HAVING COUNT(*) > 1
        LIMIT 1
        """
    ).fetchone()

    if duplicate is None:

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_users_cnic_unique
            ON users(cnic)
            WHERE cnic IS NOT NULL
              AND TRIM(cnic) != ''
            """
        )

    else:

        logger.warning(
            "Duplicate CNIC values exist. "
            "The unique CNIC index was skipped."
        )


def create_unique_cnic_index_postgresql(connection):

    duplicate = connection.execute(
        """
        SELECT cnic
        FROM users
        WHERE cnic IS NOT NULL
          AND TRIM(cnic) != ''
        GROUP BY cnic
        HAVING COUNT(*) > 1
        LIMIT 1
        """
    ).fetchone()

    if duplicate is None:

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_users_cnic_unique
            ON users(cnic)
            WHERE cnic IS NOT NULL
              AND TRIM(cnic) != ''
            """
        )

    else:

        logger.warning(
            "Duplicate CNIC values exist. "
            "The unique CNIC index was skipped."
        )


def create_unique_donation_match_index(connection):

    duplicate = connection.execute(
        """
        SELECT match_id
        FROM donations
        WHERE match_id IS NOT NULL
        GROUP BY match_id
        HAVING COUNT(*) > 1
        LIMIT 1
        """
    ).fetchone()

    if duplicate is None:

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_donations_unique_match
            ON donations(match_id)
            WHERE match_id IS NOT NULL
            """
        )

    else:

        logger.warning(
            "Duplicate donation records exist for a match. "
            "The unique donation index was skipped."
        )


def create_unique_active_match_index(connection):

    duplicate = connection.execute(
        """
        SELECT donor_user_id
        FROM request_matches
        WHERE donor_user_id IS NOT NULL
          AND status IN ('Accepted', 'Confirmed', 'Donation Reported')
        GROUP BY donor_user_id
        HAVING COUNT(*) > 1
        LIMIT 1
        """
    ).fetchone()

    if duplicate is None:

        connection.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
            idx_one_active_match_per_donor
            ON request_matches(donor_user_id)
            WHERE donor_user_id IS NOT NULL
              AND status IN ('Accepted', 'Confirmed', 'Donation Reported')
            """
        )

    else:

        logger.warning(
            "A donor has multiple active matches. "
            "The one-active-match unique index was skipped; "
            "existing records were left unchanged."
        )


# =========================================================
# 4. SQLITE TABLE CREATION
# =========================================================

def create_sqlite_tables(connection):

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,

            password TEXT NOT NULL,
            cnic TEXT
        );


        CREATE TABLE IF NOT EXISTS donors (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            age INTEGER NOT NULL
                CHECK(age BETWEEN 18 AND 100),

            contact TEXT NOT NULL,

            blood_type TEXT NOT NULL,
            location TEXT NOT NULL,

            hospital TEXT,

            availability TEXT DEFAULT 'Available',

            last_donation TEXT,

            eligible INTEGER DEFAULT 1,

            user_id INTEGER,

            health_screening_status TEXT
                DEFAULT 'Not Assessed',

            health_screening_answers TEXT,

            health_screening_date TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS blood_requests (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

           blood_type TEXT NOT NULL,
urgency TEXT NOT NULL,
needed_by TEXT,

location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,

            status TEXT DEFAULT 'Pending',

            user_id INTEGER,

            requested_units INTEGER DEFAULT 1,
            received_units INTEGER DEFAULT 0,
            remaining_units INTEGER DEFAULT 1,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS request_matches (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            request_id INTEGER NOT NULL,
            donor_id INTEGER NOT NULL,

            donor_user_id INTEGER,

            units_pledged INTEGER DEFAULT 1,

            status TEXT DEFAULT 'Accepted',

            requester_confirmed INTEGER DEFAULT 0,

            accepted_at TEXT DEFAULT CURRENT_TIMESTAMP,

            confirmed_at TEXT,
            completed_at TEXT,
            updated_at TEXT,

            UNIQUE(request_id, donor_id),

            FOREIGN KEY(request_id)
                REFERENCES blood_requests(id)
                ON DELETE CASCADE,

            FOREIGN KEY(donor_id)
                REFERENCES donors(id)
                ON DELETE CASCADE,

            FOREIGN KEY(donor_user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS donations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            donor_id INTEGER NOT NULL,

            donation_date TEXT NOT NULL,

            hospital TEXT,
            location TEXT,

            request_id INTEGER,
            match_id INTEGER,

            units INTEGER DEFAULT 1,

            status TEXT DEFAULT 'Reported',

            requester_confirmed INTEGER DEFAULT 0,

            confirmed_at TEXT,

            FOREIGN KEY(donor_id)
                REFERENCES donors(id)
                ON DELETE CASCADE,

            FOREIGN KEY(request_id)
                REFERENCES blood_requests(id)
                ON DELETE SET NULL,

            FOREIGN KEY(match_id)
                REFERENCES request_matches(id)
                ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS notifications (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            message TEXT NOT NULL,

            notification_type TEXT,

            is_read INTEGER DEFAULT 0,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            related_request_id INTEGER,
            related_match_id INTEGER,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE CASCADE,

            FOREIGN KEY(related_request_id)
                REFERENCES blood_requests(id)
                ON DELETE SET NULL,

            FOREIGN KEY(related_match_id)
                REFERENCES request_matches(id)
                ON DELETE SET NULL
        );


        CREATE TABLE IF NOT EXISTS audit_logs (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER,

            action TEXT NOT NULL,

            entity_type TEXT,
            entity_id INTEGER,

            details TEXT,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(user_id)
                REFERENCES users(id)
                ON DELETE SET NULL
        );
        """
    )

    connection.commit()


# =========================================================
# 5. SQLITE MIGRATIONS
# =========================================================

def migrate_sqlite_database(connection):

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    add_sqlite_column(
        connection,
        "users",
        "cnic",
        "TEXT"
    )

    # -----------------------------------------------------
    # DONORS
    # -----------------------------------------------------

    donor_columns = {
        "hospital": "TEXT",
        "availability": "TEXT DEFAULT 'Available'",
        "last_donation": "TEXT",
        "eligible": "INTEGER DEFAULT 1",
        "user_id": "INTEGER",
        "health_screening_status": "TEXT DEFAULT 'Not Assessed'",
        "health_screening_answers": "TEXT",
        "health_screening_date": "TEXT"
    }

    for column, definition in donor_columns.items():
        add_sqlite_column(
            connection,
            "donors",
            column,
            definition
        )

    # -----------------------------------------------------
    # BLOOD REQUESTS
    # -----------------------------------------------------

    request_columns = {
        "user_id": "INTEGER",
        "requested_units": "INTEGER DEFAULT 1",
        "received_units": "INTEGER DEFAULT 0",
        "remaining_units": "INTEGER DEFAULT 1",
        "needed_by": "TEXT",
        "created_at": "TEXT",
        "updated_at": "TEXT"
    }

    for column, definition in request_columns.items():
        add_sqlite_column(
            connection,
            "blood_requests",
            column,
            definition
        )

    # -----------------------------------------------------
    # REQUEST MATCHES
    # -----------------------------------------------------

    match_columns = {
        "donor_user_id": "INTEGER",
        "units_pledged": "INTEGER DEFAULT 1",
        "status": "TEXT DEFAULT 'Accepted'",
        "requester_confirmed": "INTEGER DEFAULT 0",
        "accepted_at": "TEXT",
        "confirmed_at": "TEXT",
        "completed_at": "TEXT",
        "updated_at": "TEXT"
    }

    for column, definition in match_columns.items():
        add_sqlite_column(
            connection,
            "request_matches",
            column,
            definition
        )

    # -----------------------------------------------------
    # DONATIONS
    # -----------------------------------------------------

    donation_columns = {
        "request_id": "INTEGER",
        "match_id": "INTEGER",
        "units": "INTEGER DEFAULT 1",
        "status": "TEXT DEFAULT 'Reported'",
        "requester_confirmed": "INTEGER DEFAULT 0",
        "confirmed_at": "TEXT"
    }

    for column, definition in donation_columns.items():
        add_sqlite_column(
            connection,
            "donations",
            column,
            definition
        )

    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    add_sqlite_column(
        connection,
        "notifications",
        "related_request_id",
        "INTEGER"
    )

    add_sqlite_column(
        connection,
        "notifications",
        "related_match_id",
        "INTEGER"
    )

    # -----------------------------------------------------
    # REPAIR OLD REQUEST RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE blood_requests
        SET requested_units = 1
        WHERE requested_units IS NULL
           OR requested_units < 1
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET received_units = 0
        WHERE received_units IS NULL
           OR received_units < 0
        """
    )

    # Calculate remaining units.
    connection.execute(
        """
        UPDATE blood_requests
        SET remaining_units =
            MAX(requested_units - received_units, 0)
        """
    )

    # Update only normal request statuses.
    # Cancelled requests remain cancelled.
    connection.execute(
        """
        UPDATE blood_requests
        SET status = 'Fulfilled'
        WHERE remaining_units = 0
          AND status IN ('Pending', 'Fulfilled')
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET status = 'Pending'
        WHERE remaining_units > 0
          AND status = 'Fulfilled'
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
           OR TRIM(created_at) = ''
        """
    )

    # -----------------------------------------------------
    # REPAIR MATCH RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE request_matches
        SET units_pledged = 1
        WHERE units_pledged IS NULL
           OR units_pledged < 1
        """
    )

    # Backfill donor account IDs for old matches.
    connection.execute(
        """
        UPDATE request_matches
        SET donor_user_id = (
            SELECT donors.user_id
            FROM donors
            WHERE donors.id = request_matches.donor_id
        )
        WHERE donor_user_id IS NULL
        """
    )

    # -----------------------------------------------------
    # REPAIR DONATION RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE donations
        SET units = 1
        WHERE units IS NULL
           OR units < 1
        """
    )

    # -----------------------------------------------------
    # UNIQUE INDEXES
    # -----------------------------------------------------

    create_unique_cnic_index_sqlite(connection)
    create_unique_donation_match_index(connection)
    create_unique_active_match_index(connection)

    # -----------------------------------------------------
    # PERFORMANCE INDEXES
    # -----------------------------------------------------

    connection.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_donors_user
        ON donors(user_id);

        CREATE INDEX IF NOT EXISTS idx_donors_blood_location
        ON donors(blood_type, location);

        CREATE INDEX IF NOT EXISTS idx_donors_availability
        ON donors(availability, eligible);


        CREATE INDEX IF NOT EXISTS idx_requests_user
        ON blood_requests(user_id);

        CREATE INDEX IF NOT EXISTS idx_requests_status
        ON blood_requests(status);

        CREATE INDEX IF NOT EXISTS idx_requests_blood_location
        ON blood_requests(blood_type, location);

        CREATE INDEX IF NOT EXISTS idx_requests_duplicate_check
        ON blood_requests(
            user_id,
            blood_type,
            hospital,
            location
        );

        CREATE INDEX IF NOT EXISTS idx_requests_needed_by
        ON blood_requests(needed_by);


        CREATE INDEX IF NOT EXISTS idx_matches_request
        ON request_matches(request_id);

        CREATE INDEX IF NOT EXISTS idx_matches_donor
        ON request_matches(donor_id);

        CREATE INDEX IF NOT EXISTS idx_matches_donor_user
        ON request_matches(donor_user_id);

        CREATE INDEX IF NOT EXISTS idx_matches_status
        ON request_matches(status, requester_confirmed);


        CREATE INDEX IF NOT EXISTS idx_donations_donor
        ON donations(donor_id);

        CREATE INDEX IF NOT EXISTS idx_donations_request
        ON donations(request_id);

        CREATE INDEX IF NOT EXISTS idx_donations_match
        ON donations(match_id);


        CREATE INDEX IF NOT EXISTS idx_notifications_user
        ON notifications(user_id, is_read);

        CREATE INDEX IF NOT EXISTS idx_audit_user
        ON audit_logs(user_id);
        """
    )

    connection.commit()


# =========================================================
# 6. POSTGRESQL TABLE CREATION
# =========================================================

def create_postgresql_tables(connection):

    statements = [

        """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password TEXT NOT NULL,
            cnic TEXT
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS donors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL
                CHECK(age BETWEEN 18 AND 100),
            contact TEXT NOT NULL,
            blood_type TEXT NOT NULL,
            location TEXT NOT NULL,
            hospital TEXT,
            availability TEXT DEFAULT 'Available',
            last_donation TEXT,
            eligible INTEGER DEFAULT 1,
            user_id INTEGER REFERENCES users(id)
                ON DELETE SET NULL,
            health_screening_status TEXT
                DEFAULT 'Not Assessed',
            health_screening_answers TEXT,
            health_screening_date TEXT
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS blood_requests (
            id SERIAL PRIMARY KEY,
            blood_type TEXT NOT NULL,
            urgency TEXT NOT NULL,
            needed_by TEXT,
            location TEXT NOT NULL,
            hospital TEXT NOT NULL,
            contact TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            user_id INTEGER REFERENCES users(id)
                ON DELETE SET NULL,
            requested_units INTEGER DEFAULT 1,
            received_units INTEGER DEFAULT 0,
            remaining_units INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS request_matches (
            id SERIAL PRIMARY KEY,
            request_id INTEGER NOT NULL
                REFERENCES blood_requests(id)
                ON DELETE CASCADE,
            donor_id INTEGER NOT NULL
                REFERENCES donors(id)
                ON DELETE CASCADE,
            donor_user_id INTEGER
                REFERENCES users(id)
                ON DELETE SET NULL,
            units_pledged INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Accepted',
            requester_confirmed INTEGER DEFAULT 0,
            accepted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            confirmed_at TEXT,
            completed_at TEXT,
            updated_at TEXT,
            UNIQUE(request_id, donor_id)
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS donations (
            id SERIAL PRIMARY KEY,
            donor_id INTEGER NOT NULL
                REFERENCES donors(id)
                ON DELETE CASCADE,
            donation_date TEXT NOT NULL,
            hospital TEXT,
            location TEXT,
            request_id INTEGER
                REFERENCES blood_requests(id)
                ON DELETE SET NULL,
            match_id INTEGER
                REFERENCES request_matches(id)
                ON DELETE SET NULL,
            units INTEGER DEFAULT 1,
            status TEXT DEFAULT 'Reported',
            requester_confirmed INTEGER DEFAULT 0,
            confirmed_at TEXT
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS notifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL
                REFERENCES users(id)
                ON DELETE CASCADE,
            message TEXT NOT NULL,
            notification_type TEXT,
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            related_request_id INTEGER
                REFERENCES blood_requests(id)
                ON DELETE SET NULL,
            related_match_id INTEGER
                REFERENCES request_matches(id)
                ON DELETE SET NULL
        )
        """,

        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id SERIAL PRIMARY KEY,
            user_id INTEGER
                REFERENCES users(id)
                ON DELETE SET NULL,
            action TEXT NOT NULL,
            entity_type TEXT,
            entity_id INTEGER,
            details TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    ]

    for statement in statements:
        connection.execute(statement)

    connection.commit()


# =========================================================
# 7. POSTGRESQL MIGRATIONS
# =========================================================

def migrate_postgresql_database(connection):

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    add_postgresql_column(
        connection,
        "users",
        "cnic",
        "TEXT"
    )

    # -----------------------------------------------------
    # DONORS
    # -----------------------------------------------------

    donor_columns = {
        "hospital": "TEXT",
        "availability": "TEXT DEFAULT 'Available'",
        "last_donation": "TEXT",
        "eligible": "INTEGER DEFAULT 1",
        "user_id": "INTEGER",
        "health_screening_status": "TEXT DEFAULT 'Not Assessed'",
        "health_screening_answers": "TEXT",
        "health_screening_date": "TEXT"
    }

    for column, definition in donor_columns.items():
        add_postgresql_column(
            connection,
            "donors",
            column,
            definition
        )

    # -----------------------------------------------------
    # BLOOD REQUESTS
    # -----------------------------------------------------

    request_columns = {
        "user_id": "INTEGER",
        "requested_units": "INTEGER DEFAULT 1",
        "received_units": "INTEGER DEFAULT 0",
        "remaining_units": "INTEGER DEFAULT 1",
        "needed_by": "TEXT",
        "created_at": "TEXT",
        "updated_at": "TEXT"
    }

    for column, definition in request_columns.items():
        add_postgresql_column(
            connection,
            "blood_requests",
            column,
            definition
        )

    # -----------------------------------------------------
    # REQUEST MATCHES
    # -----------------------------------------------------

    match_columns = {
        "donor_user_id": "INTEGER",
        "units_pledged": "INTEGER DEFAULT 1",
        "status": "TEXT DEFAULT 'Accepted'",
        "requester_confirmed": "INTEGER DEFAULT 0",
        "accepted_at": "TEXT",
        "confirmed_at": "TEXT",
        "completed_at": "TEXT",
        "updated_at": "TEXT"
    }

    for column, definition in match_columns.items():
        add_postgresql_column(
            connection,
            "request_matches",
            column,
            definition
        )

    # -----------------------------------------------------
    # DONATIONS
    # -----------------------------------------------------

    donation_columns = {
        "request_id": "INTEGER",
        "match_id": "INTEGER",
        "units": "INTEGER DEFAULT 1",
        "status": "TEXT DEFAULT 'Reported'",
        "requester_confirmed": "INTEGER DEFAULT 0",
        "confirmed_at": "TEXT"
    }

    for column, definition in donation_columns.items():
        add_postgresql_column(
            connection,
            "donations",
            column,
            definition
        )

    # -----------------------------------------------------
    # NOTIFICATIONS
    # -----------------------------------------------------

    add_postgresql_column(
        connection,
        "notifications",
        "related_request_id",
        "INTEGER"
    )

    add_postgresql_column(
        connection,
        "notifications",
        "related_match_id",
        "INTEGER"
    )

    # -----------------------------------------------------
    # REPAIR OLD REQUEST RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE blood_requests
        SET requested_units = 1
        WHERE requested_units IS NULL
           OR requested_units < 1
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET received_units = 0
        WHERE received_units IS NULL
           OR received_units < 0
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET remaining_units =
            GREATEST(requested_units - received_units, 0)
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET status = 'Fulfilled'
        WHERE remaining_units = 0
          AND status IN ('Pending', 'Fulfilled')
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET status = 'Pending'
        WHERE remaining_units > 0
          AND status = 'Fulfilled'
        """
    )

    connection.execute(
        """
        UPDATE blood_requests
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
           OR created_at = ''
        """
    )

    # -----------------------------------------------------
    # REPAIR MATCH RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE request_matches
        SET units_pledged = 1
        WHERE units_pledged IS NULL
           OR units_pledged < 1
        """
    )

    connection.execute(
        """
        UPDATE request_matches
        SET donor_user_id = (
            SELECT donors.user_id
            FROM donors
            WHERE donors.id = request_matches.donor_id
        )
        WHERE donor_user_id IS NULL
        """
    )

    # -----------------------------------------------------
    # REPAIR DONATION RECORDS
    # -----------------------------------------------------

    connection.execute(
        """
        UPDATE donations
        SET units = 1
        WHERE units IS NULL
           OR units < 1
        """
    )

    # -----------------------------------------------------
    # UNIQUE INDEXES
    # -----------------------------------------------------

    create_unique_cnic_index_postgresql(connection)
    create_unique_donation_match_index(connection)
    create_unique_active_match_index(connection)

    # -----------------------------------------------------
    # PERFORMANCE INDEXES
    # -----------------------------------------------------

    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_donors_user ON donors(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_donors_blood_location ON donors(blood_type, location)",
        "CREATE INDEX IF NOT EXISTS idx_donors_availability ON donors(availability, eligible)",

        "CREATE INDEX IF NOT EXISTS idx_requests_user ON blood_requests(user_id)",
        "CREATE INDEX IF NOT EXISTS idx_requests_status ON blood_requests(status)",
        "CREATE INDEX IF NOT EXISTS idx_requests_blood_location ON blood_requests(blood_type, location)",
        "CREATE INDEX IF NOT EXISTS idx_requests_duplicate_check ON blood_requests(user_id, blood_type, hospital, location)",
        "CREATE INDEX IF NOT EXISTS idx_requests_needed_by ON blood_requests(needed_by)",

        "CREATE INDEX IF NOT EXISTS idx_matches_request ON request_matches(request_id)",
        "CREATE INDEX IF NOT EXISTS idx_matches_donor ON request_matches(donor_id)",
        "CREATE INDEX IF NOT EXISTS idx_matches_donor_user ON request_matches(donor_user_id)",
        "CREATE INDEX IF NOT EXISTS idx_matches_status ON request_matches(status, requester_confirmed)",

        "CREATE INDEX IF NOT EXISTS idx_donations_donor ON donations(donor_id)",
        "CREATE INDEX IF NOT EXISTS idx_donations_request ON donations(request_id)",
        "CREATE INDEX IF NOT EXISTS idx_donations_match ON donations(match_id)",

        "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, is_read)",
        "CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_logs(user_id)"
    ]

    for statement in indexes:
        connection.execute(statement)

    connection.commit()


# =========================================================
# 8. DATABASE INITIALIZATION
# =========================================================

def init_database():

    connection = get_db_connection()

    try:

        if DATABASE_URL:

            create_postgresql_tables(connection)

            migrate_postgresql_database(connection)

        else:

            create_sqlite_tables(connection)

            migrate_sqlite_database(connection)

        connection.commit()

        logger.info(
            "Blood Network database initialized successfully."
        )

    except Exception:

        connection.rollback()

        logger.exception(
            "Database initialization failed."
        )

        raise

    finally:

        connection.close()


if __name__ == "__main__":

    init_database()

    print(
        "Database initialized successfully."
    )
