import sqlite3
import hashlib
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '../../usuarios.db')

# =====================
# CREACIÓN DE TABLAS
# =====================
def crear_tabla_usuarios():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            contra TEXT NOT NULL,
            verificado INTEGER DEFAULT 0,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def crear_tabla_proyectos():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS proyectos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            ubicacion TEXT,
            precio REAL,
            tamano REAL,
            estado TEXT,
            descripcion TEXT,
            imagen_path TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def crear_tabla_citas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER,
            proyecto_id INTEGER,
            fecha DATE,
            hora TEXT,
            estado TEXT,
            creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(usuario_id) REFERENCES usuarios(id),
            FOREIGN KEY(proyecto_id) REFERENCES proyectos(id)
        )
    ''')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_usuario_fecha ON citas(usuario_id, fecha)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_citas_proyecto_fecha ON citas(proyecto_id, fecha)')
    conn.commit()
    conn.close()

# =====================
# SEED DE PROYECTOS Y USUARIO TEST
# =====================
def seed_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Proyectos
    cursor.execute('SELECT COUNT(*) FROM proyectos')
    if cursor.fetchone()[0] == 0:
        proyectos = [
            ("Apto Laureles", "Laureles", 420_000_000, 85, "Excelente", "Apartamento moderno en Laureles.", "static/placeholders/apt1.png"),
            ("Casa El Poblado", "El Poblado", 950_000_000, 210, "Buena", "Casa amplia con jardín.", "static/placeholders/apt2.png"),
            ("Loft Envigado", "Envigado", 350_000_000, 60, "Media", "Loft ideal para parejas.", "static/placeholders/apt3.png"),
            ("Penthouse Centro", "Centro", 780_000_000, 150, "Mala", "Penthouse con vista panorámica.", "static/placeholders/apt4.png"),
            ("Apto Belén", "Belén", 390_000_000, 75, "Excelente", "Apartamento cerca de parques.", "static/placeholders/apt5.png"),
            ("Casa Robledo", "Robledo", 500_000_000, 120, "Horrible", "Casa familiar en Robledo.", "static/placeholders/apt6.png"),
        ]
        cursor.executemany('''
            INSERT INTO proyectos (nombre, ubicacion, precio, tamano, estado, descripcion, imagen_path)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', proyectos)
    # Usuario test
    cursor.execute('SELECT COUNT(*) FROM usuarios WHERE email = ?', ("test@local",))
    if cursor.fetchone()[0] == 0:
        contra_hash = hashlib.sha256("test123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO usuarios (nombre, email, contra, verificado)
            VALUES (?, ?, ?, 1)
        ''', ("Usuario Test", "test@local", contra_hash))
    conn.commit()
    conn.close()

# =====================
# INICIALIZACIÓN GENERAL
# =====================
def init_db():
    crear_tabla_usuarios()
    crear_tabla_proyectos()
    crear_tabla_citas()
    seed_db()
