import unittest
from datetime import datetime

from app import (
    PAKISTAN_TZ,
    calculate_request_reminder_time,
    donor_matches_request,
    get_compatible_donor_groups,
    get_notification_recipient_user_ids,
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


if __name__ == "__main__":
    unittest.main()
