import flet as ft
from segunda import segunda_pagina
# Función principal que maneja la UI
def main(page: ft.Page):
    page.title = "Login"
    page.vertical_alignment="center"
    page.horizontal_alignment="center"
    
    # Función para manejar el inicio de sesión
    def login(e):
        if (username.value == "admin" and password.value == "1234"):
            page.clean()  # Limpia la pantalla actual
            page.add(ft.Text(f"¡Bienvenido, {username.value}!", size=30))
        elif (username.value == "empleado" and password.value == "empleado"):
            page.clean()  # Limpia la pantalla actual
            segunda_pagina(page)
        else:
            error_message.value = "Credenciales incorrectas. Inténtalo de nuevo."
            page.update()

    # Campos de entrada para usuario y contraseña
    username = ft.TextField(label="Usuario", width=300)
    password = ft.TextField(label="Contraseña", password=True, width=300)
    error_message = ft.Text(color="red")

    # Botón de inicio de sesión
    login_button = ft.ElevatedButton("Iniciar sesión", on_click=login)

    # Añadir los elementos a la página
    page.add(
        ft.Column(
            [
                ft.Text("Inicio de sesión", size=40),
                username,
                password,
                login_button,
                error_message,
                
            ],

            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )
    
# Ejecutar la aplicación
ft.app(target=main)
