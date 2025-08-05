# =======================
# IMPORTS Y CONFIGURACIÓN
# =======================
import customtkinter as ctk
import os
from PIL import Image
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

global registrado
registrado = False

# ===========================
# CONFIGURACIÓN DE LA INTERFAZ
# ===========================
ctk.set_appearance_mode("System")
Base_Dir = os.path.dirname(__file__)
Path_Style = os.path.join(Base_Dir,"NightTrain.json")
Path_Logo = os.path.join(Base_Dir,"Logo.png")
ctk.set_default_color_theme(Path_Style)

# ===========================
# CLASE PRINCIPAL DE LA APP
# ===========================
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Urban Nest")   
        self.geometry("800x700")
        self.resizable(False, False)

        # Variables de estado
        self.codigo_verificacion = None
        self.usuario_actual = None
        self.email_usuario = None

        # Atributos para el sidebar
        self.sidebar_expanded = False
        self.sidebar_width_min = 50
        self.sidebar_width_max = 200
        self.sidebar_current_width = self.sidebar_width_min

        self.mostrar_menu_principal()

    # ========================
    # UTILIDADES DE INTERFAZ
    # ========================
    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    # ====================
    # ========== MAIN ==========
    # ====================
    def mostrar_menu_principal(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self, fg_color="#062741")
        frame.pack(expand=True, fill="both", padx=200, pady=100)
        logo_img = ctk.CTkImage(Image.open(Path_Logo), size=(120, 120))
        ctk.CTkLabel(frame, image=logo_img, text="").pack(pady=10)
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
        frame = ctk.CTkFrame(self, fg_color="transparent")
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
        user = self.login_user.get()
        contra = self.login_pass.get()
        
        if not user or not contra:
            messagebox.showwarning("Error", "Todos los campos son obligatorios")
            return

        # Verifica si el email existe
        existe = verificar_usuario(user)
        if not existe:
            messagebox.showerror("Error", "El email no existe")
            return

        # Verifica la contraseña
        from database.crud import hash_contraseña, conectar
        conn = None
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("SELECT contra FROM usuarios WHERE email = ?", (user,))
            resultado = cursor.fetchone()
            if resultado and resultado[0] == hash_contraseña(contra):
                global registrado
                registrado = True
                self.usuario_actual = user
                self.mostrar_panel_usuario()
            else:
                messagebox.showerror("Error", "La contraseña o el email no concuerdan")
        except Exception as e:
            messagebox.showerror("Error", f"Error al verificar usuario: {e}")
        finally:
            if conn:
                conn.close()

    # ===========================
    # ========== REGISTRO ==========
    # ===========================
    def mostrar_registro(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self, fg_color="transparent")
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
        frame = ctk.CTkFrame(self, fg_color="transparent")
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


    def toggle_sidebar(self):
        self.sidebar_expanded = not self.sidebar_expanded
        self.animate_sidebar()
        
    def animate_sidebar(self):
        target_width = self.sidebar_width_max if self.sidebar_expanded else self.sidebar_width_min
        if self.sidebar_current_width != target_width:
            step = 10 if self.sidebar_expanded else -10
            self.sidebar_current_width += step
            if hasattr(self, 'sidebar'):
                self.sidebar.configure(width=self.sidebar_current_width) # type: ignore

            # Mostrar/ocultar botones cuando esté expandido
            if self.sidebar_expanded and self.sidebar_current_width >= self.sidebar_width_max:
                self.button1.grid(row=1, column=0, pady=10, padx=10)
                self.button2.grid(row=2, column=0, pady=10, padx=10)
                self.button3.grid(row=3, column=0, pady=10, padx=10)
            elif not self.sidebar_expanded and self.sidebar_current_width <= self.sidebar_width_min:
                self.button1.grid_forget()
                self.button2.grid_forget()
                self.button3.grid_forget()

            self.after(10, self.animate_sidebar)
    # ================================
    # ========== PANEL USUARIO ==========
    # ================================
    def mostrar_panel_usuario(self):
        self.limpiar_pantalla()

        # Configuración de la grilla principal
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Estado inicial del sidebar
        self.sidebar_expanded = False
        self.sidebar_width_min = 50
        self.sidebar_width_max = 200
        self.sidebar_current_width = self.sidebar_width_min

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=self.sidebar_width_min, height=700, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.toggle_button = ctk.CTkButton(self.sidebar, text="☰", command=self.toggle_sidebar, width=40)
        self.toggle_button.pack(pady=10, padx=10)

        self.button1 = ctk.CTkButton(self.sidebar, text="Opción 1")
        self.button2 = ctk.CTkButton(self.sidebar, text="Opción 2")
        self.button3 = ctk.CTkButton(self.sidebar, text="Opción 3")
        # Los botones se muestran/ocultan en animate_sidebar

        ctk.CTkButton(self.sidebar, text="Soporte Técnico", command=self.soporte_tecnico, width=150, height=35).pack(pady=(30, 0))
        ctk.CTkButton(self.sidebar, text="Preguntas Frecuentes", command=self.preguntas_frecuentes, width=150, height=35).pack(pady=(10, 0))
        ctk.CTkButton(self.sidebar, text="Contáctanos", command=self.contactanos, width=150, height=35).pack(pady=(10, 0))
        ctk.CTkButton(self.sidebar, text="Asesorías", command=self.mostrar_asesorias, width=150, height=35).pack(pady=(10, 0))
        ctk.CTkButton(self.sidebar, text="Cerrar Sesión", command=self.mostrar_menu_principal, fg_color="#7a8894", width=150, height=35).pack(pady=(30, 0))

        # Contenido principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(main_frame, text=f"Bienvenido, {self.usuario_actual}", font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(pady=20)
        ctk.CTkLabel(main_frame, text="Panel de Usuario", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        ctk.CTkLabel(main_frame, text="""Se los juro que me
                     voy a suicidar si es que se daña esta mierda
                     hijos de puta""", font=ctk.CTkFont(size=30,weight="bold")).pack(pady=20)
    # ============================
    # ========== AYUDA ==========
    # ============================
    def soporte_tecnico(self):
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self, fg_color="transparent")
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
        frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
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
        frame = ctk.CTkFrame(self, fg_color="transparent")
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
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)

        ctk.CTkLabel(frame, text="Asesorías Personalizadas", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Próximamente disponible...").pack(pady=(10, 0))
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_panel_usuario, width=100, height=30, fg_color="#7a8894").pack(pady=10)

if __name__ == "__main__":
    app = App()
    app.mainloop()
