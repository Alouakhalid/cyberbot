CREATE_USERS_TABLE = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    NOT NULL UNIQUE,
    email         TEXT    NOT NULL UNIQUE,
    password_hash TEXT    NOT NULL,
    role          TEXT    NOT NULL DEFAULT 'student',
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    is_active     INTEGER NOT NULL DEFAULT 1
);
"""

CREATE_CHAT_LOGS_TABLE = """
CREATE TABLE IF NOT EXISTS chat_logs (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id        INTEGER NOT NULL,
    message        TEXT    NOT NULL,
    response       TEXT    NOT NULL,
    mode           TEXT    NOT NULL DEFAULT 'general',
    timestamp      TEXT    NOT NULL DEFAULT (datetime('now')),
    search_queries TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

CREATE_SESSIONS_TABLE = """
CREATE TABLE IF NOT EXISTS sessions (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    token      TEXT    NOT NULL UNIQUE,
    created_at TEXT    NOT NULL DEFAULT (datetime('now')),
    expires_at TEXT    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

CREATE_QUIZ_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS quiz_results (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    question   TEXT    NOT NULL,
    answer     TEXT    NOT NULL,
    is_correct INTEGER NOT NULL DEFAULT 0,
    topic      TEXT    NOT NULL,
    timestamp  TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
"""

ALL_TABLES = [
    CREATE_USERS_TABLE,
    CREATE_SESSIONS_TABLE,
    CREATE_CHAT_LOGS_TABLE,
    CREATE_QUIZ_RESULTS_TABLE,
]
