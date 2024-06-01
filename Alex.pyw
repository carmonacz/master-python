import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import hashlib
import hmac
from hexadecimalAsciiBinario import calcular_bloques
from calcularW import procesar_bloque
from calcularK import obtener_K_32_bits, numerosPrimosCubico
from calcularH import obtener_H_32_bits, numerosPrimosCuadrado
from calcularSha256 import *
import requests
import pyodbc


contador = '000'
cambios = [contador]
dato1 = 0
dato2 = 0


def obtener_direccion_ip_externa():
    try:
        # Usar un servicio que devuelve la dirección IP externa
        response = requests.get('https://api.ipify.org')
        if response.status_code == 200:
            return response.text
        else:
            return "No se pudo obtener la dirección IP externa"
    except Exception as e:
        return "Error al obtener la dirección IP externa: " + str(e)

ip_externa = obtener_direccion_ip_externa()


# establecer conexión a la base de datos
def establecer_conexion():
    # Definición de las variables de conexión
    server_name = 'localhost\\PRUEBAS'  # Si la instancia es nombrada, usa SERVER\\INSTANCIA
    database_name = 'freebitcoin'

    # String de conexión usando autenticación de Windows
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server_name};"
        f"DATABASE={database_name};"
        f"Trusted_Connection=yes;"
    )

    try:
        cnx = pyodbc.connect(connection_string)
        return cnx
    except pyodbc.Error as err:        
        return messagebox.showerror("ERROR", f"Error al conectar a la base de datos: {err}")
    
def obtener_datos_BD():
    cnx = establecer_conexion()
    cursor = cnx.cursor()

     # Ejecutar consulta SQL
    cursor.execute(f"SELECT * FROM freebitcoin")  # Solo selecciona las columnas deseadas
    registros = cursor.fetchall()

    return registros[0]

def inicio():
    # Para cargar los valores de las cajas
    ne = 0

    datos = obtener_datos_BD()
    roll.set('0000')

    btnComprobar.configure(state='disabled')

    cajaSeed.insert(
        0, f'  Número Secreto:    {ip_externa}  ')
    cajaSeed.configure(state='disable')

    cajaGanadas.insert(0, '0')
    cajaJugadas.insert(0, '0')
    cajaFiltro.insert(0, '100')
    cajaPerdidasSeguidas.insert(0, '0')
    cajaGanadasSeguidas.insert(0, '0')

    cajaPorcentaje.delete(0, 'end')
    cajaPorcentaje.insert(0, '0.0%')

    cajaDeApuesta.delete(0, 'end')
    cajaDeApuesta.insert(0, 'HI')

    cajaNE.delete(0, 'end')
    cajaNE.insert(0, round(ne, 2))

    cajaHash.insert(0, datos[2])
    cajaClient.insert(0, 'zdwPOS2yp0MwPJ9z')
    cajaNonce.insert(0, datos[3])

    establecer_conexion()

       

class EntryEx(tk.Entry):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = tk.Menu(self, tearoff=False)
        self.menu.add_command(label="Copiar", command=self.popup_copy)
        self.menu.add_command(label="Cortar", command=self.popup_cut)
        self.menu.add_separator()
        self.menu.add_command(label="Pegar", command=self.popup_paste)
        self.bind("<Button-3>", self.display_popup)

        # Configurar validación para limitar a 64 caracteres
        validate_func = (self.register(self.validar_longitud), '%P', '%V')
        self.configure(validate="key", validatecommand=validate_func)

    def display_popup(self, event):
        self.menu.post(event.x_root, event.y_root)

    def popup_copy(self):
        # Obtiene el texto seleccionado en el widget
        texto_seleccionado = self.selection_get()

        if texto_seleccionado:
            # Elimina los espacios al principio y al final del texto seleccionado
            texto_seleccionado = texto_seleccionado.strip()

            # Copia el texto procesado al portapapeles
            self.clipboard_clear()
            self.clipboard_append(texto_seleccionado)

    def popup_cut(self):
        # Obtiene el texto seleccionado en el widget
        texto_seleccionado = self.selection_get()

        if texto_seleccionado:
            # Elimina los espacios al principio y al final del texto seleccionado
            texto_seleccionado = texto_seleccionado.strip()

            # Copia el texto procesado al portapapeles
            self.clipboard_clear()
            self.clipboard_append(texto_seleccionado)

            # Borra el texto seleccionado del widget
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)

    def popup_paste(self):
        # Pega el texto desde el portapapeles
        texto_pegado = self.clipboard_get()

        # Elimina los espacios al principio y al final del texto pegado
        texto_pegado = texto_pegado.strip()

        # Obtiene el rango de la selección actual (si existe)
        seleccion = self.selection_present()

        # Borra el texto seleccionado en el widget si existe
        if seleccion:
            self.delete(tk.SEL_FIRST, tk.SEL_LAST)

        # Inserta el texto procesado en el widget en la posición actual del cursor
        self.insert(tk.INSERT, texto_pegado)

    def validar_longitud(self, valor, acción):
        return len(valor) <= 64 and acción != '1'
    
