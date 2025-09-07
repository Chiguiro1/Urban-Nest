from database.models import init_db
from interfaces.gui import App
import customtkinter as ctk

def main():
    # Inicializar la base de datos
    init_db()
    #-------------------------------

    # Crear y ejecutar la aplicación
    app = App()
    app.mainloop()
    #-------------------------------

if __name__ == "__main__":
    main()
