"""Compare stored individual game logs with stored player season totals."""
from database import query_db


def season_coverage(start_year, end_year):
    # A traded player's season may have multiple team rows.
    expected = query_db("""
        SELECT season_year, player_id, SUM(gp) AS games, COUNT(*) AS season_rows
        FROM player_season_stats WHERE gp > 0
        GROUP BY season_year, player_id
    """)
    collected = query_db("""
        SELECT season_year, player_id, COUNT(*) AS games
        FROM player_game_stats GROUP BY season_year, player_id
    """)
    expected_by_year, collected_by_year = {}, {}
    for row in expected:
        expected_by_year.setdefault(row['season_year'], {})[row['player_id']] = row
    for row in collected:
        collected_by_year.setdefault(row['season_year'], {})[row['player_id']] = row['games']

    seasons = []
    years = set(range(start_year, end_year + 1)) | set(expected_by_year) | set(collected_by_year)
    for year in sorted(years):
        players = expected_by_year.get(year, {})
        logs = collected_by_year.get(year, {})
        expected_rows = sum(row['games'] for row in players.values())
        total_rows = sum(logs.values())
        matched_rows = sum(min(row['games'], logs.get(pid, 0)) for pid, row in players.items())
        missing_rows = expected_rows - matched_rows
        extra_rows = total_rows - matched_rows
        covered = sum(logs.get(pid, 0) > 0 for pid in players)
        incomplete = sum(logs.get(pid, 0) != row['games'] for pid, row in players.items())
        if not total_rows:
            status = 'empty'
        elif not players:
            status = 'unverified'
        elif extra_rows:
            status = 'mismatch'
        elif missing_rows:
            status = 'partial'
        else:
            status = 'complete'
        seasons.append({
            'season': year,
            'expected_players': len(players),
            'collected_players': covered,
            'logged_players': len(logs),
            'missing_players': len(players) - covered,
            'players_needing_update': incomplete,
            'unexpected_players': len(set(logs) - set(players)),
            'season_rows': sum(row['season_rows'] for row in players.values()),
            'expected_rows': int(expected_rows),
            'total_rows': total_rows,
            'matched_rows': int(matched_rows),
            'missing_rows': int(missing_rows),
            'extra_rows': int(extra_rows),
            'status': status,
        })
    return seasons
