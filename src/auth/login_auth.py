import customtkinter as ctk
from tkinter import messagebox
from database.crud import (
    crear_usuario,
    verificar_usuario,
    obtener_email_usuario,
    marcar_como_verificado
)
from auth.email_utils import enviar_codigo

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
