import unittest

from app import get_compatible_donor_groups, locations_match


class LocationMatchingTests(unittest.TestCase):
    def test_city_matches_province_suffix(self):
        self.assertTrue(locations_match("Sukkur", "Sukkur, Sindh"))

    def test_city_matches_city_suffix(self):
        self.assertTrue(locations_match("Sukkur, Sindh", "Sukkur City"))

    def test_same_city_with_different_localities(self):
        self.assertTrue(
            locations_match("Gulshan-e-Iqbal, Karachi", "DHA, Karachi")
        )

    def test_different_cities_do_not_match(self):
        self.assertFalse(locations_match("Sukkur", "Rohri"))

    def test_empty_location_never_matches(self):
        self.assertFalse(locations_match("", "Sukkur"))
        self.assertFalse(locations_match("Sukkur", None))


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
