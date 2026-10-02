import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "sistema.db"

def connection():
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT UNIQUE NOT NULL,
            nombres TEXT NOT NULL,
            apellidos TEXT NOT NULL,
            resultado TEXT NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS obligaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER NOT NULL,
            entidad TEXT NOT NULL,
            tipo TEXT NOT NULL,
            estado TEXT NOT NULL,
            monto REAL NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS consultas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dni TEXT NOT NULL,
            resultado TEXT NOT NULL,
            fecha_hora TEXT NOT NULL
        )
    """)

    count = cur.execute("SELECT COUNT(*) FROM clientes").fetchone()[0]
    if count == 0:
        demo_clients = [
            ("76302274", "Carlos", "Ramírez Torres", "CON INFORMACIÓN"),
            ("70451236", "María", "Gómez Salazar", "SIN INFORMACIÓN NEGATIVA"),
            ("45871263", "Luis", "Paredes Mendoza", "CON INFORMACIÓN")
        ]

        for dni, nombres, apellidos, resultado in demo_clients:
            cur.execute(
                "INSERT INTO clientes (dni,nombres,apellidos,resultado) VALUES (?,?,?,?)",
                (dni, nombres, apellidos, resultado)
            )

        client_ids = {
            row["dni"]: row["id"]
            for row in cur.execute("SELECT id,dni FROM clientes").fetchall()
        }

        demo_obligations = [
            (client_ids["76302274"], "Entidad Demo A", "Crédito personal", "VIGENTE", 1250.00, "2026-09-15"),
            (client_ids["76302274"], "Entidad Demo B", "Tarjeta", "PAGADO", 0.00, "2026-07-10"),
            (client_ids["70451236"], "Entidad Demo C", "Crédito personal", "PAGADO", 0.00, "2026-08-22"),
            (client_ids["45871263"], "Entidad Demo D", "Préstamo", "VENCIDO", 3280.50, "2026-09-28"),
        ]

        cur.executemany("""
            INSERT INTO obligaciones
            (cliente_id, entidad, tipo, estado, monto, fecha)
            VALUES (?,?,?,?,?,?)
        """, demo_obligations)

    conn.commit()
    conn.close()

def get_client_by_dni(dni):
    conn = connection()
    client = conn.execute(
        "SELECT * FROM clientes WHERE dni = ?", (dni,)
    ).fetchone()

    if not client:
        conn.close()
        return None

    obligations = conn.execute("""
        SELECT entidad, tipo, estado, monto, fecha
        FROM obligaciones
        WHERE cliente_id = ?
        ORDER BY fecha DESC
    """, (client["id"],)).fetchall()

    result = dict(client)
    result["obligaciones"] = [dict(row) for row in obligations]
    conn.close()
    return result

def get_all_clients():
    conn = connection()
    rows = conn.execute(
        "SELECT dni,nombres,apellidos,resultado FROM clientes ORDER BY apellidos"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_query(dni, resultado):
    conn = connection()
    conn.execute(
        "INSERT INTO consultas (dni,resultado,fecha_hora) VALUES (?,?,?)",
        (dni, resultado, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()
