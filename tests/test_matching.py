import sqlite3
import unittest
from datetime import datetime

from app import (
    app as flask_app,
    PAKISTAN_TZ,
    activate_legacy_single_click_matches,
    get_notification_target_url,
    donor_has_active_match,
    donor_has_other_active_match,
    get_active_request_count,
    calculate_request_reminder_time,
    donor_matches_request,
    get_compatible_donor_groups,
    get_notification_recipient_user_ids,
    check_donor_eligibility,
    locations_match,
)


class RequestReminderTimingTests(unittest.TestCase):
    def test_twenty_hour_request_reminder_is_nine_hours_before_deadline(self):
        reminder = calculate_request_reminder_time(
            "2026-11-04 10:00:00",
            "2026-11-05 06:00:00",
        )
        self.assertEqual(
            reminder,
            datetime(2026, 11, 4, 21, 0, tzinfo=PAKISTAN_TZ),
        )

    def test_invalid_or_non_positive_duration_has_no_reminder(self):
        self.assertIsNone(
            calculate_request_reminder_time(
                "2026-11-05 06:00:00",
                "2026-11-04 10:00:00",
            )
        )
        self.assertIsNone(
            calculate_request_reminder_time("", "2026-11-05 06:00:00")
        )


class LocationMatchingTests(unittest.TestCase):
    def test_city_matches_province_suffix(self):
        self.assertTrue(locations_match("Sukkur", "Sukkur, Sindh"))

    def test_city_matches_city_suffix(self):
        self.assertTrue(locations_match("Sukkur, Sindh", "Sukkur City"))

    def test_same_city_with_different_localities(self):
        self.assertTrue(
            locations_match("Gulshan-e-Iqbal, Karachi", "DHA, Karachi")
        )

    def test_city_is_extracted_from_dash_separated_location(self):
        self.assertTrue(
            locations_match("Sukkur City - Old Town", "Sukkur, Sindh")
        )

    def test_different_cities_do_not_match(self):
        self.assertFalse(locations_match("Sukkur", "Rohri"))

    def test_empty_location_never_matches(self):
        self.assertFalse(locations_match("", "Sukkur"))
        self.assertFalse(locations_match("Sukkur", None))


class DonorRequestMatchingTests(unittest.TestCase):
    def test_a_positive_donor_matches_a_positive_request_in_sukkur(self):
        self.assertTrue(
            donor_matches_request("A+", "Sukkur", "A+", "Sukkur, Sindh")
        )

    def test_o_negative_donor_matches_a_positive_request(self):
        self.assertTrue(
            donor_matches_request("O-", "Sukkur", "A+", "Sukkur City")
        )

    def test_ab_positive_donor_does_not_match_a_positive_request(self):
        self.assertFalse(
            donor_matches_request("AB+", "Sukkur", "A+", "Sukkur")
        )

    def test_compatible_blood_group_in_a_different_city_does_not_match(self):
        self.assertFalse(
            donor_matches_request("A+", "Sukkur", "A+", "Rohri")
        )


class BloodRequestNotificationTargetTests(unittest.TestCase):
    def test_only_compatible_donors_in_same_city_are_notified_once(self):
        donor_rows = [
            (11, "A+", "Sukkur"),
            (12, "AB+", "Sukkur"),
            (13, "O-", "Rohri"),
            (14, "O-", "Sukkur, Sindh"),
            (11, "O-", "Sukkur"),
            (15, "A+", "Sukkur"),
            (None, "O-", "Sukkur"),
        ]

        self.assertEqual(
            get_notification_recipient_user_ids(
                donor_rows,
                "A+",
                "Sukkur City",
                excluded_user_id=15,
            ),
            [11, 14],
        )


class BloodCompatibilityTests(unittest.TestCase):
    def test_a_positive_recipient_has_expected_donor_groups(self):
        self.assertEqual(
            get_compatible_donor_groups("A+"),
            ["A+", "A-", "O+", "O-"],
        )

    def test_ab_positive_recipient_accepts_all_groups(self):
        self.assertEqual(
            get_compatible_donor_groups("AB+"),
            ["A+", "A-", "AB+", "AB-", "B+", "B-", "O+", "O-"],
        )




