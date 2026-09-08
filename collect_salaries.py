"""
Standalone salary scraper using eu.hoopshype.com
Scrapes salary data via __NEXT_DATA__ JSON embedded in pages.

Usage:
  python collect_salaries.py              # Scrape + save JSON + insert DB
  python collect_salaries.py --scrape     # Only scrape to JSON (no DB)
  python collect_salaries.py --import     # Only import existing JSON to DB
"""
import sys
import os
import time
import json
import re
import requests
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database import get_db, init_db

# ---------------------------------------------------------------------------
# Season range
# ---------------------------------------------------------------------------
SEASON_START = 2004
_now = datetime.now()
SEASON_END = _now.year if _now.month >= 10 else _now.year - 1

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'files', 'salaries_scraped.json')

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# ---------------------------------------------------------------------------
# HoopsHype team ID → NBA API team ID
# ---------------------------------------------------------------------------
HH_TO_NBA = {
    '1':    1610612737,  # Atlanta Hawks
    '2':    1610612738,  # Boston Celtics
    '17':   1610612751,  # Brooklyn Nets
    '5312': 1610612766,  # Charlotte Hornets
    '4':    1610612741,  # Chicago Bulls
    '5':    1610612739,  # Cleveland Cavaliers
    '6':    1610612742,  # Dallas Mavericks
    '7':    1610612743,  # Denver Nuggets
    '8':    1610612765,  # Detroit Pistons
    '9':    1610612744,  # Golden State Warriors
    '10':   1610612745,  # Houston Rockets
    '11':   1610612754,  # Indiana Pacers
    '12':   1610612746,  # Los Angeles Clippers
    '13':   1610612747,  # Los Angeles Lakers
    '29':   1610612763,  # Memphis Grizzlies
    '14':   1610612748,  # Miami Heat
    '15':   1610612749,  # Milwaukee Bucks
    '16':   1610612750,  # Minnesota Timberwolves
    '3':    1610612740,  # New Orleans Pelicans
    '18':   1610612752,  # New York Knicks
    '25':   1610612760,  # Oklahoma City Thunder
    '19':   1610612753,  # Orlando Magic
    '20':   1610612755,  # Philadelphia 76ers
    '21':   1610612756,  # Phoenix Suns
    '22':   1610612757,  # Portland Trail Blazers
    '23':   1610612758,  # Sacramento Kings
    '24':   1610612759,  # San Antonio Spurs
    '28':   1610612761,  # Toronto Raptors
    '26':   1610612762,  # Utah Jazz
    '27':   1610612764,  # Washington Wizards
}

# (slug, hoopshype_id)
HH_TEAMS = [
    ('atlanta-hawks', '1'),         ('boston-celtics', '2'),
    ('brooklyn-nets', '17'),        ('charlotte-hornets', '5312'),
    ('chicago-bulls', '4'),         ('cleveland-cavaliers', '5'),
    ('dallas-mavericks', '6'),      ('denver-nuggets', '7'),
    ('detroit-pistons', '8'),       ('golden-state-warriors', '9'),
    ('houston-rockets', '10'),      ('indiana-pacers', '11'),
    ('los-angeles-clippers', '12'), ('los-angeles-lakers', '13'),
    ('memphis-grizzlies', '29'),    ('miami-heat', '14'),
    ('milwaukee-bucks', '15'),      ('minnesota-timberwolves', '16'),
    ('new-orleans-pelicans', '3'),  ('new-york-knicks', '18'),
    ('oklahoma-city-thunder', '25'),('orlando-magic', '19'),
    ('philadelphia-76ers', '20'),   ('phoenix-suns', '21'),
    ('portland-trail-blazers', '22'),('sacramento-kings', '23'),
    ('san-antonio-spurs', '24'),    ('toronto-raptors', '28'),
    ('utah-jazz', '26'),            ('washington-wizards', '27'),
]


