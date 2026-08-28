import unittest

from ris_prescreener.core import classify_record


class ScreeningTests(unittest.TestCase):
    def setUp(self):
        self.groups = {"first concept": ["alpha"], "second concept": ["beta"]}

    def test_includes_when_all_required_groups_match(self):
        result = classify_record("Alpha beta", "", include_groups=self.groups, required_groups=self.groups)
        self.assertEqual(result["decision"], "INCLUDE")

    def test_exclude_has_priority(self):
        result = classify_record("Alpha beta obsolete", "", include_groups=self.groups, exclude_terms=["obsolete"], required_groups=self.groups)
        self.assertEqual(result["decision"], "EXCLUDE")
        self.assertIn("obsolete", result["exclude_hits"])

    def test_missing_group_is_excluded(self):
        result = classify_record("Alpha paper", "", include_groups=self.groups, required_groups=self.groups)
        self.assertEqual(result["decision"], "EXCLUDE")

    def test_language_can_be_required(self):
        result = classify_record("Alpha beta", "", "fr", include_groups=self.groups, required_groups=self.groups, require_language=True)
        self.assertEqual(result["decision"], "EXCLUDE")


if __name__ == "__main__":
    unittest.main()
