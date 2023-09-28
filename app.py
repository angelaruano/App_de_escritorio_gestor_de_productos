from tkinter import ttk
from tkinter import *

import sqlite3
from models import Producto




if __name__ == "__main__":
    root = Tk() #Instancia de la ventana principal
    #A continuación voy a crear mi objeto para que los cambios gráficos de models, se apliquen
    app = Producto(root)
    root.mainloop() #Hace que nuestra instancia se mantenga "viva", es como un bucle while infinito

