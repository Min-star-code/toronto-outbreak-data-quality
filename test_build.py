"""Run:  python3 -m unittest -v"""

import csv
import sqlite3
import unittest

import build


class CleaningTests(unittest.TestCase):
    def test_tidy_collapses_spaces(self):
        self.assertEqual(build.tidy("  30  The Queensway "), "30 The Queensway")

    def test_agent_groups(self):
        self.assertEqual(build.agent_group("Influenza A (H3N2)"), "Influenza A")
        self.assertEqual(build.agent_group("Enterovirus/ Rhinovirus"), "Rhinovirus / Enterovirus")
        self.assertEqual(build.agent_group("Unable to identify"), "Not identified")
        self.assertEqual(build.agent_group("Rotavirus"), "Other")

    def test_parainfluenza_is_not_influenza(self):
        self.assertEqual(build.agent_group("Parainfluenza type 3"), "Parainfluenza")

    def test_address_key_ignores_punctuation_and_case(self):
        self.assertEqual(build.address_key("2701 St. Clair Ave E"), build.address_key("2701 St.Clair ave E"))

    def test_split_institution(self):
        self.assertEqual(build.split_institution("Michael Garron Hospital - H6"),
                         ("Michael Garron Hospital", "H6"))
        self.assertEqual(build.split_institution("Seaton House"), ("Seaton House", None))


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build.main()
        cls.db = sqlite3.connect(build.DB)

    def test_no_rows_lost_when_combining_files(self):
        source_rows = 0
        for path in build.RAW_DIR.glob("ob_report_*.csv"):
            with open(path, encoding="utf-8-sig", newline="") as handle:
                source_rows += sum(1 for _ in csv.DictReader(handle))
        self.assertEqual(self.db.execute("SELECT COUNT(*) FROM outbreaks").fetchone()[0], source_rows)

    def test_2020_columns_were_aligned(self):
        missing = self.db.execute(
            "SELECT COUNT(*) FROM outbreaks WHERE source_year = 2020 AND agent_1 = ''").fetchone()[0]
        self.assertEqual(missing, 0)

    def test_duration_only_for_closed_outbreaks(self):
        wrong = self.db.execute(
            "SELECT COUNT(*) FROM outbreaks WHERE (date_over IS NULL) <> (duration_days IS NULL)").fetchone()[0]
        self.assertEqual(wrong, 0)


if __name__ == "__main__":
    unittest.main()
