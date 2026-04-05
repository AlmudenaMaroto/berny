import flet as ft
from database import get_hive, update_hive
from theme import *


def edit_hive_view(page: ft.Page, hive_id: int, navigate):
    hive = get_hive(hive_id)
    if not hive:
        return ft.Column([ft.Text("Colmena no encontrada")])

    selected_color = [hive.get("color", AMBER)]

    name_field = ft.TextField(
        label="Nombre de la colmena",
        value=hive["name"],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    color_row = ft.Row(spacing=4)

    def build_color_picker():
        color_row.controls.clear()
        for c in HIVE_COLORS:
            is_sel = c["hex"] == selected_color[0]
            color_row.controls.append(
                ft.Container(
                    width=32,
                    height=32,
                    border_radius=16,
                    bgcolor=c["hex"],
                    border=ft.border.all(3, TEXT_PRIMARY if is_sel else "transparent"),
                    on_click=lambda e, col=c["hex"]: select_color(col),
                    tooltip=c["name"],
                )
            )

    def select_color(col):
        selected_color[0] = col
        build_color_picker()
        page.update()

    build_color_picker()

    def save(e):
        name = name_field.value.strip() if name_field.value else ""
        if not name:
            name_field.error_text = "El nombre no puede estar vacío"
            page.update()
            return
        update_hive(hive_id, name, selected_color[0])
        navigate("detail", hive_id)

    return ft.Column(
        [
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=lambda e: navigate("detail", hive_id),
                        ),
                        ft.Text(
                            "Editar colmena",
                            size=18,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_PRIMARY,
                            expand=True,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(left=4, right=16, top=8, bottom=4),
            ),
            ft.Container(
                content=ft.Column(
                    [
                        name_field,
                        ft.Container(height=8),
                        ft.Text("Color", size=13, weight=ft.FontWeight.W_600, color=TEXT_SECONDARY),
                        color_row,
                        ft.Container(height=16),
                        ft.ElevatedButton(
                            "Guardar",
                            icon=ft.Icons.SAVE,
                            bgcolor=AMBER,
                            color=CARD_BG,
                            on_click=save,
                            width=200,
                            height=44,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.all(20),
            ),
        ],
        expand=True,
        spacing=0,
    )
