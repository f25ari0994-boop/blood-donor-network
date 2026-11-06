import os
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from app import app as flask_app


class ProfilePageRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(self.temp_dir.name, "profile-test.db")
        self._old_testing = flask_app.config.get("TESTING", False)
        flask_app.config["TESTING"] = True

        connection = sqlite3.connect(self.database_path)
        connection.executescript(
            """
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                password TEXT NOT NULL,
                cnic TEXT,
                language_preference TEXT
            );

            CREATE TABLE donors (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER,
                blood_type TEXT,
                location TEXT,
                availability TEXT,
                eligible INTEGER,
                last_donation TEXT,
                health_screening_status TEXT,
                user_id INTEGER
            );

            CREATE TABLE blood_requests (
                id INTEGER PRIMARY KEY,
                blood_type TEXT,
                urgency TEXT,
                location TEXT,
                hospital TEXT,
                requested_units INTEGER,
                received_units INTEGER,
                remaining_units INTEGER,
                status TEXT,
                user_id INTEGER,
                created_at TEXT
            );

            CREATE TABLE donations (
                id INTEGER PRIMARY KEY,
                donor_id INTEGER,
                donation_date TEXT,
                hospital TEXT,
                location TEXT,
                units INTEGER,
                status TEXT,
                requester_confirmed INTEGER,
                request_id INTEGER,
                match_id INTEGER
            );

            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                is_read INTEGER DEFAULT 0
            );
            """
        )

        connection.executemany(
            """
            INSERT INTO users
                (id, name, email, phone, password, cnic, language_preference)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, "Own User", "own@example.com", "03001111111",
                 "hash", "1111111111111", "English"),
                (2, "Other User", "other@example.com", "03002222222",
                 "hash", "2222222222222", "Urdu"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO donors
                (id, name, age, blood_type, location, availability,
                 eligible, last_donation, health_screening_status, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (101, "Own Donor Profile", 25, "O-", "Sukkur",
                 "Available", 1, None, "Self-Declared Clear", 1),
                (201, "Other Donor Profile", 30, "A+", "Karachi",
                 "Available", 1, None, "Self-Declared Clear", 2),
            ],
        )

        connection.executemany(
            """
            INSERT INTO blood_requests
                (id, blood_type, urgency, location, hospital, requested_units,
                 received_units, remaining_units, status, user_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (1, "A+", "Emergency", "Sukkur", "Civil Hospital",
                 2, 0, 2, "Pending", 1, "2026-11-06 09:00:00"),
                (2, "O-", "Normal", "Sukkur", "Civil Hospital",
                 1, 1, 0, "Fulfilled", 1, "2026-11-05 09:00:00"),
                (3, "B+", "Normal", "Sukkur", "Civil Hospital",
                 1, 0, 1, "Cancelled", 1, "2026-11-04 09:00:00"),
                (4, "AB+", "Normal", "Karachi", "City Hospital",
                 1, 0, 1, "Fulfilled", 2, "2026-11-03 09:00:00"),
            ],
        )

        connection.executemany(
            """
            INSERT INTO donations
                (id, donor_id, donation_date, hospital, location, units,
                 status, requester_confirmed, request_id, match_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                # A confirmed donation made by this user's donor profile.
                (301, 101, "2026-11-06", "City Hospital", "Karachi",
                 1, "Confirmed", 1, 4, 401),
                # A donation received for this user's request, not made by them.
                (302, 201, "2026-11-06", "Civil Hospital", "Sukkur",
                 1, "Confirmed", 1, 1, 402),
                # An unconfirmed donation must not appear in completed history.
                (303, 101, "2026-11-06", "City Hospital", "Karachi",
                 1, "Reported", 0, 4, 403),
            ],
        )
        connection.commit()
        connection.close()

        self.connection_patch = patch(
            "app.get_db_connection",
            side_effect=self.connect_test_database,
        )
        self.connection_patch.start()

        self.client = flask_app.test_client()
        with self.client.session_transaction() as session_data:
            session_data["user_id"] = 1

    def tearDown(self):
        self.connection_patch.stop()
        flask_app.config["TESTING"] = self._old_testing
        self.temp_dir.cleanup()

    def connect_test_database(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def test_profile_counts_all_requests_and_separates_completed_requests(self):
        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertRegex(
            html,
            r'<span class="stat-label">\s*Total Blood Requests\s*</span>\s*'
            r'<span class="stat-number">\s*3\s*</span>',
        )
        self.assertRegex(
            html,
            r'<span class="stat-label">Completed Requests</span>\s*'
            r'<span class="stat-number">\s*1\s*</span>',
        )
        self.assertIn("Active Requests", html)
        self.assertIn("Request #1", html)
        self.assertIn("Request #2", html)
        self.assertIn("Request #3", html)
        self.assertNotIn("Request #4", html)

    def test_donation_history_contains_only_confirmed_donations_made_by_user(self):
        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Donation #301", html)
        self.assertNotIn("Donation #302", html)
        self.assertNotIn("Donation #303", html)
        self.assertIn("Own Donor Profile", html)
        self.assertNotIn("Other Donor Profile", html)

    def test_profile_never_displays_another_users_account_details(self):
        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Own User", html)
        self.assertIn("own@example.com", html)
        self.assertNotIn("Other User", html)
        self.assertNotIn("other@example.com", html)

    def test_profile_page_does_not_repeat_logout_action(self):
        response = self.client.get("/profile")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Logout", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
