# =======================
# IMPORTS Y CONFIGURACIÓN
# =======================
import customtkinter as ctk
import sys
from tkinter import messagebox
from PIL import Image
import os
from database.crud import (
    crear_usuario, verificar_usuario, verificar_usuario_contraseña, marcar_como_verificado, obtener_usuario_por_email,
    listar_proyectos, obtener_proyecto, crear_cita, listar_citas_por_usuario, cancelar_cita, listar_citas_por_proyecto
)
from database.models import init_db
from customtkinter import CTkImage
from auth.email_utils import enviar_codigo, enviar_notificacion_cita

# -----------------------
# Resource helper (PyInstaller-friendly)
# -----------------------
def resource_path(relative_path: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS  # type: ignore
    else:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

# Rutas y tema
Base_Dir = os.path.dirname(__file__)
Path_Style = os.path.join(Base_Dir, "NightTrain.json")
# Logo cargado desde la carpeta images empaquetada
Path_Logo = resource_path(os.path.join("images", "logo.png"))

ctk.set_appearance_mode("System")
if os.path.exists(Path_Style):
    ctk.set_default_color_theme(Path_Style)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Urban Nest")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.usuario_actual = None
        self.sidebar_visible = True

        # Cargar logo si existe
        try:
            if os.path.exists(Path_Logo):
                logo_image = Image.open(Path_Logo).resize((60, 60))
                self.logo_img = CTkImage(logo_image)
            else:
                self.logo_img = None
        except Exception as e:
            print("Error cargando logo:", e)
            self.logo_img = None

        self.mostrar_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    # -------------------------
    # LOGIN / REGISTRO
    # -------------------------
    def mostrar_login(self):
        self.limpiar_pantalla()

        frame = ctk.CTkFrame(self, width=400, height=500, fg_color="#21244e")
        frame.pack(expand=True)
        frame.pack_propagate(False)

        # Usar logo desde images (si existe)
        logo_path = resource_path(os.path.join("images", "logo.png"))
        if os.path.exists(logo_path):
            try:
                logo_img = Image.open(logo_path).resize((120, 120))
                logo_ctk = CTkImage(light_image=logo_img, dark_image=logo_img, size=(120, 120))
                ctk.CTkLabel(frame, image=logo_ctk, text="").pack(pady=(20, 10))
                frame.logo_img = logo_ctk  # referencia para GC
            except Exception as e:
                print("Error cargando logo en login:", e)

        ctk.CTkLabel(
            frame,
            text="Urban Nest",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#37B8A0"
        ).pack(pady=(0, 20))

        usuario_entry = ctk.CTkEntry(frame, placeholder_text="Usuario", width=280)
        usuario_entry.pack(pady=10)

        password_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=280)
        password_entry.pack(pady=10)

        ctk.CTkButton(frame, text="Iniciar Sesión", fg_color="#37B8A0", hover_color="#2E9985",
                      command=lambda: self.verificar_login(usuario_entry.get(), password_entry.get())).pack(pady=20)

        ctk.CTkButton(frame, text="Registrarse", fg_color="#407996", hover_color="#49829f",
                      command=self.mostrar_registro).pack(pady=10)

    def verificar_login(self, email, password):
        if not email or not password:
            messagebox.showerror("Error", "Por favor ingresa tu correo y contraseña.")
            return

        if verificar_usuario_contraseña(email, password):
            self.usuario_actual = email
            self.mostrar_panel_usuario()
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o usuario no verificado.")

    def mostrar_verificacion_email(self, email):
        self.limpiar_pantalla()
        self.configure(bg_color="#e6ecf5")
        frame = ctk.CTkFrame(self, width=420, height=260, fg_color="#407996")
        frame.pack(expand=True)
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text="Verificación de correo", font=ctk.CTkFont(size=22, weight="bold"), text_color="#fff").pack(pady=18)
        ctk.CTkLabel(frame, text=f"Se envió un código a\n{email}", text_color="#fff").pack(pady=6)
        codigo_entry = ctk.CTkEntry(frame, placeholder_text="Código de verificación", width=180)
        codigo_entry.pack(pady=10)

        def verificar_codigo():
            codigo = codigo_entry.get()
            if not codigo:
                messagebox.showerror("Error", "Ingresa el código de verificación.")
                return
            if marcar_como_verificado(email, codigo):
                messagebox.showinfo("Verificado", "Correo verificado correctamente.")
                self.mostrar_login()
            else:
                messagebox.showerror("Error", "Código incorrecto or expirado.")

        ctk.CTkButton(frame, text="Verificar", command=verificar_codigo, width=180, fg_color="#21244e", hover_color="#1e214b").pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_login, width=180, fg_color="#ffb347", hover_color="#ff9800", text_color="#21244e").pack(pady=4)

    def mostrar_registro(self):
        self.limpiar_pantalla()
        self.configure(bg_color="#e6ecf5")
        frame = ctk.CTkFrame(self, width=420, height=470, fg_color="#407996")
        frame.pack(expand=True)
        frame.pack_propagate(False)
        ctk.CTkLabel(frame, text="").pack(pady=18)
        ctk.CTkLabel(frame, text="Registro de Usuario", font=ctk.CTkFont(size=26, weight="bold"), text_color="#fff").pack(pady=16)
        nombre_entry = ctk.CTkEntry(frame, placeholder_text="Nombre completo", width=280)
        nombre_entry.pack(pady=10)
        email_entry = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=280)
        email_entry.pack(pady=10)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=280)
        pass_entry.pack(pady=10)

        def registro_action():
            nombre = nombre_entry.get()
            email = email_entry.get()
            contra = pass_entry.get()
            if not nombre or not email or not contra:
                messagebox.showerror("Error", "Completa todos los campos.")
                return
            if len(contra) < 6:
                messagebox.showerror("Error", "La contraseña debe tener al menos 6 caracteres.")
                return
            if crear_usuario(nombre, email, contra):
                # Enviar código de verificación
                enviar_codigo(email, nombre)
                messagebox.showinfo("Registro exitoso", "Usuario registrado. Revisa tu correo para el código de verificación.")
                self.mostrar_verificacion_email(email)
            else:
                messagebox.showerror("Error", "El correo ya está registrado.")

        ctk.CTkButton(frame, text="Registrar", command=registro_action, width=240, fg_color="#21244e", hover_color="#1e214b").pack(pady=14)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_login, width=240, fg_color="#ffb347", hover_color="#ff9800", text_color="#21244e").pack(pady=6)

    # -------------------------
    # NAVBAR / PANEL USUARIO
    # -------------------------
    def mostrar_navbar(self):
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and getattr(widget, 'is_navbar', False):
                widget.destroy()
        nombre_usuario = None
        if self.usuario_actual:
            user = obtener_usuario_por_email(self.usuario_actual)
            if user:
                nombre_usuario = user[1]
        navbar = ctk.CTkFrame(self, height=60, fg_color="#1e214b")
        navbar.is_navbar = True
        navbar.pack(side="top", fill="x")
        navbar.grid_columnconfigure(0, weight=1)
        navbar.grid_columnconfigure(1, weight=8)
        ctk.CTkLabel(navbar, text=f"Usuario: {nombre_usuario if nombre_usuario else ''}", font=ctk.CTkFont(size=14), text_color="#dbf2f6", fg_color="#1e214b").grid(row=0, column=0, padx=20, pady=10, sticky="w")
        nav_btn_frame = ctk.CTkFrame(navbar, fg_color="#407996")
        nav_btn_frame.grid(row=0, column=1, pady=10, padx=10, sticky="e")
        btn_style = {"fg_color": "#407996", "hover_color": "#49829f", "text_color": "#fff", "corner_radius": 8, "border_width": 0, "height": 32, "width": 110}
        ctk.CTkButton(nav_btn_frame, text="Agendar Cita", command=self.mostrar_form_agendar, **btn_style).pack(side="left", padx=3)
        ctk.CTkButton(nav_btn_frame, text="Mis Citas", command=self.mostrar_mis_citas, **btn_style).pack(side="left", padx=3)
        ctk.CTkButton(nav_btn_frame, text="Soporte Técnico", command=self.mostrar_soporte_tecnico, **btn_style).pack(side="left", padx=3)
        ctk.CTkButton(nav_btn_frame, text="Preguntas Frecuentes", command=self.mostrar_faq, **btn_style).pack(side="left", padx=3)
        ctk.CTkButton(nav_btn_frame, text="Contáctanos", command=self.mostrar_contacto, **btn_style).pack(side="left", padx=3)
        ctk.CTkButton(nav_btn_frame, text="Cerrar Sesión", command=self.mostrar_login, fg_color="#7a8894", hover_color="#565B5E", text_color="#fff", corner_radius=8, border_width=0, height=32, width=110).pack(side="left", padx=3)

    def mostrar_panel_usuario(self):
        self.limpiar_pantalla()
        self.mostrar_navbar()
        nombre_usuario = None
        if self.usuario_actual:
            user = obtener_usuario_por_email(self.usuario_actual)
            if user:
                nombre_usuario = user[1]
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(main_frame, text=f"Bienvenido, {nombre_usuario if nombre_usuario else ''}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#dbf2f6").pack(pady=20)
        ctk.CTkLabel(main_frame, text="Proyectos disponibles", font=ctk.CTkFont(size=20, weight="bold"), text_color="#fff07e").pack(pady=10)
        self.mostrar_proyectos_grid(parent=main_frame)

    # -------------------------
    # GRID DE PROYECTOS (sin imágenes en la lista)
    # -------------------------
    def mostrar_proyectos_grid(self, parent=None):
        ESTADO_COLOR = {
            "Excelente": "#4caf50",
            "Buena": "#8bc34a",
            "Media": "#ffc107",
            "Mala": "#ff9800",
            "Deteriorada": "#f44336"
        }
        if parent is None:
            self.limpiar_pantalla()
            parent = ctk.CTkFrame(self, fg_color="transparent")
            parent.pack(fill="both", expand=True)

        proyectos = listar_proyectos()
        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(pady=20, padx=20, fill="both", expand=True)

        columnas = 3
        for i in range(columnas):
            grid.grid_columnconfigure(i, weight=1, uniform="col")
        filas = (len(proyectos) + columnas - 1) // columnas
        for i in range(filas):
            grid.grid_rowconfigure(i, weight=1, uniform="row")

        # NOTA: no cargamos imágenes aquí; las mostramos sólo en los detalles
        for idx, p in enumerate(proyectos):
            fila = idx // columnas
            col = idx % columnas
            card = ctk.CTkFrame(grid, width=400, height=220, fg_color="#21244e", corner_radius=16, border_width=2, border_color="#407996")
            card.grid(row=fila, column=col, padx=24, pady=24, sticky="nsew")
            ctk.CTkLabel(card, text=p[1], font=ctk.CTkFont(size=18, weight="bold"), text_color="#00e6e6").pack(pady=(16, 2))
            ctk.CTkLabel(card, text=f"Ubicación: {p[2]}", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            ctk.CTkLabel(card, text=f"Precio: ${p[3]:,.0f}", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            ctk.CTkLabel(card, text=f"Tamaño: {p[4]} m²", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            estado = p[5] if p[5] != "Horrible" else "Deteriorada"
            color_estado = ESTADO_COLOR.get(estado, "#888")
            estado_frame = ctk.CTkFrame(card, fg_color=color_estado, corner_radius=8)
            estado_frame.pack(pady=4)
            ctk.CTkLabel(estado_frame, text=f"Estado: {estado}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fff").pack(padx=8, pady=2)
            ctk.CTkButton(card, text="Detalles", width=300, fg_color="#407996", hover_color="#49829f", command=lambda idx=idx, pid=p[0]: self.mostrar_detalle_proyecto_custom(idx, pid)).pack(pady=2)

    # -------------------------
    # DETALLE DEL PROYECTO - CORREGIDO
    # -------------------------
    def mostrar_detalle_proyecto_custom(self, idx, proyecto_id):
        self.limpiar_pantalla()
        self.mostrar_navbar()

        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="#21244e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Frame de contenido con scroll
        content_frame = ctk.CTkScrollableFrame(main_frame, fg_color="#21244e")
        content_frame.pack(fill="both", expand=True, padx=10, pady=10)

        proyectos = listar_proyectos()
        p = next((pr for pr in proyectos if pr[0] == proyecto_id), None)
        if not p:
            messagebox.showerror("Error", "Proyecto no encontrado.")
            return

        # Cargar imágenes
        images_dir = resource_path(os.path.join('..', '..', 'images'))
        image_files = [os.path.join(images_dir, f'a{i+1}.jpeg') for i in range(6)]
        img_path = image_files[idx % len(image_files)] if os.path.exists(image_files[idx % len(image_files)]) else None
        img = None
        if img_path:
            try:
                pil_img = Image.open(img_path)
                display_size = (700, 450)
                pil_img = pil_img.resize(display_size)
                img = CTkImage(light_image=pil_img, dark_image=pil_img, size=display_size)
            except Exception as e:
                print("Error cargando imagen principal:", e)
                img = None
        if img:
            lbl_main = ctk.CTkLabel(content_frame, image=img, text="", width=700, height=450)
            lbl_main.pack(pady=(10, 15))
            lbl_main.image = img

        # Información del proyecto
        ctk.CTkLabel(content_frame, text=p[1], font=ctk.CTkFont(size=22, weight="bold"), text_color="#00e6e6").pack(pady=(0, 10))
        ctk.CTkLabel(content_frame, text=f"Ubicación: {p[2]}", font=ctk.CTkFont(size=15), text_color="#fff").pack(pady=2)
        ctk.CTkLabel(content_frame, text=f"Precio: ${p[3]:,.0f}", font=ctk.CTkFont(size=15), text_color="#fff").pack(pady=2)
        ctk.CTkLabel(content_frame, text=f"Tamaño: {p[4]} m²", font=ctk.CTkFont(size=15), text_color="#fff").pack(pady=2)

        estado = p[5] if p[5] != "Horrible" else "Deteriorada"
        ctk.CTkLabel(content_frame, text=f"Estado: {estado}", font=ctk.CTkFont(size=15, weight="bold"), text_color="#fff").pack(pady=(10, 10))

        # Descripción
        descripciones = [
            "Este apartamento en Laureles combina modernidad y comodidad en un entorno urbano privilegiado...",
            "Esta casa en El Poblado destaca por su amplitud y su hermoso jardín...",
            "El loft en Envigado es la elección ideal para parejas jóvenes o profesionales...",
            "El penthouse en el Centro ofrece una vista panorámica inigualable...",
            "Este apartamento en Belén se caracteriza por su proximidad a parques y zonas verdes...",
            "La casa en Robledo es una opción familiar que destaca por su amplitud..."
        ]
        desc_text = descripciones[idx] if 0 <= idx < len(descripciones) else "Descripción no disponible."
        ctk.CTkLabel(content_frame, text=desc_text, font=ctk.CTkFont(size=14), text_color="#fff", wraplength=800, justify="left").pack(pady=(10, 15))

        # Galería de miniaturas
        if image_files:
            ctk.CTkLabel(content_frame, text="Galería de imágenes:", font=ctk.CTkFont(size=16, weight="bold"), text_color="#fff07e").pack(pady=(10, 5))
            galeria_frame = ctk.CTkFrame(content_frame, fg_color="#1e214b")
            galeria_frame.pack(pady=10, fill="x")
            for i, img_file in enumerate(image_files):
                if os.path.exists(img_file):
                    try:
                        thumb = Image.open(img_file).resize((180, 135))
                        thumb_ctk = CTkImage(light_image=thumb, dark_image=thumb, size=(180, 135))
                        lbl = ctk.CTkLabel(galeria_frame, image=thumb_ctk, text="")
                        lbl.pack(side="left", padx=5, pady=5)
                        lbl.image = thumb_ctk
                        # Vincula el click a la función del carrusel
                        lbl.bind("<Button-1>", lambda e, idx=i: self.mostrar_carrusel_imagenes(image_files, idx))
                    except Exception as e:
                        print("Error cargando miniatura:", e)

        # Frame para botones (fijo en la parte inferior)
        btn_frame = ctk.CTkFrame(main_frame, fg_color="#21244e", height=60)
        btn_frame.pack(fill="x", pady=(10, 0))
        btn_frame.pack_propagate(False)
        
        # Botones centrados
        btn_container = ctk.CTkFrame(btn_frame, fg_color="transparent")
        btn_container.pack(expand=True)
        
        ctk.CTkButton(btn_container, text="Agendar cita", width=200, height=40,
                     fg_color="#4caf50", hover_color="#388e3c",
                     command=lambda pid=p[0]: self.mostrar_form_agendar(pid)).pack(side="left", padx=20, pady=10)
        
        ctk.CTkButton(btn_container, text="Volver", width=200, height=40,
                     fg_color="#407996", hover_color="#49829f",
                     command=self.mostrar_panel_usuario).pack(side="left", padx=20, pady=10)

    # -------------------------
    # CARRUSEL DE IMÁGENES
    # -------------------------
    def mostrar_carrusel_imagenes(self, image_files, start_idx):
        # Ventana modal para el carrusel
        carrusel = ctk.CTkToplevel(self)
        carrusel.title("Galería de imágenes")
        carrusel.geometry("900x650")
        carrusel.grab_set()  # Modal

        img_label = ctk.CTkLabel(carrusel, text="")
        img_label.pack(pady=20)

        idx = [start_idx]  # mutable para closures

        def mostrar_imagen():
            img_path = image_files[idx[0]]
            if os.path.exists(img_path):
                pil_img = Image.open(img_path)
                display_size = (800, 500)
                pil_img = pil_img.resize(display_size)
                img = CTkImage(light_image=pil_img, dark_image=pil_img, size=display_size)
                img_label.configure(image=img, width=800, height=500)
                img_label.image = img
                img_label.text = ""
            else:
                img_label.configure(text="Imagen no encontrada", image=None)

        def anterior():
            idx[0] = (idx[0] - 1) % len(image_files)
            mostrar_imagen()

        def siguiente():
            idx[0] = (idx[0] + 1) % len(image_files)
            mostrar_imagen()

        btn_frame = ctk.CTkFrame(carrusel, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Anterior", width=120, command=anterior).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Siguiente", width=120, command=siguiente).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Salir", width=120, fg_color="#e57373", hover_color="#c62828", command=carrusel.destroy).pack(side="left", padx=10)

        mostrar_imagen()

    # -------------------------
    # DETALLE SIMPLE (otra función del repo)
    # -------------------------
    def mostrar_detalle_proyecto(self, proyecto_id):
        p = obtener_proyecto(proyecto_id)
        if not p:
            messagebox.showerror("Error", "Proyecto no encontrado.")
            return
        win = ctk.CTkToplevel(self)
        win.title("Detalle del Proyecto")
        win.geometry("400x500")
        img_path = p[7] if p[7] and os.path.exists(p[7]) else os.path.join(Base_Dir, "static/placeholders/apt1.png")
        try:
            img = Image.open(img_path).resize((200, 150))
            img = ImageTk.PhotoImage(img)
        except:
            img = None
        if img:
            ctk.CTkLabel(win, image=img, text="").pack(pady=10)
            win.image = img
        ctk.CTkLabel(win, text=p[1], font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        ctk.CTkLabel(win, text=f"Ubicación: {p[2]}").pack()
        ctk.CTkLabel(win, text=f"Precio: ${p[3]:,.0f}").pack()
        ctk.CTkLabel(win, text=f"Tamaño: {p[4]} m²").pack()
        ctk.CTkLabel(win, text=f"Estado: {p[5]}").pack()
        ctk.CTkLabel(win, text=f"Descripción: {p[6]}", wraplength=350, justify="left").pack(pady=10)
        ctk.CTkButton(win, text="Agendar cita", width=150, command=lambda: self.mostrar_form_agendar(p[0])).pack(pady=10)
        ctk.CTkButton(win, text="Cerrar", width=100, command=win.destroy).pack(pady=5)

    # -------------------------
    # FORM AGENDAR, MIS CITAS, CONTACTO, SOPORTE, FAQ (mantengo tu lógica)
    # -------------------------
    def mostrar_form_agendar(self, proyecto_id=None):
        from datetime import date, timedelta
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Agendar Cita", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        if not proyecto_id:
            proyectos = listar_proyectos()
            opciones = {f"{p[1]} - {p[2]} (${p[3]:,.0f})": p[0] for p in proyectos}
            proyecto_var = ctk.StringVar(value=list(opciones.keys())[0] if opciones else "")
            proyecto_menu = ctk.CTkOptionMenu(frame, values=list(opciones.keys()), variable=proyecto_var)
            proyecto_menu.pack(pady=5)
        else:
            p = obtener_proyecto(proyecto_id)
            opciones = {f"{p[1]} - {p[2]} (${p[3]:,.0f})": p[0]}
            proyecto_var = ctk.StringVar(value=list(opciones.keys())[0])
            ctk.CTkLabel(frame, text=f"Proyecto: {p[1]} - {p[2]} (${p[3]:,.0f})").pack(pady=5)
        fechas_habiles = []
        hoy = date.today()
        d = hoy
        while len(fechas_habiles) < 30:
            if d.weekday() < 5:
                fechas_habiles.append(d.strftime('%Y-%m-%d'))
            d += timedelta(days=1)
        fecha_var = ctk.StringVar(value=fechas_habiles[0])
        ctk.CTkLabel(frame, text="Selecciona fecha:").pack(pady=2)
        fecha_menu = ctk.CTkOptionMenu(frame, values=fechas_habiles, variable=fecha_var)
        fecha_menu.pack(pady=2)
        horas = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0,30)]
        hora_var = ctk.StringVar(value=horas[0])
        ctk.CTkLabel(frame, text="Selecciona hora:").pack(pady=2)
        hora_menu = ctk.CTkOptionMenu(frame, values=horas, variable=hora_var)
        hora_menu.pack(pady=2)
        def actualizar_horas(*_):
            if not proyecto_var.get() or proyecto_var.get() not in opciones:
               
                hora_var.set("No disponible")
                return
            pid = opciones[proyecto_var.get()]
            horas_ocupadas = listar_citas_por_proyecto(pid, fecha_var.get())
            horas_disp = [h for h in horas if h not in horas_ocupadas]
            if not horas_disp:
                hora_menu.configure(values=["No disponible"])
                hora_var.set("No disponible")
            else:
                hora_menu.configure(values=horas_disp)
                hora_var.set(horas_disp[0])
        proyecto_var.trace_add('write', actualizar_horas)
        fecha_var.trace_add('write', actualizar_horas)
        actualizar_horas()
        def confirmar():
            pid = opciones[proyecto_var.get()]
            fecha = fecha_var.get()
            hora = hora_var.get()
            if hora == "No disponible":
                messagebox.showerror("Error", "No hay horas disponibles para esa fecha.")
                return
            usuario = obtener_usuario_por_email(self.usuario_actual)
            ok, msg = crear_cita(usuario[0], pid, fecha, hora)
            if ok:
                p = obtener_proyecto(pid)
                enviar_notificacion_cita(usuario[2], usuario[1], p[1], fecha, hora, tipo='creada')
                messagebox.showinfo("Éxito", "Cita agendada correctamente.")
                self.mostrar_panel_usuario()
            else:
                messagebox.showerror("Error", msg)
        ctk.CTkButton(frame, text="Confirmar cita", command=confirmar, width=200).pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=5)

    def mostrar_mis_citas(self):
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both")
        ctk.CTkLabel(frame, text="Mis Citas", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        usuario = obtener_usuario_por_email(self.usuario_actual)
        citas = listar_citas_por_usuario(usuario[0])
        if not citas:
            ctk.CTkLabel(frame, text="No tienes citas agendadas.").pack(pady=10)
        for c in citas:
            p = obtener_proyecto(c[2])
            info = f"Proyecto: {p[1]} - {p[2]}\nFecha: {c[3]}\nHora: {c[4]}\nEstado: {c[5]}"
            cita_frame = ctk.CTkFrame(frame, fg_color="#21244e", corner_radius=10)
            cita_frame.pack(pady=10, padx=10, fill="x")
            ctk.CTkLabel(cita_frame, text=info, anchor="w", justify="left", wraplength=650, font=ctk.CTkFont(size=15)).pack(padx=10, pady=10, anchor="w")
            if c[5] == "Agendada":
                def cancelar_cita_fn(cid=c[0], pid=c[2], fecha=c[3], hora=c[4]):
                    if messagebox.askyesno("Cancelar cita", "¿Seguro que deseas cancelar esta cita?"):
                        cancelar_cita(cid, usuario[0])
                        enviar_notificacion_cita(usuario[2], usuario[1], p[1], fecha, hora, tipo='cancelada')
                        messagebox.showinfo("Cita cancelada", "La cita ha sido cancelada.")
                        self.mostrar_mis_citas()
                ctk.CTkButton(cita_frame, text="Cancelar", command=cancelar_cita_fn, fg_color="#7a8894").pack(pady=5)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=10)

    def mostrar_contacto(self):
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Contáctanos", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        ctk.CTkLabel(frame, text="Escríbenos a contacto@urbannest.com o usa el formulario de soporte técnico.").pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=10)

    def mostrar_soporte_tecnico(self):
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Soporte Técnico", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        nombre_entry = ctk.CTkEntry(frame, placeholder_text="Nombre", width=250)
        nombre_entry.pack(pady=5)
        email_entry = ctk.CTkEntry(frame, placeholder_text="Correo", width=250)
        email_entry.pack(pady=5)
        asunto_entry = ctk.CTkEntry(frame, placeholder_text="Asunto", width=250)
        asunto_entry.pack(pady=5)
        mensaje_entry = ctk.CTkTextbox(frame, width=250, height=100)
        mensaje_entry.pack(pady=5)
        def enviar():
            nombre = nombre_entry.get()
            email = email_entry.get()
            asunto = asunto_entry.get()
            mensaje = mensaje_entry.get("1.0", "end").strip()
            if not nombre or not email or not asunto or not mensaje:
                messagebox.showerror("Error", "Completa todos los campos.")
                return
            messagebox.showinfo("Enviado", "Tu mensaje fue enviado correctamente.")
            self.mostrar_panel_usuario()
        ctk.CTkButton(frame, text="Enviar", command=enviar, width=200).pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=5)

    def mostrar_faq(self):
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Preguntas Frecuentes", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        faqs = [
            ("¿Cómo agendo una cita?", "Haz clic en 'Agendar cita' en la tarjeta del proyecto o en el menú lateral."),
            ("¿Puedo cancelar una cita?", "Sí, en la sección 'Mis Citas' puedes cancelar cualquier cita agendada."),
            ("¿Cómo contacto soporte?", "Usa la sección 'Soporte Técnico' en el menú lateral."),
            ("¿Puedo modificar mis datos?", "Por ahora no está disponible. Próximamente."),
        ]
        for pregunta, respuesta in faqs:
            ctk.CTkLabel(frame, text=pregunta, font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=20, pady=(10,0))
            ctk.CTkLabel(frame, text=respuesta, wraplength=700, justify="left").pack(anchor="w", padx=40, pady=(0,5))
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=10)


if __name__ == "__main__":
    init_db()
    app = App()
    app.mainloop()