class TablaApp:
    def __init__(self, root, tabla, columnas):
        self.root = root
        self.tabla = tabla

        # Configurar estilos antes de crear el Treeview
        style = ttk.Style()
        style.configure("Custom.Treeview")
        style.configure("Custom.Treeview.Rojo", background="red", foreground="white")
        style.configure("Custom.Treeview.Verde", background="green", foreground="white")

        # Crear un Treeview para mostrar la tabla
        self.tree = ttk.Treeview(root, show="headings", style="Custom.Treeview")
        self.tree["columns"] = tuple(columnas)

        for columna in columnas:
            # Utilizar una etiqueta de estilo diferente para las cabeceras
            self.tree.heading(columna, text=columna, anchor="center")
            self.tree.column(columna, anchor="center", width=100)

        self.tree.pack(expand=True, fill="both")

        # Llenar la tabla con datos desde la base de datos
        self.mostrar_tabla(tabla)

    def llenar_tabla(self, registros):
        # Limpiar la tabla antes de volver a llenarla
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Llenar la tabla con los registros de la base de datos
        for registro in registros:
            # Obtener el valor de la columna "resultado"
            resultado = registro[-1]

            # Verificar si el resultado es 'LOSSER' y cambiar el fondo de la fila a 'rojo' en ese caso
            tags = ("Custom.Treeview.Rojo",) if resultado == 'LOSSER' else ("Custom.Treeview.Verde",)
            
            # Formatear la fecha
            registro = list(registro)
            registro[0] = registro[0].strftime('%Y-%m-%d %H:%M:%S')
            
            self.tree.insert("", "end", values=registro, tags=tags)

    def mostrar_tabla(self, tabla):
        # Conectar a la base de datos
        cnx = establecer_conexion()
        cursor = cnx.cursor()

        # Ejecutar consulta SQL
        cursor.execute(f"SELECT TOP 20 time, bet, roll, rollserver, resultado FROM {tabla} ORDER BY id DESC;")
        registros = cursor.fetchall()

        # Llenar la tabla y aplicar estilos
        self.llenar_tabla(registros)

        # Asociar el estilo a las filas con resultado 'LOSSER' y a las demás
        self.tree.tag_configure("Custom.Treeview.Rojo", background="red", foreground="white")
        self.tree.tag_configure("Custom.Treeview.Verde", background="green", foreground="white")

        # Cerrar la conexión a la base de datos
        cnx.close()

    def actualizar_tabla(self):
        # Conectar a la base de datos
        cnx = establecer_conexion()
        cursor = cnx.cursor()

        # Ejecutar consulta SQL
        cursor.execute(f"SELECT TOP 20 time, bet, roll, rollserver, resultado FROM {self.tabla} ORDER BY id DESC;")  # Usar self.tabla para referenciar la tabla
        registros = cursor.fetchall()

        # Llenar la tabla y aplicar estilos
        self.llenar_tabla(registros)

        # Asociar el estilo a las filas con resultado 'LOSSER' y a las demás
        self.tree.tag_configure("Custom.Treeview.Rojo", background="red", foreground="white")
        self.tree.tag_configure("Custom.Treeview.Verde", background="green", foreground="white")

        # Cerrar la conexión a la base de datos
        cnx.close()


def sumar_uno():
    nonce = cajaNonce.get()
    r = int(nonce, 10) + 1
    cajaNonce.delete(0, 'end')
    cajaNonce.insert(0, r)


