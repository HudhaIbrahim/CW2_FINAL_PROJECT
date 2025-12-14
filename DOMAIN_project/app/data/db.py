import sqlite3
from pathlib import Path

# BASE_DIR = project root (week 8)
BASE_DIR = Path(__file__).resolve().parents[2]

# DATA folder
DATA_DIR = BASE_DIR / "DATA"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database path
DB_PATH = DATA_DIR / "intelligence_platform.db"

# DATABASE CONNECTION
def connect_database(db_path=DB_PATH):
    return sqlite3.connect(str(db_path))



