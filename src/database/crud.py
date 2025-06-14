import sqlite3
import hashlib
from typing import Optional, Tuple

def conectar():
    """Establece conexión con la base de datos"""
    return sqlite3.connect("usuarios.db")

def hash_contraseña(contra: str) -> str:
    """Genera hash SHA-256 de una contraseña"""
    return hashlib.sha256(contra.encode()).hexdigest()

def crear_usuario(nombre: str, email: str, contra: str) -> bool:
    """Crea un nuevo usuario en la base de datos"""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO usuarios (nombre, email, contra) VALUES (?, ?, ?)",
            (nombre, email, hash_contraseña(contra))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError as e:
        print(f"Error al crear usuario: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def verificar_usuario(email: str) -> bool:
    """Verifica si el email existe en la base de datos"""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT 1 FROM usuarios WHERE email = ?", 
            (email,)
        )
        resultado = cursor.fetchone()
        return resultado is not None
    except sqlite3.Error as e:
        print(f"Error al verificar email: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()

def obtener_email_usuario(nombre: str) -> Optional[str]:
    """Obtiene el email de un usuario por su nombre"""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM usuarios WHERE nombre = ?", (nombre,))
        resultado = cursor.fetchone()
        return resultado[0] if resultado else None
    except sqlite3.Error as e:
        print(f"Error al obtener email: {e}")
        return None
    finally:
        if conn is not None:
            conn.close()

def marcar_como_verificado(nombre: str) -> bool:
    """Marca un usuario como verificado por email"""
    conn = None
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuarios SET verificado = 1 WHERE nombre = ?",
            (nombre,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error as e:
        print(f"Error al marcar como verificado: {e}")
        return False
    finally:
        if conn is not None:
            conn.close()
