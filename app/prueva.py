import flet as ft
import sqlite3
from datetime import datetime

# Función para crear y gestionar la conexión de la base de datos
def get_db_connection():
    conn = sqlite3.connect("ventas.db", check_same_thread=False)
    return conn

# Crear las tablas necesarias si no existen
def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Crear tabla de ventas si no existe (con columna 'nombre')
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TIMESTAMP,
                        total REAL,
                        nombre TEXT
                      )''')

    # Crear tabla para almacenar el total acumulado si no existe
    cursor.execute('''CREATE TABLE IF NOT EXISTS totalote (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        total REAL
                      )''')
    conn.commit()
    conn.close()

# Función para obtener las ventas de hoy
def obtener_ventas_de_hoy():
    conn = get_db_connection()
    cursor = conn.cursor()
    fecha_hoy = datetime.now().date().isoformat()  # Fecha de hoy en formato ISO (YYYY-MM-DD)
    cursor.execute("SELECT fecha, total, nombre FROM ventas WHERE DATE(fecha) = ?", (fecha_hoy,))
    ventas = cursor.fetchall()
    conn.close()
    return ventas

# Función para obtener el total acumulado del día
def obtener_total_acumulado():
    conn = get_db_connection()
    cursor = conn.cursor()
    fecha_hoy = datetime.now().date().isoformat()  # Fecha de hoy en formato ISO
    cursor.execute("SELECT SUM(total) FROM ventas WHERE DATE(fecha) = ?", (fecha_hoy,))
    total = cursor.fetchone()[0]  # Obtiene la suma de los totales
    conn.close()
    return total if total is not None else 0

# Función para guardar el total acumulado en la base de datos
def guardar_total_acumulado(total):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM totalote")  # Elimina el registro anterior
    cursor.execute("INSERT INTO totalote (total) VALUES (?)", (total,))
    conn.commit()
    conn.close()

# Función para mostrar la tabla de ventas de hoy
def mostrar_tabla_ventas(page: ft.Page):
    ventas = obtener_ventas_de_hoy()  # Obtener las ventas de hoy

    # Crear una lista de filas con los datos de las ventas
    rows = []
    for venta in ventas:
        fecha_venta = venta[0]  # Fecha de la venta
        total_venta = venta[1]  # Total de la venta
        nombre_producto = venta[2]  # Nombre del producto
        rows.append([str(fecha_venta), f"${total_venta:.2f}", nombre_producto])

    # Crear una tabla para mostrar las ventas
    table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Fecha")),
            ft.DataColumn(ft.Text("Total")),
            ft.DataColumn(ft.Text("Producto"))
        ],
        rows=[ft.DataRow([ft.DataCell(ft.Text(celda)) for celda in fila]) for fila in rows],
    )

    return ft.Container(
        content=table,
        alignment=ft.alignment.center  # Centrar la tabla
    )

# Función que define la segunda página
def segunda_pagina(page: ft.Page):
    page.title = "Segunda Página"
    page.scroll = ft.ScrollMode.ALWAYS  # Habilitar scroll en toda la página
    page.add(ft.Text("¡Bienvenido!", size=30))
    page.add(ft.Text("restaurante"))
    page.vertical_alignment = "center"

    venta_total = 0  # Variable que guarda el total de la venta acumulada
    suma = 0  # Total acumulado de las ventas

    # Obtener el total acumulado del día
    total_del_dia = obtener_total_acumulado()

    # Texto que muestra el total acumulado
    suma_text = ft.Text(f"Total del día: ${total_del_dia:.2f}", size=24)
    venta_total_text = ft.Text(f"Venta total acumulada: ${venta_total:.2f}", size=24)

    # Función para manejar el clic en los botones de precio
    def boton_click(e):
        nonlocal venta_total, suma  # Declaración de nonlocal antes de usar suma y venta_total
        precio = e.control.data  # Obtener el precio del botón desde data
        nombre_producto = e.control.text  # Obtener el texto del botón (nombre del producto)
        venta_total += precio
        suma += precio
        suma_text.value = f"Total del día: ${total_del_dia + suma:.2f}"  # Actualizamos el total del día
        venta_total_text.value = f"Venta total acumulada: ${venta_total:.2f}"  # Actualizamos el total de la venta
        e.control.bgcolor = "green"  # Cambia el color de fondo del botón
        page.update()

    # Función para guardar la venta en la base de datos
    def guardar_venta(e):
        nonlocal venta_total, suma  # Declaración de nonlocal antes de usar venta_total y suma
        fecha_actual = datetime.now()

        # Convertir la fecha a formato string para evitar problemas con sqlite3
        fecha_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')  # Formato ISO 8601

        # Obtener el nombre del botón que se presionó (del control que activó el evento)
        nombre_producto = e.control.text  # Esto obtiene el texto del botón (por ejemplo "Compra básica")

        # Usamos la función get_db_connection() para obtener una conexión a la base de datos
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insertar el total y el nombre del producto junto con la fecha
        cursor.execute("INSERT INTO ventas (fecha, total, nombre) VALUES (?, ?, ?)", 
                       (fecha_str, venta_total, nombre_producto))
        conn.commit()
        conn.close()  # Cerramos la conexión después de realizar la operación
#################################
        # Guardamos el total acumulado actualizado
        total_acumulado = obtener_total_acumulado() + venta_total
        guardar_total_acumulado(total_acumulado)

        # Limpiar la venta total y recargar la página
        venta_total = 0
        venta_total_text.value = f"Venta total acumulada: ${venta_total:.2f}"  # Limpiamos la venta total en la UI

        # Limpiar la página y recargarla con la tabla actualizada
        page.controls.clear()  # Limpiar el contenido de la página
        segunda_pagina(page)  # Recargar la página con los datos actualizados

    # Crear botones de diferentes precios con texto descriptivo
    precios = [10, 20, 30, 40, 50]
    textos = [
        "Compra básica",
        "Compra avanzada",
        "Compra premium",
        "Compra exclusiva",
        "Compra VIP"
    ]
    colores = [
        ft.colors.INDIGO_500,  # Azul vibrante
        ft.colors.TEAL_500,    # Verde esmeralda
        ft.colors.PINK_500,    # Rosa brillante
        ft.colors.CYAN_500,    # Azul claro
        ft.colors.YELLOW_700   # Amarillo brillante
    ]
    botones = []
    for precio, texto, color in zip(precios, textos, colores):
        boton = ft.Container(
            content=ft.ElevatedButton(
                text=f"{texto} por ${precio}",  # Texto más descriptivo
                data=precio,
                on_click=boton_click,
                width=200,  # Aumentar el ancho del botón
                height=150,  # Aumentar la altura del botón
                bgcolor=color,  # Color de fondo del botón
                color=ft.colors.WHITE,  # Color del texto
            ),
            alignment=ft.alignment.center,
            shadow=ft.BoxShadow(  # Sombra para darle un efecto 3D
                blur_radius=10,
                spread_radius=0,
                color=ft.colors.BLACK12,
                offset=ft.Offset(4, 4)
            ),
            padding=10  # Espaciado interno del contenedor
        )
        botones.append(boton)

    # Usar GridView para mostrar los botones en una cuadrícula
    botones_grid = ft.GridView(
        controls=botones,
        runs_count=3,  # Número de columnas
        spacing=20,  # Espaciado horizontal
        run_spacing=20,  # Espaciado vertical
        max_extent=200  # Tamaño máximo de los elementos
    )

    # Botón para guardar la venta
    boton_guardar = ft.ElevatedButton(
        text="Guardar venta",
        on_click=guardar_venta,
        bgcolor="blue",
        color="white",
    )
    # Contenedor para centrar el botón
    boton_guardar_container = ft.Container(
        content=boton_guardar,
        alignment=ft.alignment.center,  # Centrar el botón
    )

    # Añadir los elementos a la página
    page.add(
        ft.Container(
            content=ft.Column(
                [
                    venta_total_text,
                    botones_grid,
                    boton_guardar_container,
                    mostrar_tabla_ventas(page),
                    suma_text
                ],
                spacing=20,  # Espacio entre los elementos
                scroll=ft.ScrollMode.ALWAYS  # Scroll en toda la columna
            ),
            alignment=ft.alignment.center  # Centrar todo el contenido
        )
    )

# Crear las tablas al iniciar la aplicación
create_tables()

# Ejecutar la aplicación de Flet
ft.app(target=segunda_pagina)
