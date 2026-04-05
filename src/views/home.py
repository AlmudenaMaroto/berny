import flet as ft
from database import get_all_hives, create_hive, delete_hive
from theme import *


def _color_light(hex_color):
    for c in HIVE_COLORS:
        if c["hex"] == hex_color:
            return c["light"]
    return AMBER_LIGHT


def home_view(page: ft.Page, navigate, on_export=None, on_import=None):
    selected_color = [HIVE_COLORS[0]["hex"]]

    name_field = ft.TextField(
        hint_text="Nombre de la colmena",
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        expand=True,
        text_size=14,
    )

    color_row = ft.Row(spacing=4)

    def build_color_picker():
        color_row.controls.clear()
        for c in HIVE_COLORS:
            is_sel = c["hex"] == selected_color[0]
            color_row.controls.append(
                ft.Container(
                    width=28,
                    height=28,
                    border_radius=14,
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

    hive_list = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def load_hives():
        hive_list.controls.clear()
        hives = get_all_hives()
        if not hives:
            hive_list.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.HIVE, size=48, color=TEXT_SECONDARY),
                            ft.Text(
                                "No hay colmenas",
                                size=16,
                                color=TEXT_SECONDARY,
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Text(
                                "Añade tu primera colmena arriba",
                                size=13,
                                color=TEXT_SECONDARY,
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=40,
                    alignment=ft.Alignment.CENTER,
                )
            )
        else:
            for hive in hives:
                last_visit = hive.get("last_visit_date", None)
                subtitle = (
                    f"Última visita: {last_visit}"
                    if last_visit
                    else "Sin visitas"
                )
                visit_count = hive.get("visit_count", 0)
                hive_color = hive.get("color", AMBER)
                hive_color_light = _color_light(hive_color)

                hive_card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(ft.Icons.HEXAGON, color=hive_color, size=28),
                                width=44,
                                height=44,
                                border_radius=22,
                                bgcolor=hive_color_light,
                                alignment=ft.Alignment.CENTER,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        hive["name"],
                                        size=15,
                                        weight=ft.FontWeight.W_600,
                                        color=TEXT_PRIMARY,
                                    ),
                                    ft.Text(
                                        subtitle,
                                        size=12,
                                        color=TEXT_SECONDARY,
                                    ),
                                ],
                                spacing=2,
                                expand=True,
                            ),
                            ft.Container(
                                content=ft.Text(
                                    str(visit_count),
                                    size=12,
                                    color=AMBER_DARK,
                                    weight=ft.FontWeight.W_600,
                                ),
                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                border_radius=12,
                                bgcolor=AMBER_LIGHT,
                            ),
                            ft.Icon(
                                ft.Icons.CHEVRON_RIGHT, color=TEXT_SECONDARY, size=20
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=12,
                    ),
                    padding=12,
                    border_radius=12,
                    bgcolor=CARD_BG,
                    border=ft.border.all(1, BORDER),
                    on_click=lambda e, hid=hive["id"]: navigate("detail", hid),
                    ink=True,
                )
                hive_list.controls.append(hive_card)
        page.update()

    def add_hive(e):
        name = name_field.value.strip() if name_field.value else ""
        if not name:
            name_field.error_text = "Escribe un nombre"
            page.update()
            return
        name_field.error_text = None
        create_hive(name, selected_color[0])
        name_field.value = ""
        load_hives()

    def on_delete_hive(hive_id):
        delete_hive(hive_id)
        load_hives()

    load_hives()

    # App bar buttons - only show export/import on desktop
    app_bar_buttons = []
    if on_export:
        app_bar_buttons.append(
            ft.IconButton(
                icon=ft.Icons.FILE_UPLOAD,
                icon_color=TEXT_SECONDARY,
                icon_size=22,
                on_click=on_export,
                tooltip="Exportar datos",
            )
        )
    if on_import:
        app_bar_buttons.append(
            ft.IconButton(
                icon=ft.Icons.FILE_DOWNLOAD,
                icon_color=TEXT_SECONDARY,
                icon_size=22,
                on_click=on_import,
                tooltip="Importar datos",
            )
        )

    return ft.Column(
        [
            # App bar
            ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.HIVE, color=AMBER, size=28),
                        ft.Text(
                            "Berny",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=TEXT_PRIMARY,
                            expand=True,
                        ),
                        *app_bar_buttons,
                    ],
                    spacing=4,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.only(left=16, right=16, top=12, bottom=8),
            ),
            # Add hive row
            ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                name_field,
                                ft.IconButton(
                                    icon=ft.Icons.ADD_CIRCLE,
                                    icon_color=AMBER,
                                    icon_size=32,
                                    on_click=add_hive,
                                    tooltip="Añadir colmena",
                                ),
                            ],
                            spacing=4,
                        ),
                        color_row,
                    ],
                    spacing=6,
                ),
                padding=ft.padding.symmetric(horizontal=16, vertical=4),
            ),
            # Hive list
            ft.Container(
                content=hive_list,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
            ),
        ],
        expand=True,
        spacing=0,
    )
