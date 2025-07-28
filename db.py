# db.py
import sqlite3
from datetime import datetime

DB_NAME = "rekomendasi.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nama TEXT,
        email TEXT,
        tanggal_upload TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        jenis TEXT,
        filename TEXT,
        path_file TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')

    conn.commit()
    conn.close()

def save_user(nama, email=""):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO users (nama, email, tanggal_upload) VALUES (?, ?, ?)", 
              (nama, email, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    user_id = c.lastrowid
    conn.commit()
    conn.close()
    return user_id

def save_document(user_id, jenis, filename, path_file):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO documents (user_id, jenis, filename, path_file) VALUES (?, ?, ?, ?)", 
              (user_id, jenis, filename, path_file))
    conn.commit()
    conn.close()

def get_user_info_by_id(user_id):
    """Mengambil nama, email, dan tanggal upload dari database berdasarkan user_id."""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT nama, email, tanggal_upload FROM users WHERE id = ?", (user_id,))
        user_data = c.fetchone()
        return user_data
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