# ===================================================================
# SCRAPE → JSON
# ===================================================================
def scrape_salaries(start_year=SEASON_START, end_year=SEASON_END):
    """Scrape eu.hoopshype.com for salary data. Returns list of dicts."""
    print(f"\n=== Scraping Salaries ({start_year}–{end_year}) ===")
    all_salaries = []

    for idx, (slug, hh_id) in enumerate(HH_TEAMS):
        nba_team_id = HH_TO_NBA[hh_id]
        team_display = slug.replace('-', ' ').title()

        team_count = 0
        for year in range(end_year, start_year - 1, -1):
            url = f"https://eu.hoopshype.com/salaries/teams/{slug}/{hh_id}/?season={year}"
            try:
                resp = requests.get(url, timeout=15, headers=HEADERS)
                if resp.status_code != 200:
                    continue

                nd = re.search(
                    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
                    resp.text, re.DOTALL
                )
                if not nd:
                    continue

                data = json.loads(nd.group(1))
                queries = (data.get('props', {})
                               .get('pageProps', {})
                               .get('dehydratedState', {})
                               .get('queries', []))

                for q in queries:
                    sd = q.get('state', {}).get('data', {})
                    if not isinstance(sd, dict) or 'contracts' not in sd:
                        continue

                    contracts = sd['contracts'].get('contracts', [])
                    for c in contracts:
                        player_name = c.get('playerName', '')
                        for s in c.get('seasons', []):
                            if s.get('season') == year:
                                sal = s.get('salary')
                                if sal and sal > 0:
                                    all_salaries.append({
                                        'player_name': player_name,
                                        'nba_team_id': nba_team_id,
                                        'season_year': year,
                                        'salary': sal,
                                    })
                                    team_count += 1
                    break  # found contracts query

                time.sleep(0.4)
            except Exception as e:
                print(f"    ✗ {team_display} {year}: {e}")

        print(f"  [{idx+1:>2}/30] ✓ {team_display} ({team_count} records)")

    # Save to JSON
    os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
    with open(JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_salaries, f, ensure_ascii=False, indent=2)

    print(f"\n  Saved {len(all_salaries)} salary records → files/salaries_scraped.json")
    return all_salaries


# ===================================================================
# Name normalization for matching
# ===================================================================
import unicodedata, re

_SUFFIXES = {'jr.', 'jr', 'sr.', 'sr', 'ii', 'iii', 'iv', 'v'}

# Characters that NFKD decomposition can't handle — need manual transliteration
# Covers German, Scandinavian, Baltic, Slavic, Turkish, etc.
_TRANSLIT = {
    'ö': 'o',  'ü': 'u',  'ä': 'a',  'ß': 'ss',     # German
    'ø': 'o',  'æ': 'ae', 'å': 'a',                    # Scandinavian
    'đ': 'dj', 'ð': 'd',  'Đ': 'Dj', 'Ð': 'D',        # Serbian đ→dj, Icelandic ð→d
    'ł': 'l',  'Ł': 'L',                                # Polish
    'ı': 'i',  'İ': 'I',  'ş': 's',  'Ş': 'S',        # Turkish
    'ğ': 'g',  'Ğ': 'G',                                # Turkish
    'ŋ': 'n',  'Ŋ': 'N',                                # Latvian  
    'œ': 'oe', 'Œ': 'OE',                               # French
    'þ': 'th', 'Þ': 'Th',                               # Icelandic
    'ħ': 'h',  'Ħ': 'H',                                # Maltese
    'ë': 'e',  'Ë': 'E',                                # Albanian / Russian translit
    'ñ': 'n',  'Ñ': 'N',                                # Spanish
}

def _strip_accents(text):
    """Remove ALL diacritics & transliterate special chars.
    Handles: ö→o, đ→d, ñ→n, č→c, ž→z, ģ→g, ņ→n, etc."""
    # Step 1: manual transliteration for chars NFKD can't decompose
    out = []
    for ch in text:
        if ch in _TRANSLIT:
            out.append(_TRANSLIT[ch])
        else:
            out.append(ch)
    text = ''.join(out)
    # Step 2: NFKD decomposition strips combining marks (accents, carons, cedillas, etc.)
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # Step 3: if anything non-ascii is left, force to ascii
    return ascii_text.encode('ascii', 'ignore').decode('ascii')
def _strip_accents_simple(text):
    """Simpler variant: đ→d (not dj). Used for alternate lookup keys."""
    out = []
    for ch in text:
        if ch in _TRANSLIT:
            # Use single-char replacement for đ/Đ
            r = _TRANSLIT[ch]
            out.append(r[0])  # just first char: dj→d, oe→o, etc.
        else:
            out.append(ch)
    text = ''.join(out)
    nfkd = unicodedata.normalize('NFKD', text)
    ascii_text = ''.join(c for c in nfkd if not unicodedata.combining(c))
    return ascii_text.encode('ascii', 'ignore').decode('ascii')
def _normalize(name):
    """Normalize player name: lowercase, strip accents, periods, smart quotes."""
    n = _strip_accents(name.strip()).lower()
    n = n.replace('.', '').replace("'", "'").replace("\u2019", "'")
    n = re.sub(r'\s+', ' ', n).strip()
    return n

def _name_without_suffix(name):
    """Remove Jr./Sr./III etc. from name."""
    parts = name.strip().split()
    while parts and parts[-1].lower().rstrip('.') in _SUFFIXES:
        parts.pop()
    return ' '.join(parts)

