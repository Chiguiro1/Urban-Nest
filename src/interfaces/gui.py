from tkinter import Tk, Label, Button, Entry, messagebox
from database.crud import (
    crear_usuario,
    verificar_usuario,
    obtener_email_usuario,
    marcar_como_verificado
)
from auth.email_utils import enviar_codigo

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Urban Nest - Sistema de Usuarios")
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
        Label(self.root, text="Urban Nest", font=('Arial', 16, 'bold')).pack(pady=20)
        
        Button(self.root, text="Iniciar Sesión", command=self.mostrar_login, 
              width=20, height=2).pack(pady=10)
        Button(self.root, text="Registrarse", command=self.mostrar_registro,
              width=20, height=2).pack(pady=10)

    def mostrar_login(self):
        """Muestra la interfaz de login"""
        self.limpiar_pantalla()
        Label(self.root, text="Inicio de Sesión", font=('Arial', 14)).pack(pady=10)
        
        Label(self.root, text="Usuario:").pack()
        self.login_user = Entry(self.root, width=30)
        self.login_user.pack()
        
        Label(self.root, text="Contraseña:").pack()
        self.login_pass = Entry(self.root, show="*", width=30)
        self.login_pass.pack()
        
        Button(self.root, text="Ingresar", command=self.verificar_login,
              width=15).pack(pady=15)
        Button(self.root, text="Regresar", command=self.mostrar_menu_principal,
              width=10).pack()

    def mostrar_registro(self):
        """Muestra la interfaz de registro"""
        self.limpiar_pantalla()
        Label(self.root, text="Registro de Usuario", font=('Arial', 14)).pack(pady=10)
        
        Label(self.root, text="Nombre de usuario:").pack()
        self.reg_user = Entry(self.root, width=30)
        self.reg_user.pack()
        
        Label(self.root, text="Email:").pack()
        self.reg_email = Entry(self.root, width=30)
        self.reg_email.pack()
        
        Label(self.root, text="Contraseña:").pack()
        self.reg_pass = Entry(self.root, show="*", width=30)
        self.reg_pass.pack()
        
        Button(self.root, text="Registrarse", command=self.registrar_usuario,
              width=15).pack(pady=15)
        Button(self.root, text="Regresar", command=self.mostrar_menu_principal,
              width=10).pack()

    def mostrar_verificacion(self):
        """Muestra la interfaz de verificación"""
        self.limpiar_pantalla()
        Label(self.root, text="Verificación de Email", font=('Arial', 14)).pack(pady=10)
        Label(self.root, text=f"Código enviado a: {self.email_usuario}").pack()
        
        Label(self.root, text="Ingrese el código de verificación:").pack()
        self.codigo_entry = Entry(self.root, width=30)
        self.codigo_entry.pack(pady=10)
        
        Button(self.root, text="Verificar", command=self.verificar_codigo,
              width=15).pack(pady=5)
        Button(self.root, text="Reenviar código", command=self.reenviar_codigo,
              width=15).pack(pady=5)
        Button(self.root, text="Cancelar", command=self.mostrar_menu_principal,
              width=10).pack()

    def mostrar_panel_usuario(self):
        """Muestra el panel del usuario"""
        self.limpiar_pantalla()
        Label(self.root, text=f"Bienvenido, {self.usuario_actual}", 
              font=('Arial', 14)).pack(pady=20)
        Button(self.root, text="Cerrar Sesión", 
              command=self.mostrar_menu_principal, width=15).pack()

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
