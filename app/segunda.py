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
    cursor.execute('''CREATE TABLE IF NOT EXISTS ventas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TIMESTAMP,
                        total REAL,
                        nombre TEXT
                      )''')
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
    fecha_hoy = datetime.now().date().isoformat()
    cursor.execute("SELECT SUM(total) FROM ventas WHERE DATE(fecha) = ?", (fecha_hoy,))
    total = cursor.fetchone()[0]
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
 #Función para mostrar la tabla de ventas de hoy
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
    page.scroll = ft.ScrollMode.ALWAYS
    page.add(ft.Text("¡Bienvenido!", size=30))
    page.add(ft.Text("restaurante"))
    page.vertical_alignment = "center"

    productos_seleccionados = []
    venta_total = 0
    suma = 0
    total_del_dia = obtener_total_acumulado()

    suma_text = ft.Text(f"Total del día: ${total_del_dia:.2f}", size=24)
    venta_total_text = ft.Text(f"Venta total acumulada: ${venta_total:.2f}", size=24)

    def boton_click(e):
        nonlocal venta_total, suma
        precio = e.control.data
        nombre_producto = e.control.text
        venta_total += precio
        suma += precio
        suma_text.value = f"Total del día: ${total_del_dia + suma:.2f}"
        venta_total_text.value = f"Venta total acumulada: ${venta_total:.2f}"

        producto_existente = next((p for p in productos_seleccionados if p['nombre'] == nombre_producto), None)
        if producto_existente:
            producto_existente['cantidad'] += 1
        else:
            productos_seleccionados.append({'nombre': nombre_producto, 'precio': precio, 'cantidad': 1})

        page.update()

    def mostrar_resumen_venta(e):
        nonlocal productos_seleccionados

        ventana_resumen = ft.AlertDialog(
            title=ft.Text("Resumen de la venta"),
            actions=[
                ft.TextButton("Cancelar", on_click=lambda e: cerrar_ventana_resumen()),
                ft.TextButton("Confirmar y guardar", on_click=lambda e: confirmar_guardar_venta())
            ]
        )
        # Añadir el diálogo a la página antes de actualizarlo
        page.dialog = ventana_resumen    # Añadir el diálogo a la página antes de actualizarlo

        def cerrar_ventana_resumen():
            ventana_resumen.open = False
            page.update()  # Actualizar la página para cerrar el diálogo
            page.controls.clear()  # Limpiar el contenido de la página
            segunda_pagina(page)  # Recargar la página con los datos actualizados

        def eliminar_producto(nombre):
            nonlocal productos_seleccionados
            productos_seleccionados = [p for p in productos_seleccionados if p['nombre'] != nombre]
            actualizar_ventana_resumen()

        def actualizar_ventana_resumen():
            rows = []
            for producto in productos_seleccionados:
                total_producto = producto['precio'] * producto['cantidad']
                eliminar_button = ft.IconButton(
                    ft.icons.DELETE,
                    on_click=lambda e, nombre=producto['nombre']: eliminar_producto(nombre)
                )
                rows.append(ft.DataRow([
                    ft.DataCell(ft.Text(producto['nombre'])),
                    ft.DataCell(ft.Text(f"Cantidad: {producto['cantidad']}")),
                    ft.DataCell(ft.Text(f"${producto['precio']:.2f}")),
                    ft.DataCell(ft.Text(f"${total_producto:.2f}")),
                    ft.DataCell(eliminar_button),
                ]))

            if not rows:
                rows.append(ft.DataRow([ft.DataCell(ft.Text("No hay productos seleccionados"))]))

            table = ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Producto")),
                    ft.DataColumn(ft.Text("Cantidad")),
                    ft.DataColumn(ft.Text("Precio")),
                    ft.DataColumn(ft.Text("Total")),
                    ft.DataColumn(ft.Text("Eliminar"))
                ],
                rows=rows,
            )

            ventana_resumen.content = table
            page.update()
            ventana_resumen.update()

        actualizar_ventana_resumen()
        ventana_resumen.open = True
        page.update()

    def confirmar_guardar_venta():
        nonlocal productos_seleccionados, venta_total, suma
        fecha_actual = datetime.now()
        fecha_str = fecha_actual.strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            for producto in productos_seleccionados:
                for _ in range(producto['cantidad']):
                    cursor.execute("INSERT INTO ventas (fecha, total, nombre) VALUES (?, ?, ?)",
                                   (fecha_str, producto['precio'], producto['nombre']))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error al guardar la venta: {e}")
        finally:
            conn.close()

        productos_seleccionados.clear()
        venta_total = 0
        venta_total_text.value = f"Venta total acumulada: ${venta_total:.2f}"
        suma_text.value = f"Total del día: ${obtener_total_acumulado():.2f}"
        page.update()
        page.controls.clear() # Limpiar el contenido de la página
        segunda_pagina(page)  # Recargar la página con los datos actualizados


    precios = [10, 20, 30, 40, 50]
    textos = ["Compra básica", "Compra avanzada", "Compra premium", "Compra exclusiva", "Compra VIP"]
    colores = [ft.colors.INDIGO_500, ft.colors.TEAL_500, ft.colors.PINK_500, ft.colors.CYAN_500, ft.colors.YELLOW_700]

    botones = []
    for precio, texto, color in zip(precios, textos, colores):
        boton = ft.Container(
            content=ft.ElevatedButton(
                text=f"{texto} por ${precio}",
                data=precio,
                on_click=boton_click,
                width=200,
                height=150,
                bgcolor=color,
                color=ft.colors.WHITE,
            ),
            alignment=ft.alignment.center,
            padding=10
        )
        botones.append(boton)

    botones_grid = ft.GridView(
        controls=botones,
        runs_count=3,
        spacing=20,
        run_spacing=20,
        max_extent=200
    )

    boton_guardar = ft.ElevatedButton(
        text="Guardar venta",
        on_click=mostrar_resumen_venta,
        bgcolor="blue",
        color="white",
    )
    boton_guardar_container = ft.Container(
        content=boton_guardar,
        alignment=ft.alignment.center,
    )

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    venta_total_text,
                    botones_grid,
                    boton_guardar_container,
                    mostrar_tabla_ventas(page),
                    suma_text,
                ],
                spacing=20,
                scroll=ft.ScrollMode.ALWAYS
            ),
            alignment=ft.alignment.center
        )
    )

# Crear las tablas al iniciar la aplicación
create_tables()

# Ejecutar la aplicación de Flet
ft.app(target=segunda_pagina)
