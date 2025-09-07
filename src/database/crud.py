import sqlite3
import hashlib
from datetime import datetime, date
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../usuarios.db')

# ========== USUARIOS ==========
def conectar():
    return sqlite3.connect(DB_PATH)

def hash_contraseña(contra: str) -> str:
    return hashlib.sha256(contra.encode()).hexdigest()

def crear_usuario(nombre, email, contra_plain):
    try:
        conn = conectar()
        cursor = conn.cursor()
        contra_hash = hash_contraseña(contra_plain)
        cursor.execute('INSERT INTO usuarios (nombre, email, contra) VALUES (?, ?, ?)', (nombre, email, contra_hash))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verificar_usuario(email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM usuarios WHERE email = ?', (email,))
    res = cursor.fetchone()
    conn.close()
    return res is not None

def verificar_usuario_contraseña(email, contra_plain):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT contra FROM usuarios WHERE email = ?', (email,))
    res = cursor.fetchone()
    conn.close()
    if res:
        return res[0] == hash_contraseña(contra_plain)
    return False

def marcar_como_verificado(email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE usuarios SET verificado = 1 WHERE email = ?', (email,))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok

def obtener_usuario_por_email(email):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM usuarios WHERE email = ?', (email,))
    res = cursor.fetchone()
    conn.close()
    return res

# ========== PROYECTOS ==========
def listar_proyectos(limit=None, offset=None, filtros=None):
    conn = conectar()
    cursor = conn.cursor()
    query = 'SELECT * FROM proyectos'
    params = []
    if filtros:
        query += ' WHERE ' + ' AND '.join([f"{k}=?" for k in filtros])
        params = list(filtros.values())
    if limit:
        query += ' LIMIT ?'
        params.append(limit)
    if offset:
        query += ' OFFSET ?'
        params.append(offset)
    cursor.execute(query, params)
    res = cursor.fetchall()
    conn.close()
    return res

def obtener_proyecto(id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM proyectos WHERE id = ?', (id,))
    res = cursor.fetchone()
    conn.close()
    return res

# ========== CITAS ==========
def crear_cita(usuario_id, proyecto_id, fecha, hora):
    try:
        # Validaciones
        hoy = date.today()
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
        if fecha_dt < hoy:
            return False, 'No puedes agendar en días pasados.'
        if fecha_dt.weekday() > 4:
            return False, 'Solo puedes agendar de lunes a viernes.'
        hora_permitidas = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0,30)]
        if hora not in hora_permitidas:
            return False, 'Hora fuera de rango permitido.'
        conn = conectar()
        cursor = conn.cursor()
        # Doble reserva
        cursor.execute('''SELECT 1 FROM citas WHERE proyecto_id=? AND fecha=? AND hora=? AND estado='Agendada' ''', (proyecto_id, fecha, hora))
        if cursor.fetchone():
            conn.close()
            return False, 'Ya existe una cita para ese proyecto en ese horario.'
        cursor.execute('''INSERT INTO citas (usuario_id, proyecto_id, fecha, hora, estado) VALUES (?, ?, ?, ?, 'Agendada')''', (usuario_id, proyecto_id, fecha, hora))
        conn.commit()
        conn.close()
        return True, 'Cita agendada correctamente.'
    except Exception as e:
        return False, str(e)

def listar_citas_por_usuario(usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM citas WHERE usuario_id = ? ORDER BY fecha, hora', (usuario_id,))
    res = cursor.fetchall()
    conn.close()
    return res

def cancelar_cita(cita_id, usuario_id):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('UPDATE citas SET estado = "Cancelada" WHERE id = ? AND usuario_id = ?', (cita_id, usuario_id))
    conn.commit()
    ok = cursor.rowcount > 0
    conn.close()
    return ok

def listar_citas_por_proyecto(proyecto_id, fecha):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('SELECT hora FROM citas WHERE proyecto_id = ? AND fecha = ? AND estado = "Agendada"', (proyecto_id, fecha))
    res = [r[0] for r in cursor.fetchall()]
    conn.close()
    return res
