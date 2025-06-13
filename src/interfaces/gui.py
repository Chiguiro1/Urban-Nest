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

registrado = False

# ===========================
# CONFIGURACIÓN DE LA INTERFAZ
# ===========================
ctk.set_appearance_mode("System")
ctk.set_default_color_theme(r"C:/Users/sapoq/Desktop/Programacion/Project_Python/Urban-Nest/src/interfaces/NightTrain.json")

# ===========================
# CLASE PRINCIPAL DE LA APP
# ===========================
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

        self.mostrar_menu_principal()

    # ========================
    # UTILIDADES DE INTERFAZ
    # ========================
    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ====================
    # ========== MAIN ==========
    # ====================
    def mostrar_menu_principal(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="#062741")
        frame.pack(expand=True, fill="both", padx=200, pady=100)

        ctk.CTkLabel(frame, text="Urban Nest", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkButton(frame, text="Iniciar Sesión", command=self.mostrar_login, width=200, height=40).pack(pady=10)
        ctk.CTkButton(frame, text="Registrarse", command=self.mostrar_registro, width=200, height=40).pack(pady=10)

        # Enlaces de ayuda
        soporte_label = ctk.CTkLabel(frame, text="FAQ", text_color="#5b40c5", cursor="hand2")
        soporte_label.pack(pady=(10, 0))
        soporte_label.bind("<Button-1>", lambda _: self.preguntas_frecuentes())

        contacto_label = ctk.CTkLabel(frame, text="Contáctanos", text_color="#5b40c5", cursor="hand2")
        contacto_label.pack()
        contacto_label.bind("<Button-1>", lambda _: self.contactanos())
        

    # ====================
    # ========== LOGIN ==========
    # ====================
    def mostrar_login(self):
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


    def verificar_login(self):
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

        global registrado
        registrado = True
        self.usuario_actual = usuario
        self.mostrar_panel_usuario()

    # ===========================
    # ========== REGISTRO ==========
    # ===========================
    def mostrar_registro(self):
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

    def registrar_usuario(self):
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

    # =============================
    # ========== VERIFICACIÓN ==========
    # =============================
    def mostrar_verificacion(self):
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
        ctk.CTkButton(frame, text="Cancelar", command=self.mostrar_menu_principal, width=100, height=30, fg_color="#7a8894").pack(pady=5)

    def verificar_codigo(self):
        codigo = self.codigo_entry.get()
        if codigo == self.codigo_verificacion:
            if self.usuario_actual is not None:
                marcar_como_verificado(self.usuario_actual)
                messagebox.showinfo("Éxito", "Cuenta verificada correctamente")
                self.mostrar_panel_usuario()
            else:
                messagebox.showerror("Error", "No se pudo verificar el usuario actual.")
        else:
            messagebox.showerror("Error", "Código incorrecto")

    def reenviar_codigo(self):
        self.codigo_verificacion = enviar_codigo(self.email_usuario, self.usuario_actual)
        if self.codigo_verificacion:
            messagebox.showinfo("Información", "Se ha reenviado el código")
        else:
            messagebox.showerror("Error", "No se pudo reenviar el código")

    # ================================
    # ========== PANEL USUARIO ==========
    # ================================
    def mostrar_panel_usuario(self):
        self.limpiar_pantalla()
        sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0, fg_color="#062741")
        sidebar.pack(side="left", fill="y")
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(side="left", fill="both", expand=True, padx=0, pady=20)

        #ctk.CTkButton(sidebar, text="Soporte Técnico", command=self.soporte_tecnico, width=150, height=35).place(x=25, y=300)
        #ctk.CTkButton(sidebar, text="Preguntas Frecuentes", command=self.preguntas_frecuentes, width=150, height=35).place(x=25, y=350)
        #ctk.CTkButton(sidebar, text="Contáctanos", command=self.contactanos, width=150, height=35).place(x=25, y=450)
        ctk.CTkButton(sidebar, text="Asesorías", command=self.mostrar_asesorias, width=150, height=35).place(x=25, y=500)
        ctk.CTkButton(sidebar, text="Cerrar Sesión", command=self.mostrar_menu_principal, fg_color="#7a8894", width=150, height=35).place(x=25, y=600)
        ctk.CTkLabel(sidebar, text=f"Bienvenido, {self.usuario_actual}", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=20)
        ctk.CTkLabel(frame, text="Panel de Usuario", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
    # ============================
    # ========== AYUDA ==========
    # ============================
    def soporte_tecnico(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Soporte Técnico", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Por favor llena el siguiente formulario y describe tu problema:", anchor="w").pack(pady=5, fill="x")

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
                entry_nombre.delete(0, "end")
                entry_correo.delete(0, "end")
                entry_asunto.delete(0, "end")
                textbox_mensaje.delete("1.0", "end")
            else:
                messagebox.showerror("Error", "Ocurrió un error al enviar tu mensaje. Intenta más tarde.")

        ctk.CTkButton(frame, text="Enviar a soporte", command=enviar).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_panel_usuario, width=100, height=30, fg_color="#7a8894").pack(pady=10)

    def preguntas_frecuentes(self):
        self.limpiar_pantalla()
        frame = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Preguntas Frecuentes y Soluciones", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(10, 20))

        preguntas_y_respuestas = [
            {
                "pregunta": "¿Qué hago si no recibo el código de verificación?",
                "respuesta": "Verifica tu carpeta de spam o correo no deseado..."
            },
            {
                "pregunta": "¿Por qué me aparece un error al iniciar sesión?",
                "respuesta": "Puede ser por un correo o contraseña incorrectos..."
            },
        ]

        for item in preguntas_y_respuestas:
            ctk.CTkLabel(frame, text=f"❓ {item['pregunta']}", font=ctk.CTkFont(size=14, weight="bold"), anchor="w", justify="left", wraplength=600).pack(fill="x", padx=10, pady=(5, 0))
            ctk.CTkLabel(frame, text=f"   {item['respuesta']}", font=ctk.CTkFont(size=13), anchor="w", justify="left", wraplength=600).pack(fill="x", padx=20, pady=(0, 10))

        def regresar():
            if self.usuario_actual:
                self.mostrar_panel_usuario()
            else:
                self.mostrar_menu_principal()
        ctk.CTkButton(frame, text="Regresar", command=regresar, width=100, height=30, fg_color="#7a8894").pack(pady=10)

    def contactanos(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Contáctanos", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Si tienes alguna duda o necesitas ayuda, envíanos un correo a:").pack(pady=(10, 0))
        ctk.CTkLabel(frame, text="auth.urbannest@gmail.com").pack(pady=(5, 20))
        def regresar():
            if self.usuario_actual:
                self.mostrar_panel_usuario()
            else:
                self.mostrar_menu_principal()
        ctk.CTkButton(frame, text="Regresar", command=regresar, width=100, height=30, fg_color="#7a8894").pack(pady=10)

    # ============================
    # ========== ASESORIAS =======
    # ============================

    def mostrar_asesorias(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Asesorías Personalizadas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Próximamente disponible...").pack(pady=(10, 0))
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_panel_usuario, width=100, height=30, fg_color="#7a8894").pack(pady=10)