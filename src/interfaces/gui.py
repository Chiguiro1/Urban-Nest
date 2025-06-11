# =======================
# IMPORTS Y CONFIGURACIÓN
# =======================
import customtkinter as ctk
from tkinter import messagebox
from auth.email_utils import (
    enviar_codigo,
    enviar_soporte_tecnico
)
from database.crud import (
    crear_usuario,
    verificar_usuario,
    obtener_email_usuario,
    marcar_como_verificado
)


# =======================
# CONFIGURACIÓN
# =======================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("NightTrain.json")

# ================
# CLASE PRINCIPAL
# ================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Urban Nest")   
        self.root.geometry("800x700")
        self.root.resizable(False, False)

        # Variables de estado
        self.codigo_verificacion = None
        self.usuario_actual = None
        self.email_usuario = None

        # Mostrar menú principal al iniciar
        self.mostrar_menu_principal()

    # =========================
    # UTILIDADES DE LA INTERFAZ
    # =========================
    def limpiar_pantalla(self):
        """Elimina todos los widgets de la ventana."""
        for widget in self.root.winfo_children():
            widget.destroy()

    # =========================
    # MENÚS PRINCIPALES
    # =========================
    def mostrar_menu_principal(self):
        """Menú principal con opciones de login y registro."""
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(frame, text="Urban Nest", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkButton(frame, text="Iniciar Sesión", command=self.mostrar_login, width=200, height=40).pack(pady=10)
        ctk.CTkButton(frame, text="Registrarse", command=self.mostrar_registro, width=200, height=40).pack(pady=10)

    def mostrar_login(self):
        """Pantalla de inicio de sesión."""
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Inicio de Sesión", font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkLabel(frame, text="Usuario:").pack(pady=(10, 0))
        self.login_user = ctk.CTkEntry(frame, width=200)
        self.login_user.pack()
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=(10, 0))
        self.login_pass = ctk.CTkEntry(frame, show="*", width=200)
        self.login_pass.pack()
        ctk.CTkButton(frame, text="Ingresar", command=self.verificar_login, width=150, height=35).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_menu_principal, width=100, height=30, fg_color="#7a8894").pack()

    def mostrar_registro(self):
        """Pantalla de registro de usuario."""
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Registro de Usuario", font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkLabel(frame, text="Nombre de usuario:").pack(pady=(10, 0))
        self.reg_user = ctk.CTkEntry(frame, width=200)
        self.reg_user.pack()
        ctk.CTkLabel(frame, text="Email:").pack(pady=(10, 0))
        self.reg_email = ctk.CTkEntry(frame, width=200)
        self.reg_email.pack()
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=(10, 0))
        self.reg_pass = ctk.CTkEntry(frame, show="*", width=200)
        self.reg_pass.pack()
        ctk.CTkButton(frame, text="Registrarse", command=self.registrar_usuario, width=150, height=35).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_menu_principal, width=100, height=30, fg_color="#7a8894").pack()

    def mostrar_verificacion(self):
        """Pantalla para ingresar el código de verificación."""
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Verificación de Email", font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkLabel(frame, text=f"Código enviado a: {self.email_usuario}").pack()
        ctk.CTkLabel(frame, text="Ingrese el código de verificación:").pack(pady=(10, 0))
        self.codigo_entry = ctk.CTkEntry(frame, width=200)
        self.codigo_entry.pack(pady=10)
        ctk.CTkButton(frame, text="Verificar", command=self.verificar_codigo, width=150, height=35).pack(pady=5)
        ctk.CTkButton(frame, text="Reenviar código", command=self.reenviar_codigo, width=150, height=35).pack(pady=5)
        ctk.CTkButton(frame, text="Cancelar", command=self.mostrar_menu_principal, width=100, height=30, fg_color="#7a8894").pack()

    def mostrar_panel_usuario(self):
        """Panel principal tras iniciar sesión."""
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=50)

        ctk.CTkLabel(frame, text=f"Bienvenido, {self.usuario_actual}", font=ctk.CTkFont(size=20, weight="bold")).place(x=50, y=10)
        ctk.CTkLabel(frame, font=ctk.CTkFont(size=15), text=f"""Hola {self.usuario_actual} bienvenido a Urban Nest, el futuro de las bienes raíces.\nContamos con las oportunidades de hogar más accesibles y hermosas en el mercado.\nEn la colmena todos deben ser felices.""").place(x=50, y=200)
        ctk.CTkButton(frame, text="Soporte Técnico", command=self.soporte_tecnico, width=150, height=35).place(x=50, y=300)
        ctk.CTkButton(frame, text="Cerrar Sesión", command=self.mostrar_menu_principal,fg_color="#7a8894", width=150, height=35).place(x=50, y=400)

    
    def soporte_tecnico(self):
        self.limpiar_pantalla()

        frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Soporte Técnico", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Por favor llena el siguiente formulario y describe tu problema:", anchor="w").pack(pady=5, fill="x")

        # Campos del formulario
        entry_nombre = ctk.CTkEntry(frame, placeholder_text="Nombre de usuario")
        entry_nombre.pack(pady=5, fill="x")

        entry_correo = ctk.CTkEntry(frame, placeholder_text="Correo electrónico")
        entry_correo.pack(pady=5, fill="x")

        entry_asunto = ctk.CTkEntry(frame, placeholder_text="Asunto")
        entry_asunto.pack(pady=5, fill="x")

        textbox_mensaje = ctk.CTkTextbox(frame, height=150)
        textbox_mensaje.pack(pady=5, fill="both")

        def enviar():
            nombre = entry_nombre.get().strip()
            correo = entry_correo.get().strip()
            asunto = entry_asunto.get().strip()
            mensaje = textbox_mensaje.get("1.0", "end").strip()

            if not (nombre and correo and asunto and mensaje):
                messagebox.showwarning("Campos incompletos", "Por favor llena todos los campos.")
                return

            resultado = enviar_soporte_tecnico(nombre, correo, asunto, mensaje)

            if resultado:
                messagebox.showinfo("Éxito", "Tu solicitud fue enviada correctamente.")
                # Opcional: limpiar los campos
                entry_nombre.delete(0, "end")
                entry_correo.delete(0, "end")
                entry_asunto.delete(0, "end")
                textbox_mensaje.delete("1.0", "end")
            else:
                messagebox.showerror("Error", "Ocurrió un error al enviar tu mensaje. Intenta más tarde.")

        ctk.CTkButton(frame, text="Enviar a soporte", command=enviar).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_panel_usuario, width=100, height=30, fg_color="#7a8894").pack(pady=10)

    # =========================
    # LÓGICA DE AUTENTICACIÓN
    # =========================
    def verificar_login(self):
        """Verifica usuario y contraseña."""
        usuario = self.login_user.get()
        contra = self.login_pass.get()

        if not usuario or not contra:
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        existe, verificado = verificar_usuario(usuario, contra)
        if not existe:
            messagebox.showerror("Error", "Usuario o contraseña incorrectos")
            return
        if not verificado:
            messagebox.showwarning("Error", "Debes verificar tu email primero")
            return

        self.usuario_actual = usuario
        self.mostrar_panel_usuario()

    def registrar_usuario(self):
        """Registra un nuevo usuario y envía código de verificación."""
        usuario = self.reg_user.get()
        email = self.reg_email.get()
        contra = self.reg_pass.get()

        if not usuario or not email or not contra:
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return
        if len(contra) < 6:
            messagebox.showwarning("Error", "La contraseña debe tener al menos 6 caracteres")
            return
        if not crear_usuario(usuario, email, contra):
            messagebox.showerror("Error", "El usuario o email ya existen")
            return

        self.usuario_actual = usuario
        self.email_usuario = email
        self.codigo_verificacion = enviar_codigo(email, usuario)
        if not self.codigo_verificacion:
            messagebox.showerror("Error", "No se pudo enviar el código de verificación")
            return

        self.mostrar_verificacion()

    def verificar_codigo(self):
        """Verifica el código ingresado por el usuario."""
        codigo = self.codigo_entry.get()
        if codigo == self.codigo_verificacion:
            marcar_como_verificado(self.usuario_actual)
            messagebox.showinfo("Éxito", "Cuenta verificada correctamente")
            self.mostrar_panel_usuario()
        else:
            messagebox.showerror("Error", "Código incorrecto")

    def reenviar_codigo(self):
        """Reenvía el código de verificación."""
        self.codigo_verificacion = enviar_codigo(self.email_usuario, self.usuario_actual)
        if self.codigo_verificacion:
            messagebox.showinfo("Información", "Se ha reenviado el código")
        else:
            messagebox.showerror("Error", "No se pudo reenviar el código")
