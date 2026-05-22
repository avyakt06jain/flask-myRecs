import sqlite3
from pathlib import Path

import click
from flask import current_app, g
from werkzeug.security import generate_password_hash


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE COLLATE NOCASE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    buyer_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price_cents INTEGER NOT NULL CHECK (unit_price_cents >= 0),
    status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'paid', 'cancelled')),
    notes TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_records_user_created ON records (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_records_user_status ON records (user_id, status);

CREATE TRIGGER IF NOT EXISTS records_updated_at
AFTER UPDATE ON records
FOR EACH ROW
BEGIN
    UPDATE records SET updated_at = CURRENT_TIMESTAMP WHERE id = OLD.id;
END;
"""


def get_db():
    if "db" not in g:
        Path(current_app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def initialize_database(seed_demo=False):
    db = get_db()
    db.executescript(SCHEMA)
    if seed_demo:
        seed_demo_data(db)
    db.commit()


def seed_demo_data(db):
    existing = db.execute("SELECT id FROM users WHERE email = ?", ("demo@myrecs.local",)).fetchone()
    if existing:
        return

    cursor = db.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo Owner", "demo@myrecs.local", generate_password_hash("password123")),
    )
    user_id = cursor.lastrowid
    db.executemany(
        """
        INSERT INTO records (user_id, buyer_name, product_name, quantity, unit_price_cents, status, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (user_id, "Aarav Stores", "Wireless Keyboard", 3, 249900, "paid", "Delivered with invoice."),
            (user_id, "Bright Cafe", "Thermal Rolls", 20, 4500, "open", "Repeat order expected next month."),
            (user_id, "Kiran Labs", "USB-C Dock", 2, 599900, "open", ""),
        ],
    )


@click.command("init-db")
@click.option("--seed-demo", is_flag=True, help="Create a demo account with sample records.")
def init_db(seed_demo):
    initialize_database(seed_demo=seed_demo)
    click.echo("Initialized the MyRecs database.")