class ActiveRequestLimitTests(unittest.TestCase):
    def test_counts_only_pending_requests_with_units_remaining(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            """
            CREATE TABLE blood_requests (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                status TEXT,
                remaining_units INTEGER
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO blood_requests (user_id, status, remaining_units)
            VALUES (?, ?, ?)
            """,
            [
                (7, "Pending", 2),
                (7, "Pending", 1),
                (7, "Fulfilled", 0),
                (7, "Cancelled", 3),
                (7, "Pending", 0),
                (8, "Pending", 4),
            ],
        )
        self.assertEqual(get_active_request_count(connection, 7), 2)
        self.assertEqual(get_active_request_count(connection, 8), 1)
        connection.close()


class DonorProfileEligibilityIsolationTests(unittest.TestCase):
    def test_recalculating_one_profile_does_not_change_sibling_profiles(self):
        import os
        import tempfile
        from unittest.mock import patch

        with tempfile.TemporaryDirectory() as directory:
            database_path = os.path.join(directory, "eligibility-test.db")
            setup = sqlite3.connect(database_path)
            setup.execute(
                """
                CREATE TABLE donors (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    name TEXT,
                    last_donation TEXT,
                    eligible INTEGER,
                    availability TEXT,
                    health_screening_status TEXT
                )
                """
            )
            setup.execute(
                """
                CREATE TABLE notifications (
                    id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    message TEXT,
                    notification_type TEXT,
                    created_at TEXT,
                    related_request_id INTEGER,
                    related_match_id INTEGER
                )
                """
            )
            setup.executemany(
                """
                INSERT INTO donors
                    (id, user_id, name, last_donation, eligible,
                     availability, health_screening_status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (101, 7, "Rizwan", None, 0, "Not Available", "Self-Declared Clear"),
                    (102, 7, "Family member", None, 1, "Not Available", "Self-Declared Clear"),
                    (103, 7, "Other family member", None, 0, "Not Available", "Needs Professional Review"),
                ],
            )
            setup.commit()
            setup.close()

            with patch(
                "app.get_db_connection",
                side_effect=lambda: sqlite3.connect(database_path),
            ):
                check_donor_eligibility(7, donor_id=101)

            verify = sqlite3.connect(database_path)
            rows = {
                row[0]: row[1:]
                for row in verify.execute(
                    """
                    SELECT id, eligible, availability, health_screening_status
                    FROM donors
                    ORDER BY id
                    """
                ).fetchall()
            }
            verify.close()

            self.assertEqual(rows[101], (1, "Available", "Self-Declared Clear"))
            self.assertEqual(rows[102], (1, "Not Available", "Self-Declared Clear"))
            self.assertEqual(rows[103], (0, "Not Available", "Needs Professional Review"))


class DonorProfileActiveMatchTests(unittest.TestCase):
    def test_other_active_match_is_checked_per_profile_not_account(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            """
            CREATE TABLE request_matches (
                id INTEGER PRIMARY KEY,
                donor_id INTEGER,
                donor_user_id INTEGER,
                status TEXT
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO request_matches (id, donor_id, donor_user_id, status)
            VALUES (?, ?, ?, ?)
            """,
            [
                (1, 101, 7, "Invited"),
                (2, 102, 7, "Confirmed"),
            ],
        )

        self.assertFalse(donor_has_other_active_match(connection, 101, 1))
        self.assertTrue(donor_has_other_active_match(connection, 102, 99))
        self.assertFalse(donor_has_other_active_match(connection, 103, 99))
        connection.close()

    def test_active_match_is_scoped_to_donor_profile_not_account(self):
        connection = sqlite3.connect(":memory:")
        connection.execute(
            """
            CREATE TABLE request_matches (
                id INTEGER PRIMARY KEY,
                donor_id INTEGER,
                donor_user_id INTEGER,
                status TEXT
            )
            """
        )
        connection.execute(
            """
            INSERT INTO request_matches (donor_id, donor_user_id, status)
            VALUES (101, 7, 'Confirmed')
            """
        )
        self.assertTrue(donor_has_active_match(connection, 101))
        self.assertFalse(donor_has_active_match(connection, 102))
        connection.close()


class LegacySingleClickMatchTests(unittest.TestCase):
    def make_connection(self):
        connection = sqlite3.connect(":memory:")
        connection.executescript(
            """
            CREATE TABLE blood_requests (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                remaining_units INTEGER,
                status TEXT,
                needed_by TEXT
            );
            CREATE TABLE request_matches (
                id INTEGER PRIMARY KEY,
                request_id INTEGER,
                donor_id INTEGER,
                donor_user_id INTEGER,
                units_pledged INTEGER,
                status TEXT,
                requester_confirmed INTEGER,
                accepted_at TEXT,
                confirmed_at TEXT,
                updated_at TEXT
            );
            CREATE TABLE notifications (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                message TEXT,
                notification_type TEXT,
                created_at TEXT,
                related_request_id INTEGER,
                related_match_id INTEGER
            );
            """
        )
        connection.executemany(
            """
            INSERT INTO blood_requests
                (id, user_id, remaining_units, status, needed_by)
            VALUES (?, ?, ?, 'Pending', '2026-11-06 12:00:00')
            """,
            [(1, 10, 2), (2, 20, 1)],
        )
        connection.executemany(
            """
            INSERT INTO request_matches
                (id, request_id, donor_id, donor_user_id, units_pledged,
                 status, requester_confirmed, accepted_at, confirmed_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, 0, NULL, NULL, '2026-11-04 12:00:00')
            """,
            [
                (101, 1, 501, 50, 1, "Accepted"),
                (102, 2, 502, 51, 1, "Invited"),
            ],
        )
        connection.commit()
        return connection

    def test_legacy_accepted_and_invited_matches_become_active_once(self):
        from unittest.mock import patch

        connection = self.make_connection()
        with patch("app.get_current_time", return_value="2026-11-04 12:00:00"):
            with patch("app.is_request_expired", return_value=False):
                activate_legacy_single_click_matches(connection)

        rows = connection.execute(
            """
            SELECT id, status, requester_confirmed, confirmed_at
            FROM request_matches
            ORDER BY id
            """
        ).fetchall()
        self.assertEqual([row[1] for row in rows], ["Confirmed", "Confirmed"])
        self.assertEqual([row[2] for row in rows], [1, 1])
        self.assertTrue(all(row[3] for row in rows))
        self.assertEqual(
            connection.execute("SELECT COUNT(*) FROM notifications").fetchone()[0],
            4,
        )
        connection.close()

    def test_legacy_matches_do_not_overbook_request_units(self):
        from unittest.mock import patch

        connection = self.make_connection()
        connection.execute(
            """
            INSERT INTO request_matches
                (id, request_id, donor_id, donor_user_id, units_pledged,
                 status, requester_confirmed, updated_at)
            VALUES (103, 1, 503, 53, 2, 'Invited', 0, '2026-11-04 12:00:00')
            """
        )
        connection.commit()
        with patch("app.get_current_time", return_value="2026-11-04 12:00:00"):
            with patch("app.is_request_expired", return_value=False):
                activate_legacy_single_click_matches(connection)

        statuses = dict(
            connection.execute(
                "SELECT id, status FROM request_matches"
            ).fetchall()
        )
        self.assertEqual(statuses[101], "Confirmed")
        self.assertEqual(statuses[103], "Cancelled")
        connection.close()


class NotificationDestinationTests(unittest.TestCase):
    def test_match_notifications_prefer_potential_matches_over_request_history(self):
        with flask_app.test_request_context():
            self.assertEqual(
                get_notification_target_url(
                    "match_confirmed", request_id=7, match_id=None
                ),
                "/my-matches",
            )
            self.assertEqual(
                get_notification_target_url(
                    "match_confirmed", request_id=7, match_id=42
                ),
                "/my-matches#match-42",
            )
            self.assertEqual(
                get_notification_target_url(
                    "match_message", request_id=7, match_id=42
                ),
                "/my-matches#match-chat-42",
            )


if __name__ == "__main__":
    unittest.main()