def analizar():
    n2 = cajaHash.get()
    n4 = cajaNonce.get()

    longitud = len(n2)

    if longitud == 64:

        cambios.insert(0, n4)

        if n4 != cambios[1]:            
            btnHash.configure(bg="green", text=longitud)

            new_hash = has256(n2)
            cajaSeed.configure(state='normal')
            cajaSeed.delete(0, 'end')
            cajaSeed.insert(0, new_hash)
            n3 = cajaClient.get()

            n1 = new_hash
            h = n4 + ":"+str(n1)+":"+n4
            key = n4+":"+n3+":"+n4
            b = int(float('429496.7295'))
            signature = hmac.new(key.encode(), h.encode(),
                                 digestmod=hashlib.sha512).hexdigest()
            resultado = int(signature[0:8], 16)
            ara = resultado/b
            div = round(ara)
            roll.set(div)

            if int(div) > 4999:
                cajaDeApuesta.delete(0, 'end')
                cajaDeApuesta.insert(0, 'HI')
                label_arrow.configure(text='\u2190')

            else:
                cajaDeApuesta.delete(0, 'end')
                cajaDeApuesta.insert(0, 'LO')
                label_arrow.configure(text='\u2192')
              

            
            btnAnalizar.configure(state='disabled')
            cajaNonce.configure(state='disabled')
            cajaHash.configure(state='disable')
            lbl7.configure(text='..GUARDAR..')
            guardar()
        else:
            messagebox.showerror("ERROR", "Tienes que modificar NONCE")

    else:
        messagebox.showerror("ERROR", "EL DATO INTRODUCIDO NO TIENE 64bits")
        btnHash.configure(bg="red")



def guardar():
    cnx = establecer_conexion()
    cursor = cnx.cursor()

    server = cajaHash.get()
    hash_val = cajaSeed.get()

    longitud = len(hash_val)

    btnSeed = tk.Button(ventana, text=longitud, command=borrar_texto, fg="white")
    btnSeed.place(x=505, y=10, width=30, height=25)       

    if longitud == 64:
        btnSeed.configure(bg="green")

        # insertar los valores en la tabla
        query = """
            INSERT INTO hashes (cadenaHash)
            SELECT ? AS cadenaHash
            WHERE NOT EXISTS (
                SELECT 1
                FROM hashes
                WHERE cadenaHash = ?
            )
        """
         # Convertir valores a tuplas adecuadas para la inserción
        values = [(server, server), (hash_val, hash_val)]
        
        # Ejecutar cada inserción individualmente
        for value in values:
            cursor.execute(query, value)
        cnx.commit()

        messagebox.showinfo(
            "GUARDAR", "LOS DATOS HAN SIDO GUARDADOS CORRECTAMENTE")
                 
        btnComprobar.configure(state='normal')
        lbl7.configure(text='COMPROBAR..')

    else:
        btnSeed.configure(bg="red")
        messagebox.showerror("ERROR", "EL DATO INTRODUCIDO NO TIENE 64bits")

def borrar_texto():
    datos = obtener_datos_BD()  
    cajaSeed.delete(0, 'end')
    cajaSeed.insert(0, datos[1])
    guardar()

def actualizar_inicio():
    datos = obtener_datos_BD()
    cajaHash.delete(0, 'end')
    cajaHash.insert(0, datos[2])
    cajaNonce.delete(0, 'end')
    cajaNonce.insert(0, datos[3])

