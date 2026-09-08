"""Coverage must match each player's saved GP, not just a season's row count."""
import sqlite3
import tempfile
import unittest
from pathlib import Path

from database import set_db_override, clear_db_override
from player_coverage import season_coverage


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="nba_coverage_")
        self.path = Path(self.directory.name).resolve() / "test.db"
        set_db_override(str(self.path))
        self.db = sqlite3.connect(self.path)
        self.db.executescript("""
            CREATE TABLE player_season_stats (season_year INTEGER, player_id INTEGER, gp INTEGER);
            CREATE TABLE player_game_stats (season_year INTEGER, player_id INTEGER, game_id TEXT);
        """)

    def tearDown(self):
        self.db.close()
        clear_db_override()
        self.directory.cleanup()

    def season(self, player, gp, year=2025):
        self.db.execute("INSERT INTO player_season_stats VALUES (?, ?, ?)", (year, player, gp))

    def logs(self, player, count, year=2025):
        self.db.executemany("INSERT INTO player_game_stats VALUES (?, ?, ?)",
                            [(year, player, str(i)) for i in range(count)])

    def result(self):
        self.db.commit()
        return season_coverage(2025, 2025)[0]

    def test_summaries_exist_without_game_logs(self):
        self.season(1, 82)
        row = self.result()
        self.assertEqual((row['status'], row['season_rows'], row['missing_rows']), ('empty', 1, 82))

    def test_one_log_per_player_is_not_complete(self):
        for player in (1, 2):
            self.season(player, 3)
            self.logs(player, 1)
        row = self.result()
        self.assertEqual(row['collected_players'], 2)
        self.assertEqual(row['missing_players'], 0)
        self.assertEqual((row['status'], row['missing_rows']), ('partial', 4))

    def test_equal_total_counts_do_not_hide_per_player_mismatches(self):
        self.season(1, 3)
        self.season(2, 3)
        self.logs(1, 2)
        self.logs(2, 4)
        row = self.result()
        self.assertEqual(row['total_rows'], row['expected_rows'])
        self.assertEqual((row['status'], row['missing_rows'], row['extra_rows']), ('mismatch', 1, 1))

    def test_traded_player_team_rows_are_combined(self):
        self.season(1, 2)
        self.season(1, 3)
        self.logs(1, 5)
        row = self.result()
        self.assertEqual((row['status'], row['expected_players'], row['expected_rows']), ('complete', 1, 5))

    def test_unexpected_players_cannot_replace_missing_players(self):
        self.season(1, 2)
        self.logs(2, 2)
        row = self.result()
        self.assertEqual(row['status'], 'mismatch')
        self.assertEqual((row['collected_players'], row['unexpected_players'], row['missing_rows']), (0, 1, 2))

    def test_game_logs_without_a_reference_are_unverified(self):
        self.logs(1, 4)
        row = self.result()
        self.assertEqual((row['status'], row['expected_rows']), ('unverified', 0))
        self.assertEqual(row['logged_players'], 1)

    def test_exact_counts_match_the_saved_snapshot(self):
        self.season(1, 3)
        self.logs(1, 3)
        self.season(2, 0)
        row = self.result()
        self.assertEqual((row['status'], row['matched_rows'], row['expected_players']), ('complete', 3, 1))

    def test_empty_database_has_no_false_complete_status(self):
        self.assertEqual(self.result()['status'], 'empty')


if __name__ == '__main__':
    unittest.main()