# Manual mappings for names that differ between HoopsHype and NBA API
# Keys = normalized HoopsHype name, Values = DB display_name
_MANUAL_MAP = {
    # Legal name changes
    'enes kanter':               'Enes Freedom',
    'patrick mills':             'Patty Mills',
    # German ö→oe transliteration (HH uses "oe", DB uses "ö"→"o")
    'dennis schroeder':          'Dennis Schröder',
    # Hyphenated / shortened names on HoopsHype
    'timothe luwawu':            'Timothe Luwawu-Cabarrot',
    'didier ilunga-mbenga':      'DJ Mbenga',
    'nigel hayes':               'Nigel Hayes-Davis',
    # Name changes / nicknames
    'carlton carrington':        'Bub Carrington',
    'maurice williams':          'Mo Williams',
    'joseph young':              'Joe Young',
    'ronald murray':             'Flip Murray',           # Flip = Ronald Murray
    'aleksandar pavlovic':       'Sasha Pavlovic',        # Sasha = Aleksandar
    # First/last name reversal (Asian name order)
    'hansen yang':               'Yang Hansen',
    # Greek/international name variants
    'iakovos tsakalidis':        'Jake Tsakalidis',       # Iakovos = Jake
    'sergey monya':              'Sergei Monia',           # different romanization
    'saer sene':                 'Mouhamed Sene',          # Saer = Mouhamed
    'walter tavares':            'Edy Tavares',            # Walter = Edy
    # Apostrophe / spelling variations
    "hamady n'diaye":            "Mamadou N'diaye",
    "boniface n'dong":           'Boniface Ndong',
    # Different romanization
    'wang zhizhi':               'Wang Zhi-zhi',
    # DJ / initials  
    'dj stewart':                'DJ Stewart',
    'dj steward':                'DJ Stewart',
}

# Direct ID mappings for ambiguous names (multiple players with same display_name)
_MANUAL_MAP_IDS = {
    'christapher johnson':       203187,   # Chris Johnson born 1990-04-29, active 2012-2015
}

def _build_player_lookup(cursor):
    """Build dict of normalized name → player_id for fast matching."""
    cursor.execute("SELECT id, display_name FROM players")
    lookup = {}
    for row in cursor.fetchall():
        pid = row['id']
        dn = row['display_name']
        # Primary key: fully normalized (đ→dj, accents stripped)
        key = _normalize(dn)
        if key not in lookup:
            lookup[key] = pid
        # Alt key: simple strip (đ→d) for alternate transliterations
        key_simple = _strip_accents_simple(dn.strip()).lower().replace('.', '').replace("'", "'")
        key_simple = re.sub(r'\s+', ' ', key_simple).strip()
        if key_simple not in lookup:
            lookup[key_simple] = pid
        # Also register without suffix
        key2 = _normalize(_name_without_suffix(dn))
        if key2 and key2 not in lookup:
            lookup[key2] = pid
        # Register with hyphens removed: "Luwawu-Cabarrot" → "luwawu cabarrot"
        key3 = key.replace('-', ' ')
        if key3 != key and key3 not in lookup:
            lookup[key3] = pid
        # Register first part of hyphenated last name:
        # "Nigel Hayes-Davis" → "nigel hayes", "Luwawu-Cabarrot" → already handled by manual map
        parts = key.split()
        if any('-' in p for p in parts):
            short_parts = [p.split('-')[0] for p in parts]
            key4 = ' '.join(short_parts)
            if key4 not in lookup:
                lookup[key4] = pid
        # Also register with apostrophes removed: "N'diaye" → "ndiaye"
        key5 = key.replace("'", '')
        if key5 != key and key5 not in lookup:
            lookup[key5] = pid
        # First name only for single-name players (Nenê)
        if ' ' not in key and key not in lookup:
            lookup[key] = pid

    # Add manual overrides
    for alias, real in _MANUAL_MAP.items():
        cursor.execute("SELECT id FROM players WHERE display_name = ?", (real,))
        row = cursor.fetchone()
        if row:
            lookup[alias] = row['id']
            # Also add without suffix variant
            alias2 = _normalize(_name_without_suffix(alias))
            if alias2 and alias2 != alias:
                lookup[alias2] = row['id']
    # Add direct ID overrides for ambiguous names
    for alias, pid in _MANUAL_MAP_IDS.items():
        lookup[alias] = pid
    return lookup