def comprobar():
    try: 
        dato1 = roll.get()
        hash_caja = hashlib.sha256(cajaSeed.get().encode('utf-8')).hexdigest()
        # Verificar que el Hash de cajaHash es el resultado buscado    
        if hash_caja == cajaHash.get(): 
            h = cajaNonce.get() + ":" + str(cajaSeed.get()) + ":" + cajaNonce.get()
            key = cajaNonce.get() + ":" + cajaClient.get() + ":" + cajaNonce.get()
            b = int(float('429496.7295'))
            signature = hmac.new(key.encode(), h.encode(), digestmod=hashlib.sha512).hexdigest()
            resultado = int(signature[0:8], 16)
            ara = resultado / b
            div = round(ara)

            btnComprobar.configure(state='disabled')
            lbl7.config(text='*CONTINUAR*')
            roll.set(div)

            añadir(dato1)

            return

        # Obtener todos los datos de la tabla en el caso de cajaHash no contenga el resultado buscado
        cnx = establecer_conexion()
        cursor = cnx.cursor()
        query = "SELECT cadenaHash FROM hashes;"
        cursor.execute(query)
        datos = cursor.fetchall()   

        
        for d in datos:            
            h = d[0]
            hash_calc = hashlib.sha256(h.encode('utf-8')).hexdigest()

            if hash_calc == cajaHash.get():
                # Realizar las operaciones necesarias si hay coincidencia
                cajaSeed.delete(0, 'end')
                cajaSeed.insert(0, h[:64])
                
                h = cajaNonce.get() + ":" + str(cajaSeed.get()) + ":" + cajaNonce.get()
                key = cajaNonce.get() + ":" + cajaClient.get() + ":" + cajaNonce.get()
                b = int(float('429496.7295'))
                signature = hmac.new(key.encode(), h.encode(), digestmod=hashlib.sha512).hexdigest()
                resultado = int(signature[0:8], 16)
                ara = resultado / b
                div = round(ara)

                btnComprobar.configure(state='disabled')
                lbl7.config(text='*CONTINUAR*')
                roll.set(div)
                añadir(dato1)

                return

    except pyodbc.Error as pymysql_error:
        messagebox.showerror("ERROR", f"Error de MySQL: {pymysql_error}")
        cajaSeed.insert(0, "Error")

    btnComprobar.configure(state='disabled')
    lbl7.config(text='*JUEGA*')
    messagebox.showerror(
        "ERROR", "¡NO HAS ENCONTRADO EL RESULTADO SIGUE INTENTADOLO!")

def añadir(dato):
    cnx = establecer_conexion()
    cursor = cnx.cursor()
    datos = obtener_datos_BD()

    dato2 = roll.get()
    ne = cajaNE.get()
    ganadas = cajaGanadas.get()
    filtro = cajaFiltro.get()
    jugadas = cajaJugadas.get()
    Verde = 0
    Rojo = cajaPerdidasSeguidas.get()
    Azul = cajaGanadasSeguidas.get()
    mensaje = 'WINNER'

    jugadas = int(jugadas) + 1
    valor = cajaDeApuesta.get()

    if (((int(dato2) > 5250) & (valor == 'HI')) | ((int(dato2) < 4750) & (valor == 'LO')) ):
        ganadas = int(ganadas) + 1
        filtro = int(filtro) + 1
        Azul = int(Azul) + 1
        Verde = 1

       
        mensaje = 'WINNER'

    else:
        filtro = int(filtro) - 1
        Rojo = int(Rojo) + 1
        mensaje = 'LOSSER'
        
        if ((int(dato2) < 5251) & (int(dato2) > 4749)):
            mensaje = 'LOSSER'
            ne = int(ne)+1
            
    if Verde == 1:
        Rojo = 0

    else:
        Azul = 0

    cajaGanadas.delete(0, 'end')
    cajaGanadas.insert(0, ganadas)

    cajaFiltro.delete(0, 'end')
    cajaFiltro.insert(0, filtro)

    cajaPerdidasSeguidas.delete(0, 'end')
    cajaPerdidasSeguidas.insert(0, Rojo)
    cajaGanadasSeguidas.delete(0, 'end')
    cajaGanadasSeguidas.insert(0, Azul)

    ganadas = (round((int(ganadas) / jugadas)*1000))/10

    cajaJugadas.delete(0, 'end')
    cajaJugadas.insert(0, jugadas)

    cajaPorcentaje.delete(0, 'end')
    cajaPorcentaje.insert(0, str(ganadas)+"%")

    cajaNE.delete(0, 'end')
    cajaNE.insert(0, ne)

    # Añadir datos a la tabla historico
    query = "INSERT INTO historico(bet, roll, rollserver, resultado) VALUES(?,?,?,?)"
    values = [(valor, dato, dato2, mensaje)]
    cursor.executemany(query, values)
    cnx.commit()

    app.actualizar_tabla()

    messagebox.showwarning("SUCCESSFUL", "¡HAS ENCONTRADO EL RESULTADO!")

    btnAnalizar.configure(state='normal')
    cajaNonce.configure(state='normal')
    cajaNonce.delete(0, 'end')
    cajaNonce.insert(0, datos[3])
    cajaSeed.configure(state='disable')
    cajaHash.configure(state='normal')
    cajaHash.delete(0, 'end')
    cajaHash.insert(0, datos[2])

