import sqlite3
import os
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba.db')
STAGING_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nba_staging.db')
BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')

# Thread-local override for DB path (used by staging collection)
_thread_local = threading.local()

def set_db_override(path):
    """Set a per-thread DB path override (for staging)."""
    _thread_local.db_path = path

def clear_db_override():
    """Clear the per-thread DB path override."""
    _thread_local.db_path = None

def get_db_path():
    """Get current DB path (thread-local override or default)."""
    return getattr(_thread_local, 'db_path', None) or DB_PATH

_MONTHS = {'JAN':'01','FEB':'02','MAR':'03','APR':'04','MAY':'05','JUN':'06',
           'JUL':'07','AUG':'08','SEP':'09','OCT':'10','NOV':'11','DEC':'12'}

def _date_iso(text):
    """Convert 'OCT 31, 2025' -> '2025-10-31' for sorting."""
    if not text:
        return '0000-00-00'
    try:
        parts = text.strip().split()
        mon = _MONTHS.get(parts[0][:3].upper(), '00')
        day = parts[1].rstrip(',').zfill(2)
        year = parts[2]
        return f'{year}-{mon}-{day}'
    except Exception:
        return '0000-00-00'

def get_db():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.create_function('date_iso', 1, _date_iso)
    return conn

def init_db():
    """Initialize database from baza.sql schema."""
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'baza.sql')
    with open(schema_path, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized successfully.")

def query_db(query, args=(), one=False):
    """Helper to run a query and return results as list of dicts."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    rows = cursor.fetchall()
    conn.close()
    if one:
        return dict(rows[0]) if rows else None
    return [dict(row) for row in rows]

def execute_db(query, args=()):
    """Helper to run an INSERT/UPDATE/DELETE."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, args)
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

if __name__ == '__main__':
    init_db()
    print("Tables created:")
    for t in query_db("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
        print(f"  - {t['name']}")