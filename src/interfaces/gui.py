import customtkinter as ctk
from tkinter import messagebox
from database.crud import (
    crear_usuario,
    verificar_usuario,
    obtener_email_usuario,
    marcar_como_verificado
)
from auth.email_utils import enviar_codigo

# Configuración inicial de CustomTkinter
ctk.set_appearance_mode("System")  # "Light", "Dark" o "System"
ctk.set_default_color_theme("blue")  # Temas: "blue", "green", "dark-blue"

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Urban Nest - ")
        self.root.geometry("500x400")
        self.codigo_verificacion = None
        self.usuario_actual = None
        self.email_usuario = None
        self.mostrar_menu_principal()

    def limpiar_pantalla(self):
        """Limpia todos los widgets de la ventana"""
        for widget in self.root.winfo_children():
            widget.destroy()

    def mostrar_menu_principal(self):
        """Muestra el menú principal"""
        self.limpiar_pantalla()
        
        # Frame principal para centrar contenido
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(frame, text="Urban Nest", 
                    font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkButton(frame, text="Iniciar Sesión", command=self.mostrar_login,
                    width=200, height=40, corner_radius=8).pack(pady=10)
        ctk.CTkButton(frame, text="Registrarse", command=self.mostrar_registro,
                    width=200, height=40, corner_radius=8).pack(pady=10)

    def mostrar_login(self):
        """Muestra la interfaz de login"""
        self.limpiar_pantalla()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        ctk.CTkLabel(frame, text="Inicio de Sesión",
                    font=ctk.CTkFont(size=16)).pack(pady=10)
        
        ctk.CTkLabel(frame, text="Usuario:").pack(pady=(10, 0))
        self.login_user = ctk.CTkEntry(frame, width=200)
        self.login_user.pack()
        
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=(10, 0))
        self.login_pass = ctk.CTkEntry(frame, show="*", width=200)
        self.login_pass.pack()
        
        ctk.CTkButton(frame, text="Ingresar", command=self.verificar_login,
                    width=150, height=35, corner_radius=8).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_menu_principal,
                    width=100, height=30, corner_radius=8, fg_color="gray40").pack()

    def mostrar_registro(self):
        """Muestra la interfaz de registro"""
        self.limpiar_pantalla()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        ctk.CTkLabel(frame, text="Registro de Usuario",
                    font=ctk.CTkFont(size=16)).pack(pady=10)
        
        ctk.CTkLabel(frame, text="Nombre de usuario:").pack(pady=(10, 0))
        self.reg_user = ctk.CTkEntry(frame, width=200)
        self.reg_user.pack()
        
        ctk.CTkLabel(frame, text="Email:").pack(pady=(10, 0))
        self.reg_email = ctk.CTkEntry(frame, width=200)
        self.reg_email.pack()
        
        ctk.CTkLabel(frame, text="Contraseña:").pack(pady=(10, 0))
        self.reg_pass = ctk.CTkEntry(frame, show="*", width=200)
        self.reg_pass.pack()
        
        ctk.CTkButton(frame, text="Registrarse", command=self.registrar_usuario,width=150,
                    height=35, corner_radius=8).pack(pady=20)
        ctk.CTkButton(frame, text="Regresar", command=self.mostrar_menu_principal,width=100,
                    height=30, corner_radius=8, fg_color="gray40").pack()

    def mostrar_verificacion(self):
        """Muestra la interfaz de verificación"""
        self.limpiar_pantalla()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=20)
        
        ctk.CTkLabel(frame, text="Verificación de Email",
                    font=ctk.CTkFont(size=16)).pack(pady=10)
        ctk.CTkLabel(frame, text=f"Código enviado a: {self.email_usuario}").pack()
        
        ctk.CTkLabel(frame, text="Ingrese el código de verificación:").pack(pady=(10, 0))
        self.codigo_entry = ctk.CTkEntry(frame, width=200)
        self.codigo_entry.pack(pady=10)
        
        ctk.CTkButton(frame, text="Verificar", command=self.verificar_codigo,
                    width=150, height=35, corner_radius=8).pack(pady=5)
        ctk.CTkButton(frame, text="Reenviar código", command=self.reenviar_codigo,
                    width=150, height=35, corner_radius=8).pack(pady=5)
        ctk.CTkButton(frame, text="Cancelar", command=self.mostrar_menu_principal,
                    width=100, height=30, corner_radius=8, fg_color="gray40").pack()

    def mostrar_panel_usuario(self):
        """Muestra el panel del usuario"""
        self.limpiar_pantalla()
        
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(expand=True, fill="both", padx=50, pady=50)
        
        ctk.CTkLabel(frame, text=f"Bienvenido, {self.usuario_actual}",
                    font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)
        ctk.CTkButton(frame, text="Cerrar Sesión", 
                    command=self.mostrar_menu_principal,
                    width=150, height=35, corner_radius=8).pack()

    # Métodos de lógica (se mantienen igual que en la versión original)
    def verificar_login(self):
        """Verifica las credenciales del usuario"""
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
        """Registra un nuevo usuario"""
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
        """Verifica el código ingresado"""
        codigo = self.codigo_entry.get()
        
        if codigo == self.codigo_verificacion:
            marcar_como_verificado(self.usuario_actual)
            messagebox.showinfo("Éxito", "Cuenta verificada correctamente")
            self.mostrar_panel_usuario()
        else:
            messagebox.showerror("Error", "Código incorrecto")

    def reenviar_codigo(self):
        """Reenvía el código de verificación"""
        self.codigo_verificacion = enviar_codigo(self.email_usuario, self.usuario_actual)
        if self.codigo_verificacion:
            messagebox.showinfo("Información", "Se ha reenviado el código")
        else:
            messagebox.showerror("Error", "No se pudo reenviar el código")
