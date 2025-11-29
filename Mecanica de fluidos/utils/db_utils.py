# utils/db_utils.py
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

def _table_exists(conn, name: str) -> bool:
    row = conn.execute(
        text("SELECT name FROM sqlite_master WHERE type='table' AND name=:n;"),
        {"n": name}
    ).fetchone()
    return row is not None

def _columns(conn, table: str):
    return [r[1] for r in conn.execute(text(f"PRAGMA table_info({table});"))]

def _unique(base: str, used: set) -> str:
    base = (base or "user").strip() or "user"
    cand = base
    i = 1
    while cand in used:
        cand = f"{base}_{i}"
        i += 1
    used.add(cand)
    return cand

def ensure_schema(db):
    """
    Migra automáticamente tabla 'user' antigua (con columna 'correo')
    a nueva (con 'username' UNIQUE). Blindado: no rompe el arranque si falla.
    """
    try:
        engine = db.engine
    except Exception:
        return

    try:
        with engine.begin() as conn:
            # Si no hay tabla user, no hay nada que migrar
            if not _table_exists(conn, "user"):
                return

            cols = _columns(conn, "user")
            if "username" in cols:
                return  # ya migrado

            # Crear tabla nueva con esquema correcto
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username VARCHAR(80) NOT NULL UNIQUE,
                    password VARCHAR(200) NOT NULL
                );
            """))

            used = set()
            insert_stmt = text(
                "INSERT OR IGNORE INTO user_new (id, username, password) "
                "VALUES (:id, :u, :p);"
            )

            if "correo" in cols:
                # Migrar desde correo -> username
                rows = conn.execute(text("SELECT id, correo, password FROM user;")).fetchall()
                for uid, correo, pwd in rows:
                    base = (correo or f"user{uid}")
                    username = _unique(base, used)
                    conn.execute(insert_stmt, {"id": uid, "u": username, "p": pwd})
            else:
                # Generar usernames sintéticos
                rows = conn.execute(text("SELECT id, password FROM user;")).fetchall()
                for uid, pwd in rows:
                    username = _unique(f"user{uid}", used)
                    conn.execute(insert_stmt, {"id": uid, "u": username, "p": pwd})

            # Reemplazar tabla
            conn.execute(text("DROP TABLE user;"))
            conn.execute(text("ALTER TABLE user_new RENAME TO user;"))

    except SQLAlchemyError:
        # No propagamos errores de SQLite/SQLAlchemy
        pass
    except Exception:
        pass
