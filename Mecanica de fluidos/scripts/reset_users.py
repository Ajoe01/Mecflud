# scripts/reset_users.py
import os, sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'database.db')
DB_PATH = os.path.abspath(DB_PATH)

def table_exists(cur, name):
    cur.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?;", (name,))
    return cur.fetchone() is not None

def count(cur, tbl):
    cur.execute(f"SELECT COUNT(*) FROM {tbl};")
    return cur.fetchone()[0]

def main():
    if not os.path.exists(DB_PATH):
        print(f"[WARN] No existe: {DB_PATH}")
        return
    con = sqlite3.connect(DB_PATH)
    try:
        cur = con.cursor()
        # Desactiva FKs por si el esquema viejo no las define
        cur.execute("PRAGMA foreign_keys = OFF;")

        if table_exists(cur, 'attempt'):
            print(f"attempt antes: {count(cur,'attempt')}")
            cur.execute("DELETE FROM attempt;")
            print(f"attempt después: {count(cur,'attempt')}")

        if table_exists(cur, 'user'):
            print(f"user antes: {count(cur,'user')}")
            cur.execute("DELETE FROM user;")
            print(f"user después: {count(cur,'user')}")

        con.commit()
        cur.execute("VACUUM;")
        print("[OK] Usuarios y envíos borrados.")
    finally:
        con.close()

if __name__ == "__main__":
    main()
