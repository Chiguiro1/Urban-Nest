import sqlite3
import hashlib

def crear_tabla():
    conn = sqlite3.connect("usuarios.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            contra TEXT NOT NULL,
            verificado INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()
