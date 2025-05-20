import sqlite3
import hashlib
from typing import Optional, List, Tuple

def conectar():
    """Establece conexión con la base de datos"""
    return sqlite3.connect("usuarios.db")

def hash_contraseña(contra: str) -> str:
    """Genera hash SHA-256 de una contraseña"""
    return hashlib.sha256(contra.encode()).hexdigest()

def crear_usuario(nombre: str, email: str, contra: str) -> bool:
    """Crea un nuevo usuario en la base de datos"""
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
        conn.close()

def verificar_usuario(nombre: str, contra: str) -> Tuple[bool, bool]:
    """Verifica si las credenciales son correctas y si el usuario está verificado"""
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT contra, verificado FROM usuarios WHERE nombre = ?", 
            (nombre,)
        )
        resultado = cursor.fetchone()
        
        if resultado:
            contra_hash, verificado = resultado
            return (contra_hash == hash_contraseña(contra), verificado)
        return (False, False)
    except sqlite3.Error as e:
        print(f"Error al verificar credenciales: {e}")
        return (False, False)
    finally:
        conn.close()

def obtener_email_usuario(nombre: str) -> Optional[str]:
    """Obtiene el email de un usuario por su nombre"""
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
        conn.close()

def marcar_como_verificado(nombre: str) -> bool:
    """Marca un usuario como verificado por email"""
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
        conn.close()
