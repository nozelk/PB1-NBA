"""
Salary Import Health Check
==========================
Diagnoses salary→player matching issues. Shows:
  1. DB players with special characters — matched status
  2. Unmatched HoopsHype names with potential DB matches
  3. Important missing players (>$500K salary or 3+ seasons)
  4. Summary stats

Usage:
  python check_salaries.py            # full report
  python check_salaries.py --json     # JSON output (for admin API)
"""

import json, os, sys, sqlite3, unicodedata
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'nba.db')
UNMATCHED_PATH = os.path.join(BASE_DIR, 'files', 'salaries_unmatched.json')


def _strip_accents(text):
    """Remove diacritics from text."""
    _tr = {'đ':'dj','ð':'d','Đ':'Dj','Ð':'D','ö':'o','ü':'u','ä':'a',
           'ß':'ss','ø':'o','æ':'ae','ł':'l','ı':'i','ş':'s','ğ':'g',
           'ñ':'n','œ':'oe','ë':'e'}
    out = ''.join(_tr.get(c, c) for c in text)
    nfkd = unicodedata.normalize('NFKD', out)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def _norm(name):
    return _strip_accents(name.strip()).lower().replace('.','').replace("'","'")


def run_check(as_json=False):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    report = {
        'summary': {},
        'diacritic_players': [],
        'potential_matches': [],
        'important_missing': [],
        'all_unmatched': [],
    }

    # ── 1. Summary stats ─────────────────────────────────────────────
    total_sal = c.execute("SELECT COUNT(*) as n FROM salaries").fetchone()['n']
    unique_pl  = c.execute("SELECT COUNT(DISTINCT player_id) as n FROM salaries").fetchone()['n']
    total_pl   = c.execute("SELECT COUNT(*) as n FROM players").fetchone()['n']
    total_teams = c.execute("SELECT COUNT(*) as n FROM teams").fetchone()['n']

    report['summary'] = {
        'total_salary_records': total_sal,
        'unique_players_with_salary': unique_pl,
        'total_players_in_db': total_pl,
        'total_teams': total_teams,
    }

    # ── 2. DB players with special characters — salary status ────────
    c.execute("SELECT id, display_name FROM players")
    for r in c.fetchall():
        dn = r['display_name']
        if not any(ord(ch) > 127 for ch in dn):
            continue
        cnt = c.execute("SELECT COUNT(*) as n FROM salaries WHERE player_id=?",
                        (r['id'],)).fetchone()['n']
        entry = {
            'id': r['id'],
            'name': dn,
            'salary_records': cnt,
            'matched': cnt > 0,
        }
        report['diacritic_players'].append(entry)

    # ── 3. Load unmatched, find potential fixes ──────────────────────
    if os.path.exists(UNMATCHED_PATH):
        with open(UNMATCHED_PATH, 'r', encoding='utf-8') as f:
            unmatched = json.load(f)
    else:
        unmatched = []

    by_name = defaultdict(list)
    for u in unmatched:
        by_name[u['player_name']].append(u)

    report['summary']['unmatched_players'] = len(by_name)
    report['summary']['unmatched_records'] = len(unmatched)

    # Build DB lookup by last name
    c.execute("SELECT id, display_name FROM players")
    db_by_last = defaultdict(list)
    for r in c.fetchall():
        parts = _norm(r['display_name']).split()
        if parts:
            db_by_last[parts[-1]].append((r['id'], r['display_name']))

    for hh_name in sorted(by_name.keys()):
        entries = by_name[hh_name]
        total_salary = sum(e['salary'] for e in entries)
        years = sorted(set(e['season_year'] for e in entries))

        # Find potential DB matches (same last name + first initial)
        hh_norm = _norm(hh_name)
        hh_parts = hh_norm.split()
        potentials = []
        if hh_parts:
            first_char = hh_parts[0][0] if hh_parts[0] else ''
            # check all parts (incl. hyphenated)
            last_variants = set()
            for p in hh_parts:
                for sub in p.split('-'):
                    if len(sub) > 3:
                        last_variants.add(sub)
            for lv in last_variants:
                for pid, dn in db_by_last.get(lv, []):
                    dn_first = _norm(dn).split()[0][0] if _norm(dn).split() else ''
                    if dn_first == first_char:
                        sal_cnt = c.execute("SELECT COUNT(*) as n FROM salaries WHERE player_id=?",
                                           (pid,)).fetchone()['n']
                        potentials.append({
                            'db_id': pid,
                            'db_name': dn,
                            'existing_salaries': sal_cnt,
                        })

        entry = {
            'hh_name': hh_name,
            'total_salary': total_salary,
            'years': years,
            'num_records': len(entries),
            'potential_db_matches': potentials[:5],
        }
        report['all_unmatched'].append(entry)

        if total_salary > 500_000 or len(years) >= 3:
            report['important_missing'].append(entry)

    conn.close()

    # ── Output ───────────────────────────────────────────────────────
    if as_json:
        return report

    # Pretty print
    s = report['summary']
    print("=" * 80)
    print("  NBA SALARY IMPORT — HEALTH CHECK")
    print("=" * 80)
    print(f"  Salary records in DB:    {s['total_salary_records']:,}")
    print(f"  Players with salaries:   {s['unique_players_with_salary']:,} / {s['total_players_in_db']:,}")
    print(f"  Unmatched players:       {s['unmatched_players']} ({s['unmatched_records']} records)")

    # Diacritic players
    diac = report['diacritic_players']
    if diac:
        print(f"\n{'─' * 80}")
        print(f"  PLAYERS WITH SPECIAL CHARACTERS ({len(diac)} total)")
        print(f"{'─' * 80}")
        for p in sorted(diac, key=lambda x: x['name']):
            icon = "✓" if p['matched'] else "✗"
            cnt  = f"{p['salary_records']} salary records" if p['matched'] else "NO SALARIES"
            print(f"    {icon} {p['name']:35s} (id={p['id']})  {cnt}")

    # Important missing
    imp = report['important_missing']
    if imp:
        print(f"\n{'─' * 80}")
        print(f"  IMPORTANT MISSING PLAYERS ({len(imp)} — salary >$500K or 3+ seasons)")
        print(f"{'─' * 80}")
        for p in sorted(imp, key=lambda x: -x['total_salary']):
            yr_str = f"{p['years'][0]}-{p['years'][-1]}" if len(p['years']) > 1 else str(p['years'][0])
            print(f"    {p['hh_name']:30s}  ${p['total_salary']:>12,}  {yr_str:10s} ({p['num_records']} rec)")
            for m in p['potential_db_matches']:
                has = f"has {m['existing_salaries']} sal" if m['existing_salaries'] else "NO sal yet!"
                print(f"      → possible: {m['db_name']:30s} ({has})")

    # All unmatched with potential matches
    has_potential = [u for u in report['all_unmatched'] if u['potential_db_matches']]
    if has_potential:
        print(f"\n{'─' * 80}")
        print(f"  ALL POTENTIAL FIXABLE MATCHES ({len(has_potential)} names)")
        print(f"{'─' * 80}")
        for p in has_potential:
            yr_str = f"{p['years'][0]}-{p['years'][-1]}" if len(p['years']) > 1 else str(p['years'][0])
            print(f"    {p['hh_name']:30s}  ${p['total_salary']:>12,}  {yr_str}")
            for m in p['potential_db_matches']:
                has = f"{m['existing_salaries']} sal" if m['existing_salaries'] else "NO sal!"
                print(f"      → {m['db_name']:30s} (id={m['db_id']}, {has})")

    # Simple list of truly missing (no DB match at all)
    no_match = [u for u in report['all_unmatched'] if not u['potential_db_matches']]
    if no_match:
        print(f"\n{'─' * 80}")
        print(f"  NOT IN DATABASE ({len(no_match)} players — no matching DB entry)")
        print(f"{'─' * 80}")
        for p in no_match:
            yr_str = f"{p['years'][0]}-{p['years'][-1]}" if len(p['years']) > 1 else str(p['years'][0])
            print(f"    {p['hh_name']:30s}  ${p['total_salary']:>8,}  {yr_str}")

    print(f"\n{'=' * 80}")
    print(f"  DONE — {s['total_salary_records']:,} records OK, {s['unmatched_records']} unmatched")
    print(f"{'=' * 80}")

    return report


if __name__ == '__main__':
    if '--json' in sys.argv:
        data = run_check(as_json=True)
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    else:
        run_check()
