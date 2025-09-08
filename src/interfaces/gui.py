# =======================
# IMPORTS Y CONFIGURACIÓN
# =======================
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from database.crud import (
    crear_usuario, verificar_usuario, verificar_usuario_contraseña, marcar_como_verificado, obtener_usuario_por_email,
    listar_proyectos, obtener_proyecto, crear_cita, listar_citas_por_usuario, cancelar_cita, listar_citas_por_proyecto
)
from database.models import init_db
from customtkinter import CTkImage

Base_Dir = os.path.dirname(__file__)
Path_Style = os.path.join(Base_Dir, "NightTrain.json")
Path_Logo = os.path.join(Base_Dir, "Logo.png")
ctk.set_appearance_mode("System")
ctk.set_default_color_theme(Path_Style)

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Urban Nest")
        self.geometry("1000x700")
        self.resizable(False, False)
        self.usuario_actual = None
        self.sidebar_visible = True
        self.logo_img = CTkImage(Image.open(Path_Logo).resize((60, 60)))
        self.mostrar_login()

    def limpiar_pantalla(self):
        for widget in self.winfo_children():
            widget.destroy()

    def mostrar_login(self):
        self.limpiar_pantalla()
        self.configure(bg_color="#e6ecf5")  # Fondo más claro
        frame = ctk.CTkFrame(self, width=420, height=420, fg_color="#407996")
        frame.pack(expand=True)
        frame.pack_propagate(False)
        # Elimino el logo
        ctk.CTkLabel(frame, text="").pack(pady=18)
        ctk.CTkLabel(frame, text="Iniciar Sesión", font=ctk.CTkFont(size=26, weight="bold"), text_color="#fff").pack(pady=16)
        email_entry = ctk.CTkEntry(frame, placeholder_text="Correo electrónico", width=280)
        email_entry.pack(pady=10)
        pass_entry = ctk.CTkEntry(frame, placeholder_text="Contraseña", show="*", width=280)
        pass_entry.pack(pady=10)
        def login_action():
            email = email_entry.get()
            contra = pass_entry.get()
            if not email or not contra:
                messagebox.showerror("Error", "Completa todos los campos.")
                return
            if not verificar_usuario(email):
                messagebox.showerror("Error", "Usuario no existe.")
                return
            if not verificar_usuario_contraseña(email, contra):
                messagebox.showerror("Error", "Contraseña incorrecta.")
                return
            user = obtener_usuario_por_email(email)
            if user[4] == 0:
                messagebox.showinfo("Verificación", "Verifica tu correo antes de ingresar.")
                return
            self.usuario_actual = email
            self.mostrar_panel_usuario()
        ctk.CTkButton(frame, text="Ingresar", command=login_action, width=240, fg_color="#21244e", hover_color="#1e214b").pack(pady=14)
        ctk.CTkButton(frame, text="Registrarse", command=self.mostrar_registro, width=240, fg_color="#ffb347", hover_color="#ff9800", text_color="#21244e").pack(pady=6)

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
                messagebox.showerror("Error", "Código incorrecto o expirado.")
        ctk.CTkButton(frame, text="Verificar", command=verificar_codigo, width=180, fg_color="#21244e", hover_color="#1e214b").pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_login, width=180, fg_color="#ffb347", hover_color="#ff9800", text_color="#21244e").pack(pady=4)

    def mostrar_registro(self):
        self.limpiar_pantalla()
        self.configure(bg_color="#e6ecf5")  # Fondo más claro
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
                messagebox.showinfo("Registro exitoso", "Usuario registrado. Revisa tu correo para el código de verificación.")
                self.mostrar_verificacion_email(email)
            else:
                messagebox.showerror("Error", "El correo ya está registrado.")
        ctk.CTkButton(frame, text="Registrar", command=registro_action, width=240, fg_color="#21244e", hover_color="#1e214b").pack(pady=14)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_login, width=240, fg_color="#ffb347", hover_color="#ff9800", text_color="#21244e").pack(pady=6)

    def mostrar_navbar(self):
        # Elimina cualquier navbar anterior
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

    def mostrar_proyectos_grid(self, parent=None):
        import customtkinter as ctk
        from PIL import Image
        import os
        # Badge de color según estado
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
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../images'))
        image_files = [os.path.join(images_dir, f'a{i+1}.jpeg') for i in range(6)]
        for idx, p in enumerate(proyectos):
            fila = idx // columnas
            col = idx % columnas
            card = ctk.CTkFrame(grid, width=400, height=220, fg_color="#21244e", corner_radius=16, border_width=2, border_color="#407996")
            card.grid(row=fila, column=col, padx=24, pady=24, sticky="nsew")
            # Título
            ctk.CTkLabel(card, text=p[1], font=ctk.CTkFont(size=18, weight="bold"), text_color="#00e6e6").pack(pady=(16, 2))
            # Ubicación
            ctk.CTkLabel(card, text=f"Ubicación: {p[2]}", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            # Precio
            ctk.CTkLabel(card, text=f"Precio: ${p[3]:,.0f}", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            # Tamaño
            ctk.CTkLabel(card, text=f"Tamaño: {p[4]} m²", font=ctk.CTkFont(size=14), text_color="#fff").pack()
            # Estado con badge
            estado = p[5] if p[5] != "Horrible" else "Deteriorada"
            color_estado = ESTADO_COLOR.get(estado, "#888")
            estado_frame = ctk.CTkFrame(card, fg_color=color_estado, corner_radius=8)
            estado_frame.pack(pady=4)
            ctk.CTkLabel(estado_frame, text=f"Estado: {estado}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#fff").pack(padx=8, pady=2)
            # Botón Detalles
            ctk.CTkButton(card, text="Detalles", width=300, fg_color="#407996", hover_color="#49829f", command=lambda idx=idx, pid=p[0]: self.mostrar_detalle_proyecto_custom(idx, pid)).pack(pady=2)

    def mostrar_detalle_proyecto_custom(self, idx, proyecto_id):
        import customtkinter as ctk
        from PIL import Image
        import os
        self.limpiar_pantalla()
        frame = ctk.CTkFrame(self, width=700, height=600, fg_color="#21244e")
        frame.pack(expand=True)
        frame.pack_propagate(False)
        proyectos = listar_proyectos()
        p = None
        for pr in proyectos:
            if pr[0] == proyecto_id:
                p = pr
                break
        if not p:
            messagebox.showerror("Error", "Proyecto no encontrado.")
            return
        images_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../images'))
        image_files = [os.path.join(images_dir, f'a{i+1}.jpeg') for i in range(6)]
        img_path = image_files[idx % len(image_files)] if os.path.exists(image_files[idx % len(image_files)]) else None
        img = None
        if img_path:
            try:
                img = Image.open(img_path).resize((500, 320))
                img = CTkImage(img)
            except:
                img = None
        if img:
            ctk.CTkLabel(frame, image=img, text="").pack(pady=(18, 10))
            frame.image = img
        ctk.CTkLabel(frame, text=p[1], font=ctk.CTkFont(size=22, weight="bold"), text_color="#00e6e6").pack(pady=(0, 6))
        ctk.CTkLabel(frame, text=f"Ubicación: {p[2]}", font=ctk.CTkFont(size=15), text_color="#fff").pack()
        ctk.CTkLabel(frame, text=f"Precio: ${p[3]:,.0f}", font=ctk.CTkFont(size=15), text_color="#fff").pack()
        ctk.CTkLabel(frame, text=f"Tamaño: {p[4]} m²", font=ctk.CTkFont(size=15), text_color="#fff").pack()
        estado = p[5] if p[5] != "Horrible" else "Deteriorada"
        ctk.CTkLabel(frame, text=f"Estado: {estado}", font=ctk.CTkFont(size=15, weight="bold"), text_color="#fff").pack(pady=(0, 8))
        # Descripciones personalizadas
        descripciones = [
            "Este apartamento en Laureles combina modernidad y comodidad en un entorno urbano privilegiado. Sus amplios espacios y acabados de alta calidad lo convierten en una excelente opción para familias o profesionales que buscan un lugar tranquilo y bien ubicado. La cercanía a parques, restaurantes y centros comerciales garantiza una vida social activa y todas las comodidades a la mano. Además, la seguridad y el ambiente residencial hacen de este apartamento una inversión segura y atractiva para quienes valoran el bienestar y la calidad de vida en la ciudad.",
            "Esta casa en El Poblado destaca por su amplitud y su hermoso jardín, ideal para quienes disfrutan de la naturaleza sin salir de la ciudad. La propiedad cuenta con espacios generosos, iluminación natural y una distribución funcional que permite el máximo aprovechamiento de cada ambiente. Su ubicación estratégica facilita el acceso a colegios, centros comerciales y vías principales, haciendo de esta casa una opción perfecta para familias que buscan confort, privacidad y un entorno seguro en una de las zonas más exclusivas de la ciudad.",
            "El loft en Envigado es la elección ideal para parejas jóvenes o profesionales que buscan un espacio moderno y funcional. Su diseño abierto y contemporáneo maximiza la luz y el espacio, creando un ambiente acogedor y versátil. Ubicado cerca de zonas comerciales y de entretenimiento, este loft ofrece la combinación perfecta entre tranquilidad y acceso a la vida urbana. Es una excelente oportunidad para quienes desean invertir en una propiedad con gran potencial de valorización y calidad de vida.",
            "El penthouse en el Centro ofrece una vista panorámica inigualable de la ciudad, ideal para quienes disfrutan de los paisajes urbanos. Sus amplios ventanales y terrazas permiten disfrutar de atardeceres únicos y un ambiente luminoso durante todo el día. Aunque requiere algunas mejoras, su ubicación privilegiada y el potencial de personalización lo convierten en una excelente opción para quienes buscan un hogar exclusivo y con carácter propio en el corazón de la ciudad.",
            "Este apartamento en Belén se caracteriza por su proximidad a parques y zonas verdes, lo que lo hace perfecto para familias y amantes de la naturaleza. Sus espacios bien distribuidos y su ambiente tranquilo ofrecen el equilibrio ideal entre vida urbana y contacto con el entorno natural. La zona cuenta con excelentes servicios, transporte público y opciones de recreación, haciendo de este apartamento una alternativa atractiva para quienes buscan calidad de vida y comodidad.",
            "La casa en Robledo es una opción familiar que destaca por su amplitud y su potencial de renovación. Aunque presenta signos de deterioro, ofrece una base sólida para quienes desean remodelar y personalizar su hogar. Su ubicación en un sector tradicional brinda acceso a colegios, comercios y transporte, convirtiéndola en una oportunidad interesante para quienes buscan invertir en una propiedad con posibilidades de crecimiento y valorización a futuro."
        ]
        ctk.CTkLabel(frame, text=descripciones[idx], font=ctk.CTkFont(size=14), text_color="#fff", wraplength=650, justify="left").pack(pady=(10, 18))
        ctk.CTkButton(frame, text="Agendar cita", width=300, fg_color="#4caf50", hover_color="#388e3c", command=lambda pid=p[0]: self.mostrar_form_agendar(pid)).pack(pady=8)
        ctk.CTkButton(frame, text="Volver", width=300, fg_color="#407996", command=self.mostrar_panel_usuario).pack(pady=4)

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

    def mostrar_form_agendar(self, proyecto_id=None):
        from datetime import date, timedelta
        from database.crud import listar_citas_por_proyecto, crear_cita, obtener_proyecto, obtener_usuario_por_email
        from auth.email_utils import enviar_notificacion_cita
        import datetime
        self.limpiar_pantalla()
        self.mostrar_navbar()
        frame = ctk.CTkFrame(self)
        frame.pack(expand=True)
        ctk.CTkLabel(frame, text="Agendar Cita", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=10)
        # Proyecto
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
        # Fecha
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
        # Hora
        horas = [f"{h:02d}:{m:02d}" for h in range(9, 17) for m in (0,30)]
        hora_var = ctk.StringVar(value=horas[0])
        ctk.CTkLabel(frame, text="Selecciona hora:").pack(pady=2)
        hora_menu = ctk.CTkOptionMenu(frame, values=horas, variable=hora_var)
        hora_menu.pack(pady=2)
        # Al cambiar fecha/proyecto, actualizar horas disponibles
        def actualizar_horas(*_):
            if not proyecto_var.get() or proyecto_var.get() not in opciones:
                hora_menu.configure(values=["No disponible"])
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
        # Confirmar
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
                # Notificación email y log
                p = obtener_proyecto(pid)
                enviar_notificacion_cita(usuario[2], usuario[1], p[1], fecha, hora, tipo='creada')
                logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
                if not os.path.exists(logs_dir):
                    os.makedirs(logs_dir)
                with open(os.path.join(logs_dir, 'citas.log'), 'a') as f:
                    f.write(f"[{datetime.datetime.now().isoformat()}] {usuario[2]} agendó cita: Proyecto {p[1]}, Fecha {fecha}, Hora {hora}\n")
                messagebox.showinfo("Éxito", "Cita agendada correctamente.")
                self.mostrar_panel_usuario()
            else:
                messagebox.showerror("Error", msg)
        ctk.CTkButton(frame, text="Confirmar cita", command=confirmar, width=200).pack(pady=10)
        ctk.CTkButton(frame, text="Volver", command=self.mostrar_panel_usuario, width=200, fg_color="#407996").pack(pady=5)

    def mostrar_mis_citas(self):
        from database.crud import listar_citas_por_usuario, obtener_proyecto, cancelar_cita, obtener_usuario_por_email
        from auth.email_utils import enviar_notificacion_cita
        import datetime
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
                        logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
                        if not os.path.exists(logs_dir):
                            os.makedirs(logs_dir)
                        with open(os.path.join(logs_dir, 'citas.log'), 'a') as f:
                            f.write(f"[{datetime.datetime.now().isoformat()}] {usuario[2]} canceló cita: Proyecto {p[1]}, Fecha {fecha}, Hora {hora}\n")
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
        from auth.email_utils import enviar_soporte_tecnico
        import datetime
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
            ok = enviar_soporte_tecnico(nombre, email, asunto, mensaje)
            # Log local
            logs_dir = os.path.join(os.path.dirname(__file__), '../../logs')
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            with open(os.path.join(logs_dir, 'soporte.log'), 'a') as f:
                f.write(f"[{datetime.datetime.now().isoformat()}] {email} - {asunto}\n{mensaje}\n\n")
            if ok:
                messagebox.showinfo("Enviado", "Tu mensaje fue enviado correctamente.")
                self.mostrar_panel_usuario()
            else:
                messagebox.showerror("Error", "No se pudo enviar el mensaje. Intenta más tarde.")
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