# ===================================================================
# JSON → DATABASE
# ===================================================================
def import_salaries_to_db(salaries=None):
    """Import salary data (list of dicts or from JSON file) into SQLite."""
    print("\n=== Importing Salaries into DB ===")

    if salaries is None:
        if not os.path.exists(JSON_PATH):
            print("  ✗ No salaries_scraped.json found. Run with --scrape first.")
            return
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            salaries = json.load(f)
        print(f"  Loaded {len(salaries)} records from JSON")

    conn = get_db()
    cursor = conn.cursor()

    # Build fast lookup table
    print("  Building player name lookup...")
    lookup = _build_player_lookup(cursor)

    inserted = 0
    skipped = 0
    unmatched = []  # (name, team_id, year, salary)

    for entry in salaries:
        player_name = entry['player_name']
        team_id = entry['nba_team_id']
        year = entry['season_year']
        salary = entry['salary']

        # Try matching in order of reliability
        player_id = None

        # 1. Exact normalized match
        key = _normalize(player_name)
        player_id = lookup.get(key)

        # 2. Without suffix: "Michael Porter Jr." → "Michael Porter"
        if not player_id:
            key2 = _normalize(_name_without_suffix(player_name))
            if key2 != key:
                player_id = lookup.get(key2)

        # 3. Hyphen-aware: "Timothe Luwawu" matches "timothe luwawu-cabarrot"
        if not player_id:
            clean = _normalize(_name_without_suffix(player_name))
            # Check if any lookup key STARTS WITH this name (partial hyphenated)
            candidates = [pid for k, pid in lookup.items()
                          if k.startswith(clean + ' ') or k.startswith(clean + '-') or k == clean]
            if len(candidates) == 1:
                player_id = candidates[0]

        # 4. First-initial + last-name match against lookup keys
        if not player_id:
            clean = _normalize(_name_without_suffix(player_name))
            clean_parts = clean.split()
            if len(clean_parts) >= 2:
                first_char = clean_parts[0][0]
                last = clean_parts[-1]
                candidates = [pid for k, pid in lookup.items()
                              if k.split()[0][0:1] == first_char and k.split()[-1] == last]
                if len(candidates) == 1:
                    player_id = candidates[0]

        # 5. Last-name exact + team roster check (for common last names)
        if not player_id:
            clean_parts = _normalize(_name_without_suffix(player_name)).split()
            if len(clean_parts) >= 2:
                last = clean_parts[-1]
                cursor.execute("""
                    SELECT DISTINCT p.id FROM players p
                    JOIN rosters r ON r.player_id = p.id
                    WHERE r.team_id = ? AND r.season_year = ?
                """, (team_id, year))
                roster_ids = {r['id'] for r in cursor.fetchall()}
                if roster_ids:
                    candidates = [(k, pid) for k, pid in lookup.items()
                                  if k.split()[-1] == last and pid in roster_ids]
                    if len(candidates) == 1:
                        player_id = candidates[0][1]

        if player_id:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO salaries
                    (player_id, team_id, season_year, salary)
                    VALUES (?, ?, ?, ?)
                ''', (player_id, team_id, year, salary))
                inserted += 1
            except Exception:
                skipped += 1
        else:
            skipped += 1
            unmatched.append({
                'player_name': player_name,
                'nba_team_id': team_id,
                'season_year': year,
                'salary': salary
            })

    conn.commit()
    conn.close()

    print(f"  ✓ Inserted {inserted} salary records")

    # Save full unmatched log
    if unmatched:
        unique_names = sorted(set(u['player_name'] for u in unmatched))
        print(f"  ⚠ {len(unique_names)} players not matched ({skipped} records skipped)")
        for name in unique_names[:15]:
            print(f"      - {name}")
        if len(unique_names) > 15:
            print(f"      ... and {len(unique_names) - 15} more")

        # Write full log
        log_path = os.path.join(BASE_DIR, 'files', 'salaries_unmatched.json')
        with open(log_path, 'w', encoding='utf-8') as f:
            json.dump(unmatched, f, ensure_ascii=False, indent=2)
        print(f"  📄 Full log: files/salaries_unmatched.json ({len(unmatched)} entries)")


# ===================================================================
# collect_salaries() — called from collect_all.py
# ===================================================================
def collect_salaries():
    """Full pipeline: scrape (if needed) + import into DB."""
    if os.path.exists(JSON_PATH):
        print("  Found existing salaries_scraped.json, using cached data.")
        print("  (Delete files/salaries_scraped.json to force re-scrape)")
        import_salaries_to_db()
    else:
        data = scrape_salaries()
        import_salaries_to_db(data)


# ===================================================================
# CLI
# ===================================================================
if __name__ == '__main__':
    init_db()

    if '--scrape' in sys.argv:
        scrape_salaries()
    elif '--import' in sys.argv:
        import_salaries_to_db()
    else:
        # Full: scrape + import
        data = scrape_salaries()
        import_salaries_to_db(data)

    print("\nDone!")
