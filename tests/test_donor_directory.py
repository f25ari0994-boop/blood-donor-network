import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app import app as flask_app
from database import create_sqlite_tables, migrate_sqlite_database


class DonorDirectoryCompatibilitySearchTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = os.path.join(
            self.temp_dir.name,
            "donor-directory-test.db",
        )
        setup = sqlite3.connect(self.database_path)
        setup.row_factory = sqlite3.Row
        create_sqlite_tables(setup)
        migrate_sqlite_database(setup)

        setup.executemany(
            """
            INSERT INTO users (id, name, email, phone, password, cnic)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (1, "Directory User", "directory@example.com",
                 "03001111111", "hash", "1111111111111"),
                (2, "Donor Owner", "donor@example.com",
                 "03002222222", "hash", "2222222222222"),
            ],
        )

        donor_rows = [
            # Compatible blood group and matching city.
            ("Compatible Sukkur O Negative", 24, "03003333333", "O-",
             "Sukkur, Sindh", "Available", None, 1, 2,
             "Self-Declared Clear", 0),
            # Compatible blood group and matching city.
            ("Compatible Sukkur A Positive", 27, "03004444444", "A+",
             "Sukkur City", "Available", None, 1, 2,
             "Self-Declared Clear", 0),
            # Incompatible blood group for an A+ recipient.
            ("Incompatible AB Positive", 26, "03005555555", "AB+",
             "Sukkur", "Available", None, 1, 2,
             "Self-Declared Clear", 0),
            # Compatible group, wrong city.
            ("Wrong City O Negative", 29, "03006666666", "O-",
             "Rohri", "Available", None, 1, 2,
             "Self-Declared Clear", 0),
            # Compatible group and city, but unavailable.
            ("Unavailable O Negative", 31, "03007777777", "O-",
             "Sukkur", "Not Available", None, 1, 2,
             "Self-Declared Clear", 0),
            # Compatible group and city, but not health-screened.
            ("Ineligible O Negative", 32, "03008888888", "O-",
             "Sukkur", "Available", None, 0, 2,
             "Not Assessed", 0),
            # Compatible group and city, but donation was too recent.
            ("Recent Donation O Negative", 33, "03009999999", "O-",
             "Sukkur", "Available", "2026-11-01", 1, 2,
             "Self-Declared Clear", 0),
            # The logged-in user's own compatible donor profile remains visible.
            ("Own A Positive Profile", 25, "03001010101", "A+",
             "Sukkur", "Available", None, 1, 1,
             "Self-Declared Clear", 0),
        ]

        setup.executemany(
            """
            INSERT INTO donors (
                name, age, contact, blood_type, location, availability,
                last_donation, eligible, user_id,
                health_screening_status, share_contact
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            donor_rows,
        )
        setup.commit()
        setup.close()

        self.connection_patch = patch(
            "app.get_db_connection",
            side_effect=self.connect_test_database,
        )
        self.eligibility_patch = patch("app.check_donor_eligibility")
        self.active_request_patch = patch(
            "app.get_latest_active_request",
            return_value=None,
        )
        self.connection_patch.start()
        self.eligibility_patch.start()
        self.active_request_patch.start()

        self._old_testing = flask_app.config.get("TESTING", False)
        flask_app.config["TESTING"] = True
        self.client = flask_app.test_client()
        with self.client.session_transaction() as session_data:
            session_data["user_id"] = 1

    def tearDown(self):
        self.active_request_patch.stop()
        self.eligibility_patch.stop()
        self.connection_patch.stop()
        flask_app.config["TESTING"] = self._old_testing
        self.temp_dir.cleanup()

    def connect_test_database(self):
        connection = sqlite3.connect(self.database_path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def test_directory_filters_by_compatible_group_location_and_eligibility(self):
        response = self.client.get(
            "/donor-list",
            query_string={"blood_type": "A+", "location": "Sukkur"},
        )

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Compatible Sukkur O Negative", html)
        self.assertIn("Compatible Sukkur A Positive", html)
        self.assertIn("Own A Positive Profile", html)
        self.assertNotIn("Incompatible AB Positive", html)
        self.assertNotIn("Wrong City O Negative", html)
        self.assertNotIn("Unavailable O Negative", html)
        self.assertNotIn("Ineligible O Negative", html)
        self.assertNotIn("Recent Donation O Negative", html)
        self.assertIn("Compatible donor groups:", html)
        self.assertIn("Search Compatible Donors", html)

    def test_directory_without_compatibility_filters_keeps_all_donor_cards(self):
        response = self.client.get("/donor-list")

        self.assertEqual(response.status_code, 200)
        html = response.get_data(as_text=True)

        self.assertIn("Compatible Sukkur O Negative", html)
        self.assertIn("Incompatible AB Positive", html)
        self.assertIn("Wrong City O Negative", html)
        self.assertIn("Unavailable O Negative", html)

    def test_old_find_donors_get_url_redirects_to_directory_with_filters(self):
        response = self.client.get(
            "/search",
            query_string={"blood_type": "A+", "location": "Sukkur"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn("/donor-list?", response.headers["Location"])
        self.assertIn("blood_type=A%2B", response.headers["Location"])
        self.assertIn("location=Sukkur", response.headers["Location"])

    def test_old_find_donors_post_url_redirects_to_directory(self):
        with self.client.session_transaction() as session_data:
            session_data["_csrf_token"] = "legacy-search-csrf"

        response = self.client.post(
            "/search",
            data={
                "csrf_token": "legacy-search-csrf",
                "blood_type": "A+",
                "location": "Sukkur",
            },
        )

        self.assertEqual(response.status_code, 303)
        self.assertIn("/donor-list?", response.headers["Location"])
        self.assertIn("blood_type=A%2B", response.headers["Location"])
        self.assertIn("location=Sukkur", response.headers["Location"])

    def test_find_donors_navigation_and_duplicate_dashboard_action_are_removed(self):
        active_templates = (
            "dashboard.html",
            "donor.html",
            "donor_list.html",
            "emergency.html",
            "notifications.html",
            "profile.html",
        )

        for template_name in active_templates:
            content = Path("templates", template_name).read_text(
                encoding="utf-8"
            )
            self.assertNotIn("url_for('search')", content, template_name)
            self.assertNotIn("Find Donors", content, template_name)

        dashboard = Path("templates/dashboard.html").read_text(
            encoding="utf-8"
        )
        self.assertNotIn("Find Blood Donors", dashboard)
        self.assertFalse(Path("templates/search.html").exists())


if __name__ == "__main__":
    unittest.main()