def has256(variable):
   # Calcular los primeros 32 bits de las partes fraccionarias de las raíces cúbicas de los primeros números primos
    k = [obtener_K_32_bits(primo) for primo in numerosPrimosCubico]

    primerbloque, segundobloque = calcular_bloques(variable)
    
    valor = procesar_bloque(primerbloque)
    extra = procesar_bloque(segundobloque)

    resultadoH = [obtener_H_32_bits(primo) for primo in numerosPrimosCuadrado]
    #cadena = resultadoH[-8:] #se cogen los ultimos 8 valores del array segun el indice.
    #valores_inversos = resultadoH[::-1][:8] #de esta forma obtendré los valores desde el 7 al 0 ambos inclusive invirtiendo el orden de la lista
    #cadena = [calcular_Inversa(resultadoH[i -1]) for i in range(1,9)] para calcular la inversa de la cadena
    valorInicial = resultadoH
    # Valor máximo del rango 1, 65
    for i in range(1, 63):
        #Modificar extra, valor
        resultadoH = sha256_cadena(resultadoH, k[i-1], valor[i-1])   

    valorIntermedio = [calcular_suma(valorInicial[i - 1], resultadoH[i - 1]) for i in range(1, 9)]
    valorInicial = valorIntermedio

    for i in range(2):
        #Modificar extra, valor
        valorIntermedio = sha256_cadena(valorIntermedio, k[i-1], extra[i-1])

    valorFinal = [calcular_suma(valorInicial[i - 1], valorIntermedio[i - 1]) for i in range(1,9)]

    resultado = sha256_final(valorFinal)
    
    # Mantener valor y extra; 
    # Mantener resultadoH (cadena_inversa; cadena_S0; cadena_S1); 
    # Modificar el rango segundo a 3 
    # Modificar el rango primero a 3

    return (resultado)


# Diseño de la aplicación
ventana = tk.Tk()
roll = tk.StringVar()
colorFondo = "#007a5c"
colorLetra = "#FFF"
ventana.title("MINERO DE BTC FREEBITCOIN: FreeBTC")
ventana.geometry("560x560")
ventana.configure(background=colorFondo)
# Esta es la línea es para que se quede fija la ventana+
ventana.wm_attributes("-topmost", True)
# Esta linea es para que no se modifique el tamaño de la ventana
ventana.resizable(width=False, height=False)

# Etiquetas

