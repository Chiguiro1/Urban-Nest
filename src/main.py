from database.models import crear_tabla
from interfaces.gui import App
from tkinter import Tk

def main():
    # Inicializar la base de datos
    crear_tabla()
    
    # Crear y ejecutar la aplicación
    root = Tk()
    app = App(root)
    root.mainloop()

if __name__ == "__main__":
    main()
