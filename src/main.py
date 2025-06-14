from database.models import crear_tabla
from interfaces.gui import App
import customtkinter as ctk

def main():
    # Inicializar la base de datos
    crear_tabla()
    #-------------------------------

    # Crear y ejecutar la aplicación
    app = App()
    app.mainloop()
    #-------------------------------

if __name__ == "__main__":
    main()