lbl1 = tk.Label(ventana, text='SERVER SEED:', font=("Courier", 12, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lbl1.place(x=50, y=10, width=450, height=30)

lbl2 = tk.Label(ventana, text='SERVER SEED HASH:', font=("Courier", 12, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lbl2.place(x=50, y=80, width=450, height=30)

lbl3 = tk.Label(ventana, text='CLIENT SEED:', font=("Courier", 12, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lbl3.place(x=40, y=160, width=200, height=30)

lbl4 = tk.Label(ventana, text='NONCE:  ', font=("Courier", 12, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lbl4.place(x=300, y=160, width=200, height=30)

lbl6 = tk.Label(ventana, text='Ganadas', font=("Courier", 10, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lbl6.place(x=20, y=240, width=60, height=30)

lblp = tk.Label(ventana, text='Jugadas', font=("Courier", 9, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lblp.place(x=85, y=240, width=60, height=30)

lblf = tk.Label(ventana, text='Filtro', font=("Courier", 10, "bold"),
             bg="#142f4d", fg="#ffffff", relief="ridge")
lblf.place(x=150, y=240, width=60, height=30)


lbl7 = tk.Label(ventana, text='..ANALIZAR..', font=("Courier", 25, "bold"),
             bg="#007a5c", fg="#ffffff", bd=0, relief="ridge")
lbl7.place(x=20, y=310, width=240, height=40)


lbl10 = tk.Label(ventana, text='NE', font=("Courier", 25, "bold"),
              bg="#142f4d", fg="#ffffff", relief="ridge")
lbl10.place(x=340, y=360, width=60, height=50)

label_arrow = tk.Label(ventana, text='\u2190', font=("Arial", 26, "bold"), fg="yellow", compound="center",
              bg="#007a5c", bd=0, relief="ridge")
label_arrow.place(x=250, y=160, width=40, height=40)

# Cajas de texto
cajaSeed = EntryEx(ventana)
cajaSeed.configure(font=("Courier", 10),  bg="#004530",
                   fg="#feba00", insertbackground="#ffffff")
cajaSeed.place(x=20, y=40, width=525, height=30)

cajaHash = EntryEx(ventana)
cajaHash.configure(font=("Courier", 10),  bg="#004530",
                     fg="#feba00", insertbackground="#ffffff")
cajaHash.place(x=20, y=110, width=525, height=30)
cajaHash.focus()

cajaClient = EntryEx(ventana)
cajaClient.configure(font=("Courier", 12),  bg="#004530",
                     fg="#feba00", insertbackground="#ffffff")
cajaClient.place(x=40, y=190, width=200, height=30)

cajaNonce = EntryEx(ventana)
cajaNonce.configure(font=("Courier", 12),  bg="#004530",
                    fg="#feba00", insertbackground="#ffffff")
cajaNonce.place(x=300, y=190, width=200, height=30)

cajaGanadas = tk.Entry(ventana, font=("Courier", 12),  bg="#004530",
              fg="#feba00", justify="center", insertbackground="#ffffff")
cajaGanadas.place(x=20, y=270, width=60, height=30)

cajaJugadas = tk.Entry(ventana, font=("Courier", 12),  bg="#004530",
              fg="#feba00", justify="center", insertbackground="#ffffff")
cajaJugadas.place(x=85, y=270, width=60, height=30)

cajaFiltro = tk.Entry(ventana, font=("Courier", 12),  bg="#004530",
              fg="#feba00", justify="center", insertbackground="#ffffff")
cajaFiltro.place(x=150, y=270, width=60, height=30)

cajaPerdidasSeguidas = tk.Entry(ventana, font=("Courier", 25, "bold"),  bg="red",
              fg="#ffffff", justify="center", insertbackground="#ffffff")
cajaPerdidasSeguidas.place(x=250, y=360, width=50, height=50)

cajaGanadasSeguidas = tk.Entry(ventana, font=("Courier", 25, "bold"),  bg="blue",
              fg="#ffffff", justify="center", insertbackground="#ffffff")
cajaGanadasSeguidas.place(x=190, y=360, width=50, height=50)

cajaNE = tk.Entry(ventana, font=("Courier", 25, "bold"), bg="grey", fg="#ffffff",
               justify="center", insertbackground="#ffffff")
cajaNE.place(x=400, y=360, width=90, height=50)

cajaT = tk.Entry(ventana, textvariable=roll, font=("Courier", 60, "bold"),
              bg="#000000", fg="#ffffff", justify="right", insertbackground="#ffffff").place(x=310, y=290,
                                                                                             width=200, height=65)

cajaPorcentaje = tk.Entry(ventana, font=("Courier", 25, "bold"), bg="#AD45ED", fg="#ffffff",
               justify="center", insertbackground="#ffffff")
cajaPorcentaje.place(x=30, y=360, width=120, height=50)

cajaDeApuesta = tk.Entry(ventana, font=("Courier", 25, "bold"), bg="orange", fg="#ffffff",
               justify="center", insertbackground="#ffffff")
cajaDeApuesta.place(x=220, y=240, width=60, height=60)


# botones
btnAnalizar = tk.Button(ventana, text='ANALIZAR!', command=analizar, fg="red", bg="yellow")
btnAnalizar.place(x=320, y=240, width=80, height=40)


btnComprobar = tk.Button(ventana, text='COMPROBAR!', command=comprobar, fg="red", bg="yellow")
btnComprobar.place(x=420, y=240, width=80, height=40)

btn5 = tk.Button(ventana, text="\u25b2", command=sumar_uno,
              fg="white", bg="blue", justify="center")
btn5.place(x=470, y=160, width=30, height=30)

btnHash = tk.Button(ventana, text="\u21bb", command=actualizar_inicio, fg="white", bg="green")
btnHash.place(x=505, y=80, width=30, height=25)


inicio()

tabla = "historico"  # Nombre de la tabla a mostrar
columnas = ["TIME", "BET", "ROLL", "SERVER", "PROFIT"]  # Columnas que queremos mostrar

app = TablaApp(ventana, tabla, columnas)
app.tree.place(x=20, y=420, width=525, height=130)  # Ajusta la posición y dimensiones


ventana.mainloop()