import sqlite3
import os
from contextlib import contextmanager
from database.models import ALL_TABLES

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, "..", "cyberbot.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for statement in ALL_TABLES:
            cursor.execute(statement)
        conn.commit()
    except sqlite3.Error as e:
        raise
    finally:
        conn.close()


@contextmanager
def get_cursor():
    conn = get_connection()
    try:
        cursor = conn.cursor()
        yield cursor
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
