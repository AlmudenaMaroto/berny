import sqlite3
import os
import shutil
from datetime import datetime


DB_NAME = "berny.db"
_db_dir = None


def set_db_dir(path):
    global _db_dir
    _db_dir = path


def get_db_path():
    if _db_dir:
        os.makedirs(_db_dir, exist_ok=True)
        return os.path.join(_db_dir, DB_NAME)
    return DB_NAME


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def export_db(dest_path: str):
    """Copy the database file to the given destination path."""
    src = get_db_path()
    # Force WAL checkpoint so all data is in the main file
    conn = get_connection()
    conn.execute("PRAGMA wal_checkpoint(FULL)")
    conn.close()
    shutil.copy2(src, dest_path)


def import_db(src_path: str):
    """Replace the current database with the given file."""
    dest = get_db_path()
    # Validate it's a real SQLite DB with our tables
    try:
        test_conn = sqlite3.connect(src_path)
        test_conn.execute("SELECT id FROM hives LIMIT 1")
        test_conn.execute("SELECT id FROM visits LIMIT 1")
        test_conn.close()
    except Exception as exc:
        raise ValueError(f"El archivo no es una base de datos Berny v\u00e1lida: {exc}")
    shutil.copy2(src_path, dest)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hives (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#F59E0B',
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hive_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            weather TEXT DEFAULT '',
            total_frames INTEGER DEFAULT 0,
            sealed_brood_frames INTEGER DEFAULT 0,
            open_brood_frames INTEGER DEFAULT 0,
            honey_frames INTEGER DEFAULT 0,
            bee_amount TEXT DEFAULT 'media',
            has_queen_cells INTEGER DEFAULT 0,
            drone_level TEXT DEFAULT 'bajo',
            feeding_type TEXT DEFAULT 'ninguna',
            varroa_treatment TEXT DEFAULT '',
            has_varroa INTEGER DEFAULT 0,
            has_super INTEGER DEFAULT 0,
            has_queen_excluder INTEGER DEFAULT 0,
            grid_mode TEXT DEFAULT 'invierno',
            hive_opened INTEGER DEFAULT 0,
            extra_food INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            FOREIGN KEY (hive_id) REFERENCES hives(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


# --- Hive CRUD ---

def create_hive(name: str, color: str = "#F59E0B") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO hives (name, color, created_at) VALUES (?, ?, ?)",
        (name, color, datetime.now().isoformat()),
    )
    conn.commit()
    hive_id = cursor.lastrowid
    conn.close()
    return hive_id


def get_all_hives():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT h.*, 
               (SELECT COUNT(*) FROM visits v WHERE v.hive_id = h.id) as visit_count,
               (SELECT v.date FROM visits v WHERE v.hive_id = h.id ORDER BY v.date DESC LIMIT 1) as last_visit_date
        FROM hives h
        ORDER BY h.name
    """)
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_hive(hive_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM hives WHERE id = ?", (hive_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_hive(hive_id: int, name: str, color: str = None):
    conn = get_connection()
    if color:
        conn.execute("UPDATE hives SET name = ?, color = ? WHERE id = ?", (name, color, hive_id))
    else:
        conn.execute("UPDATE hives SET name = ? WHERE id = ?", (name, hive_id))
    conn.commit()
    conn.close()


def delete_hive(hive_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM hives WHERE id = ?", (hive_id,))
    conn.commit()
    conn.close()


# --- Visit CRUD ---

def create_visit(hive_id: int, data: dict) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO visits 
           (hive_id, date, weather, total_frames, sealed_brood_frames, 
            open_brood_frames, honey_frames, bee_amount, has_queen_cells,
            drone_level, feeding_type, varroa_treatment, has_varroa, has_super,
            has_queen_excluder, grid_mode,
            hive_opened, extra_food, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            hive_id,
            data.get("date", datetime.now().strftime("%Y-%m-%d")),
            data.get("weather", ""),
            data.get("total_frames", 0),
            data.get("sealed_brood_frames", 0),
            data.get("open_brood_frames", 0),
            data.get("honey_frames", 0),
            data.get("bee_amount", "Media"),
            1 if data.get("has_queen_cells") else 0,
            data.get("drone_level", "Bajo"),
            data.get("feeding_type", "Ninguna"),
            data.get("varroa_treatment", "No"),
            1 if data.get("has_varroa") else 0,
            1 if data.get("has_super") else 0,
            1 if data.get("has_queen_excluder") else 0,
            data.get("grid_mode", "Invierno"),
            1 if data.get("hive_opened") else 0,
            1 if data.get("extra_food") else 0,
            data.get("notes", ""),
        ),
    )
    conn.commit()
    visit_id = cursor.lastrowid
    conn.close()
    return visit_id


def get_visits_for_hive(hive_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM visits WHERE hive_id = ? ORDER BY date DESC", (hive_id,)
    )
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_latest_visit(hive_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM visits WHERE hive_id = ? ORDER BY date DESC LIMIT 1",
        (hive_id,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_visit(visit_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM visits WHERE id = ?", (visit_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def update_visit(visit_id: int, data: dict):
    conn = get_connection()
    conn.execute(
        """UPDATE visits SET
           date=?, weather=?, total_frames=?, sealed_brood_frames=?,
           open_brood_frames=?, honey_frames=?, bee_amount=?, has_queen_cells=?,
           drone_level=?, feeding_type=?, varroa_treatment=?, has_varroa=?,
           has_super=?, has_queen_excluder=?, grid_mode=?, hive_opened=?, extra_food=?, notes=?
           WHERE id=?""",
        (
            data.get("date", ""),
            data.get("weather", ""),
            data.get("total_frames", 0),
            data.get("sealed_brood_frames", 0),
            data.get("open_brood_frames", 0),
            data.get("honey_frames", 0),
            data.get("bee_amount", "Media"),
            1 if data.get("has_queen_cells") else 0,
            data.get("drone_level", "Bajo"),
            data.get("feeding_type", "Ninguna"),
            data.get("varroa_treatment", "No"),
            1 if data.get("has_varroa") else 0,
            1 if data.get("has_super") else 0,
            1 if data.get("has_queen_excluder") else 0,
            data.get("grid_mode", "Invierno"),
            1 if data.get("hive_opened") else 0,
            1 if data.get("extra_food") else 0,
            data.get("notes", ""),
            visit_id,
        ),
    )
    conn.commit()
    conn.close()


def delete_visit(visit_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM visits WHERE id = ?", (visit_id,))
    conn.commit()
    conn.close()
