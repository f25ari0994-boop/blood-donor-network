from pathlib import Path
import unittest


LANGUAGE_SCRIPT = (
    Path(__file__).resolve().parents[1] / "static" / "js" / "language.js"
).read_text(encoding="utf-8")


class WebsiteLanguageCoverageTests(unittest.TestCase):
    def test_major_website_sections_have_urdu_and_sindhi_entries(self):
        required_phrases = (
            "Connecting donors. Supporting lives.",
            "Donor Registration",
            "Health Self-Assessment",
            "Create a blood request, find compatible requests, manage your matches",
            "Accepting this request starts the match immediately.",
            "Private Match Chat",
            "Activity Centre",
            "Stay updated about your blood donation and emergency request activity.",
            "Manage your account and view your personal activity.",
            "Report Blood Donation",
            "No donation records are available yet.",
            "Your blood request was cancelled.",
            "Unable to sign in right now. Please try again.",
        )
        for phrase in required_phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, LANGUAGE_SCRIPT)

    def test_primary_page_headings_and_brand_are_excluded_from_translation(self):
        self.assertIn('h1,.brand strong,[data-no-translate]', LANGUAGE_SCRIPT)
        self.assertIn('h1,.brand strong,[data-no-translate]', LANGUAGE_SCRIPT)

    def test_translation_scanner_covers_form_and_accessibility_attributes(self):
        self.assertIn('querySelectorAll("[placeholder],[aria-label],[alt],[title]")', LANGUAGE_SCRIPT)
        self.assertIn('input[type="submit"],input[type="button"],input[type="reset"]', LANGUAGE_SCRIPT)

    def test_rtl_language_metadata_is_applied(self):
        self.assertIn('document.documentElement.lang=lang==="Urdu"?"ur":"sd"', LANGUAGE_SCRIPT)
        self.assertIn('document.documentElement.dir="rtl"', LANGUAGE_SCRIPT)

    def test_live_dom_updates_are_observed_without_retranslating_primary_headings(self):
        self.assertIn("new MutationObserver", LANGUAGE_SCRIPT)
        self.assertIn('h1,.brand strong,[data-no-translate]', LANGUAGE_SCRIPT)


if __name__ == "__main__":
    unittest.main()
