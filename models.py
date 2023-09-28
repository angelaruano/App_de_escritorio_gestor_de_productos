import sqlite3
import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import *




#A continuación voy a crear mi clase central, aquella que vincularé con la interfaz gráfica.
class Producto:

    #Creo una variable global en la que defino la base de datos:
    db = "database/producto.db"

    #Creo el constructos de la clase:
    def __init__(self, root): #Con "root" vinculo la clase con la interfaz gráfica
        self.ventana = root #Con ésta variable "ventana" es como voy a personalizar mi ventana
        self.ventana.title("App gestor de productos")
        self.ventana.resizable(1,1) #Ésto permite redimensionalizar la ventana. Para desactivarlo es con(0,0)
        self.ventana.wm_iconbitmap("recursos/icon.ico.ico") #El icono que saldrá en mi ventana

        #Vamos a crear el primer Frame
        frame = LabelFrame(self.ventana, text = "Registrar un nuevo producto")
        #Invocamos la función frame.grid() donde vamos a darle forma:
        frame.grid(row = 0, column =0 , columnspan = 3, pady = 20)
        # "row" y "column" Le está diciendo dónde posicionar el Frame (usamos como referencia la esquina superior izquierda)
        # "columnspan" está indicando su tamaño, en éste caso 3 columnas
        # "pady" es para indicar márgenes, en éste caso 20 píxeles

        #Label de nombre
        self.etiqueta_nombre = Label(frame, text= "Nombre: ") #frame = Lugar donde quiero que esté
        self.etiqueta_nombre.grid (row= 1, column=0) #Posiciono dentro del frame

        #Entry nombre
        self.nombre = Entry(frame)
        self.nombre.focus() #Estoy indicando que quiero que tenga el foco.
        self.nombre.grid(row=1,column=1)

        # Label de precio
        self.etiqueta_precio = Label(frame, text="Precio: ")
        self.etiqueta_precio.grid(row=2, column=0)
        # Entry precio
        self.precio = Entry(frame)
        self.precio.grid(row=2, column=1)

        # Label de categoría
        self.lista_categoria = Label(frame, text="Categoría: ")
        self.lista_categoria.grid(row=3, column=0)
        # Entry categoría: Va a ser un Combobox con las categorías disponibles y la posibilidad de escribir una.
        self.categoria= ttk.Combobox(frame, values=["PC's","Móviles","Periféricos","Accesorios","Mobiliario"]) #En values introduzco la lista de categorías
        self.categoria.grid(row=3, column=1, pady= 5)

        # Label de stock: Va a ser un Checkbutton con valor booleano

        self.check_stock = tkinter.IntVar()
        self.stock = ttk.Checkbutton(frame, text='En stock', variable=self.check_stock, onvalue=1, offvalue=0)
        self.stock.grid(row=4, column=1, pady=5)

        #Botón de añadir producto:
        self.boton_aniadir = ttk.Button(frame, text="Añadir producto", command=self.add_producto) #Ésta función es la que se invoca cuando le doy al botón "guardar".En éste caso,a la invocación de la función, no se le ponen los paréntesis, porque ya command sobreentiende que una función
        self.boton_aniadir.grid(row=5, columnspan=2, sticky= W + E) #Con sticky y W(oeste),E(Este), Indico que quiero que me ocupe el ancho de las 2 columnas

        #Lo que viene a continuación es un label para interactuar con el usuario reflejando los mensajes de error que pondremos más abajo
        self.mensaje = Label(frame,text="", fg= "red") #Para que salga justo abajo del botón de añadir, hay que poner "frame". Si o, sale abajo del todo
        self.mensaje.grid (row= 6, column=0, columnspan=2, sticky= W + E)

        #Tabla productos
        style = ttk.Style()
        style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Calibri',11))  # Se modifica la fuente de la tabla
        style.configure("mystyle.Treeview.Heading", font=('Calibri', 13, 'bold')) # Se modifica la fuente de las cabeceras
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})]) # Eliminamos los bordes

        #Estructura de la tabla
        self.tabla = ttk.Treeview(frame, height=20, columns=["#0","#1","#2"],style="mystyle.Treeview")
        #height = altura de 20 filas
        #En colums me obliga a poner strings con los nombres de las columnas. Además, si pongo de la #o, hasta la #4
        #me crea 5 columnas, por lo que he puesto de la #0 a la #3 para que me cree 4 columnas.
        self.tabla.grid(row=7, column=0, columnspan=2)
        self.tabla.heading("#0", text= "Nombre", anchor=CENTER) #Le estoy poniendo cabecera a las columnas y estoy indicando que és esté centrada
        self.tabla.heading("#1", text="Precio", anchor=CENTER)
        self.tabla.heading("#2", text="Categoría", anchor=CENTER)
        self.tabla.heading("#3", text="Stock", anchor=CENTER)

        #Botones de eliminar y editar.
        #Primero les creo un estilo:
        s = ttk.Style()
        s.configure('my.TButton', font=('Calibri', 14, 'bold'))

        #Ahora creo los botones:
        boton_eliminar = ttk.Button(frame,text='ELIMINAR',  style='my.TButton', command= self.eliminar)
        boton_eliminar.grid(row=8, column=0, sticky=W + E)
        boton_editar = ttk.Button(frame,text='EDITAR',  style='my.TButton',command=self.editar)
        boton_editar.grid(row=8, column=1, sticky=W + E)

        self.get_productos() #Invoco al método

    #Ahora creamos una función para acceder a la base de datos.Le mandaré 2 parámetros:
    #"Consulta": Será la consulta principal (SELECT * FROM...)
    #"Parámetros: Por si la consulta es más compleja y quiero ponerle condiciones. Inicialmente lo definiremos como una tupla
    def db_consulta(self, consulta, parametros = ()):
        #Establezco conexión con la base de datos con un with (que me ahorra cerrar conexión)
        with sqlite3.connect(self.db) as con:
            cursor = con.cursor()  #Establezco cursor para interactuar con la base de datos
            resultado = cursor.execute(consulta,parametros) #El método execute está preparado para recibir 2 parámetros: un string y una tuplka
            con.commit() #Ejecuto la consulta
        return resultado

    #Vamos a crear la siguiente función que nos va a servir para usar la que acabamos de hacer.
    def get_productos(self):

        #Debido a que si introduco un nuevo registro, me dará un error porque va a la posición 0 donde ya hay datos
        #Lo ideal es que cada vez que invoque la función get_productos, se borren todos los registros
        registros_tabla = self.tabla.get_children() #Método para obtener los registros
        for fila in registros_tabla:
            self.tabla.delete(fila) #Borro la tabla

        query = "SELECT * FROM producto ORDER BY nombre DESC" #Creo mi consulta
        #Ejecuto la función anterior, enviándole la variable query:
        registros = self.db_consulta(query)
        #Itero sobre el resultado para que no me devuelva un objeto
        for fila in registros:
            print(fila)
            #Y ahora lo que quiero es que ésta iteración se me muestre en la ventana, dentro de la tabla que he creado, por lo que invoco dicha tabla:
            self.tabla.insert("",0, text= fila[1], values= (fila[2],fila[3],fila[4]))
            #Las comillas vacías indican que la tabla no hereda de otra, en text indico que salga el nombre (posición 1 en la tupla) y en values, el resto de posiciones

    #Debido a que pusimos en la base de datos que nombre y precio era NOT NULL, vamos a crear dos funciones para validar que se introducen por el usuario
    def validacion_nombre(self):
        nombre_introducido_por_usuario = self.nombre.get()
        return len(nombre_introducido_por_usuario) != 0

    def validacion_precio(self):
        precio_introducido_por_usuario = self.precio.get()
        return len(precio_introducido_por_usuario) != 0




    def add_producto(self): #Método para añadir productos
        #Hacemos condicionales para comprobar que nombre y precio no están vacíos, a través de las dos funciones anteriores
        if self.validacion_nombre() and self.validacion_precio():
            consulta = "INSERT INTO producto VALUES (NULL,?,?,?,?)" #NULL correspontde a la id autoincrement y los interrogantes van a ser los datos de mis columnas
            parametros = (self.nombre.get(), self.precio.get(),self.categoria.get(),self.check_stock.get())
            self.db_consulta(consulta, parametros)
            print("Datos guardados")
            #Creo el mensaje que debe salir en el caso de que el producto se guarde con éxito
            self.mensaje['text'] = 'Producto {} añadido con éxito'.format(self.nombre.get())
            #Las siguientes 3 líneas, sirven para que cuando pulse en "guardar", se borren los campos del formulario recién escritos
            self.nombre.delete(0,END)  # Borrar el campo nombre del formulario
            self.precio.delete(0, END) # Borrar el campo precio del formulario
            self.categoria.delete(0, END)  # Borrar el campo categoría del formulario
            #Para debug
            #print(self.nombre.get())
            #print(self.precio.get())
        elif self.validacion_nombre() and self.validacion_precio() == False:
            print("El precio es obligatorio")
            #A continuación, voy a invocar a self.mensaje para que el mismo mensaje que hay justo arriba, se refleje en la app
            #Haré lo mismo en los siguientes dos. Obsérvese que "text" se invoca como si accediera a la clave de un diccionario
            self.mensaje["text"] = "El precio es obligatorio"
        elif self.validacion_nombre() == False and self.validacion_precio():
            print("El nombre es obligatorio")
            self.mensaje["text"] = "El nombre es obligatorio"
        else:
            print("El nombre y el precio son obligatorios")
            self.mensaje["text"] = "El nombre y el precio es obligatorio"

        self.get_productos() #Invoco mi función para que se actualicen los registros

    #Creamos la función de eliminar:
    def eliminar(self):
        # Debug
        #print(self.tabla.item(self.tabla.selection()))
        #print(self.tabla.item(self.tabla.selection())['text'])
        #print(self.tabla.item(self.tabla.selection())['values'])
        #print(self.tabla.item(self.tabla.selection())['values'][0])

        #Lo que haremos será:
        # 1. Invovar a self.tabla.item, para indicar que queremos un registro concreto
        # 2. Entre paréntesis, vamos a decirle que el elemento que queremos es el que está seleccionado
        print(self.tabla.item(self.tabla.selection()))
        nombre = self.tabla.item(self.tabla.selection())["text"] #Busco el nombre del producto que quiero eliminar
        query = "DELETE FROM producto WHERE nombre = ?" #Creo una consulta donde la interrogación se va sustiruir por la variable nombre
        self.db_consulta(query,(nombre,))
        self.mensaje['text'] = 'Producto {} eliminado con éxito'.format(nombre)
        self.get_productos() #Me vuelve a actualizar la tabla

    def editar(self):
        #Hacemos un control de errores en el que, si no se selecciona el productos a editar, saldrá un mensaje
        try:
            self.tabla.item(self.tabla.selection())['text'][0]
        except IndexError as e:
            self.mensaje['text'] = 'Por favor, seleccione un producto'
            return
        #Introducimos en variables todas las características del producto
        nombre = self.tabla.item(self.tabla.selection())['text']
        precio = self.tabla.item(self.tabla.selection())['values'][0]
        categoria = self.tabla.item(self.tabla.selection())["values"][1]
        stock = self.tabla.item(self.tabla.selection())["values"][2]

        #Diseñando la ventana:
        self.ventana_editar = Toplevel()  # Toplevel() se usa para que la ventana salga por encima.
        self.ventana_editar.title = "Editar Producto" # Titulo de la ventana
        self.ventana_editar.resizable(1,1) #La ventana será redimensionable
        self.ventana_editar.wm_iconbitmap('recursos/icon.ico.ico') # Icono de la ventana

        #Creo el título de la ventana:
        titulo = Label(self.ventana_editar, text="Edición de productos", font=("Calibri",15,"bold"))
        titulo.grid(row=0,column=0)

        #Ahora creamos el contenedor Frame que va a ir en la ventana de edita:
        frame_editar = LabelFrame(self.ventana_editar, text="Editar el siguiente producto")
        frame_editar.grid(row=3, column=0,columnspan=20, pady=20)

        #Vamos con las etiquetas de los productos antiguos y nuevos

        #Label del nombre antiguo, que no va a poder modificarse
        self.etiqueta_nombre_original = Label(frame_editar, text="\nNombre del producto: \n")
        self.etiqueta_nombre_original.grid(row=5,column=0)
        #Entry del nombre original. Con readonly haremos que no pueda modificarse y con textvariable, nos traeremos la variable del principio, donde hemos guardado el nombre
        self.input_nombre_original = Entry(frame_editar,textvariable=StringVar(self.ventana_editar,value=nombre),state="readonly")
        self.input_nombre_original.grid(row=5,column=1)

        #Label del nuevo nombre:
        self.etiqueta_nombre_nuevo = Label(frame_editar, text="Nuevo nombre: ")
        self.etiqueta_nombre_nuevo.grid(row=6, column=0)
        #Entry del nuevo nombre:
        self.input_nombre_nuevo = Entry(frame_editar)
        self.input_nombre_nuevo.grid(row=6, column=1)
        self.input_nombre_nuevo.focus() #El control del ratón irá, al inicio, aquí.

        # Label del precio original, que no va a poder modificarse
        self.etiqueta_precio_original = Label(frame_editar, text="\nPrecio del producto: \n")
        self.etiqueta_precio_original.grid(row=8, column=0)
        # Entry del precio original. Con readonly haremos que no pueda modificarse y con textvariable, nos traeremos la variable del principio, donde hemos guardado el nombre
        self.input_precio_original = Entry(frame_editar, textvariable=StringVar(self.ventana_editar, value=precio),state="readonly")
        self.input_precio_original.grid(row=8, column=1)

        # Label del nuevo precio:
        self.etiqueta_precio_nuevo = Label(frame_editar, text="Nuevo precio: ")
        self.etiqueta_precio_nuevo.grid(row=9, column=0)
        # Entry del nuevo precio:
        self.input_precio_nuevo = Entry(frame_editar)
        self.input_precio_nuevo.grid(row=9, column=1)

        # Label de la categoria original, que no va a poder modificarse
        self.etiqueta_categoria_original = Label(frame_editar, text="\nCategoria del producto: \n")
        self.etiqueta_categoria_original.grid(row=11, column=0)
        # Entry del nombre original.
        self.input_categoria_original = Entry(frame_editar, textvariable=StringVar(self.ventana_editar, value=categoria), state="readonly")
        self.input_categoria_original.grid(row=11, column=1)

        # Label de la nueva categoria:
        self.etiqueta_categoria_nueva = Label(frame_editar, text="Nueva categoria: ")
        self.etiqueta_categoria_nueva.grid(row=12, column=0)
        # Entry de la nueva categoria:
        self.input_categoria_nueva = ttk.Combobox(frame_editar, values=["PC's","Móviles","Periféricos","Accesorios","Mobiliario"])
        self.input_categoria_nueva.grid(row=12, column=1)

        # Label del stock original, que no va a poder modificarse
        self.etiqueta_stock_original = Label(frame_editar, text="\nStock del producto: \n")

        self.etiqueta_stock_original.grid(row=14, column=0)
        # Entry del stock original.
        self.input_stock_original = Entry(frame_editar, textvariable=StringVar(self.ventana_editar, value=stock),state="readonly")
        self.input_stock_original.grid(row=14, column=1)

        # Label del nuevo stock:
        self.etiqueta_stock_nuevo = Label(frame_editar, text="Nuevo stock: \n 0 = Sin stock \n 1 = En stock ")
        self.etiqueta_stock_nuevo.grid(row=15, column=0)
        # Entry del nuevo stock:
        self.input_stock_nuevo = Entry(frame_editar)
        self.input_stock_nuevo.grid(row=15, column=1)

        # Boton Actualizar Producto
        self.boton_actualizar = ttk.Button(frame_editar, text="Actualizar Producto", command=lambda: #lambda es para que se ejecute lo que viene a continuación, en el momento de pulsar el botón
        self.actualizar_productos(self.input_nombre_nuevo.get(),
                                  self.input_nombre_original.get(),
                                  self.input_precio_nuevo.get(),
                                  self.input_precio_original.get(),
                                  self.input_categoria_nueva.get(),
                                  self.input_categoria_original.get(),
                                  self.input_stock_nuevo.get(),
                                  self.input_stock_original.get())) #Mandamos todos los parámetros a la función "actualizar productos"
        #Ubicamos el botón
        self.boton_actualizar.grid(row=16, columnspan=2, sticky=W + E)

    def actualizar_productos(self, nombre_nuevo, nombre_original, precio_nuevo, precio_original, categoria_nueva, categoria_original, stock_nuevo, stock_original):

        producto_modificado = False

        query = 'UPDATE producto SET nombre = ?, precio = ?, categoria = ?, stock = ? WHERE nombre = ? AND precio = ? AND categoria = ? AND stock = ?'

        #Dado que tengo 4 parámetros, en lugar de los dos que salen en el pdf, he decidido crear otra técnica para los condicionale, porque de la otra forma,sería muy resundante.
        #Lo que he hecho es crear una lista para que, accediendo a los índices, pueda modificarla con los condicionales
        #Luego, dicha lista, la transformo en una tupla y la guardo en la variable "parámetros"
        lista = [nombre_nuevo, precio_nuevo, categoria_nueva, stock_nuevo, nombre_original, precio_original,categoria_original, stock_original]
        if nombre_nuevo == "":
            lista[0] = nombre_original
        else:
            producto_modificado = True

        if precio_nuevo =="":
            lista[1] = precio_original
        else:
            producto_modificado = True

        if categoria_nueva == "":
            lista[2] = categoria_original
        else:
            producto_modificado = True

        if stock_nuevo == "":
            lista[3] = stock_original
        else:
            producto_modificado = True

        tupla = tuple(lista)
        parametros = tupla
        print(parametros)

        if(producto_modificado):
            self.db_consulta(query,(parametros))  # Ejecutar la consulta
            self.ventana_editar.destroy() # Cerrar la ventana de edicion de productos
            self.mensaje['text'] = 'El producto {} ha sido actualizado con éxito'.format(nombre_original) # Mostrar mensaje para el usuario
            self.get_productos() # Actualizar la tabla de productos
        else:
            self.ventana_editar.destroy() # Cerrar la ventana de edicion de productos
            self.mensaje['text'] = 'El producto {} NO ha sido actualizado'.format(nombre_original) # Mostrar mensaje para el usuario








