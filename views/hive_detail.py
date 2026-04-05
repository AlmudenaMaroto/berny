import flet as ft
from database import get_hive, get_visits_for_hive, get_latest_visit, delete_hive, delete_visit
from theme import *


def _visit_card(visit: dict, is_latest: bool, on_edit, on_delete):
    """Build a card showing visit details."""
    badge = None
    if is_latest:
        badge = ft.Container(
            content=ft.Text("ÚLTIMA", size=10, color=CARD_BG, weight=ft.FontWeight.BOLD),
            bgcolor=AMBER,
            border_radius=4,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )

    def info_row(icon, label, value):
        return ft.Row(
            [
                ft.Icon(icon, size=16, color=TEXT_SECONDARY),
                ft.Text(label, size=12, color=TEXT_SECONDARY, expand=True),
                ft.Text(str(value), size=12, color=TEXT_PRIMARY, weight=ft.FontWeight.W_500),
            ],
            spacing=6,
        )

    def check_row(icon, label, value):
        check_icon = ft.Icons.CHECK_CIRCLE if value else ft.Icons.CANCEL
        check_color = SUCCESS if value else TEXT_SECONDARY
        return ft.Row(
            [
                ft.Icon(icon, size=16, color=TEXT_SECONDARY),
                ft.Text(label, size=12, color=TEXT_SECONDARY, expand=True),
                ft.Icon(check_icon, size=16, color=check_color),
            ],
            spacing=6,
        )

    rows = [
        # Header
        ft.Row(
            [
                ft.Icon(ft.Icons.CALENDAR_TODAY, size=16, color=AMBER),
                ft.Text(
                    visit["date"],
                    size=14,
                    weight=ft.FontWeight.W_600,
                    color=TEXT_PRIMARY,
                    expand=True,
                ),
                *([] if badge is None else [badge]),
                ft.IconButton(
                    icon=ft.Icons.EDIT,
                    icon_size=18,
                    icon_color=TEXT_SECONDARY,
                    on_click=lambda e, vid=visit["id"]: on_edit(vid),
                    tooltip="Editar visita",
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=18,
                    icon_color=DANGER,
                    on_click=lambda e, vid=visit["id"]: on_delete(vid),
                    tooltip="Eliminar visita",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        ft.Divider(height=1, color=BORDER),
        check_row(ft.Icons.LOCK_OPEN, "Colmena abierta", visit.get("hive_opened", 0)),
        info_row(ft.Icons.CLOUD, "Clima", visit.get("weather", "")),
        info_row(ft.Icons.GRID_VIEW, "Cuadros totales", visit.get("total_frames", 0)),
        info_row(ft.Icons.CHILD_CARE, "Cría cerrada", visit.get("sealed_brood_frames", 0)),
        info_row(ft.Icons.CHILD_FRIENDLY, "Cría abierta", visit.get("open_brood_frames", 0)),
        info_row(ft.Icons.WATER_DROP, "Miel", visit.get("honey_frames", 0)),
        info_row(ft.Icons.PEST_CONTROL, "Abejas", visit.get("bee_amount", "")),
        check_row(ft.Icons.STAR, "Realeras", visit.get("has_queen_cells", 0)),
        info_row(ft.Icons.MALE, "Zánganos", visit.get("drone_level", "")),
        info_row(ft.Icons.RESTAURANT, "Alimentación", visit.get("feeding_type", "")),
        check_row(ft.Icons.BUG_REPORT, "Tiene varroa", visit.get("has_varroa", 0)),
        check_row(ft.Icons.HEALING, "Trat. varroa", visit.get("varroa_treatment", "") == "Sí"),
        check_row(ft.Icons.FASTFOOD, "Comida extra", visit.get("extra_food", 0)),
        check_row(ft.Icons.LAYERS, "Alza", visit.get("has_super", 0)),
        check_row(ft.Icons.SHIELD, "Excluidor reinas", visit.get("has_queen_excluder", 0)),
        info_row(ft.Icons.THERMOSTAT, "Rejilla", visit.get("grid_mode", "")),
    ]

    if visit.get("notes"):
        rows.append(ft.Divider(height=1, color=BORDER))
        rows.append(
            ft.Row(
                [
                    ft.Icon(ft.Icons.NOTES, size=16, color=TEXT_SECONDARY),
                    ft.Text(visit["notes"], size=12, color=TEXT_SECONDARY, expand=True),
                ],
                spacing=6,
            )
        )

    return ft.Container(
        content=ft.Column(rows, spacing=6),
        padding=14,
        border_radius=12,
        bgcolor=CARD_BG,
        border=ft.border.all(1, BORDER),
    )


def hive_detail_view(page: ft.Page, hive_id: int, navigate):
    hive = get_hive(hive_id)
    if not hive:
        return ft.View("/", [ft.Text("Colmena no encontrada")])

    hive_color = hive.get("color", AMBER)
    # find light variant
    hive_color_light = AMBER_LIGHT
    from theme import HIVE_COLORS
    for c in HIVE_COLORS:
        if c["hex"] == hive_color:
            hive_color_light = c["light"]
            break

    show_all = [False]  # mutable flag
    content_col = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def load_visits():
        content_col.controls.clear()
        visits = get_visits_for_hive(hive_id)

        if not visits:
            content_col.controls.append(
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.EVENT_NOTE, size=40, color=TEXT_SECONDARY),
                            ft.Text("Sin visitas registradas", size=14, color=TEXT_SECONDARY),
                            ft.Text("Pulsa + para añadir la primera", size=12, color=TEXT_SECONDARY),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=4,
                    ),
                    padding=30,
                    alignment=ft.alignment.center,
                )
            )
        else:
            display_visits = visits if show_all[0] else visits[:1]
            for i, v in enumerate(display_visits):
                content_col.controls.append(
                    _visit_card(
                        v,
                        is_latest=(i == 0),
                        on_edit=lambda vid: navigate("edit_visit", hive_id, vid),
                        on_delete=lambda vid: do_delete_visit(vid),
                    )
                )

            if len(visits) > 1 and not show_all[0]:
                content_col.controls.append(
                    ft.TextButton(
                        f"Ver historial completo ({len(visits)} visitas)",
                        icon=ft.Icons.HISTORY,
                        on_click=toggle_history,
                        style=ft.ButtonStyle(color=AMBER_DARK),
                    )
                )
            elif show_all[0] and len(visits) > 1:
                content_col.controls.append(
                    ft.TextButton(
                        "Ocultar historial",
                        icon=ft.Icons.KEYBOARD_ARROW_UP,
                        on_click=toggle_history,
                        style=ft.ButtonStyle(color=AMBER_DARK),
                    )
                )
        page.update()

    def toggle_history(e):
        show_all[0] = not show_all[0]
        load_visits()

    def do_delete_visit(visit_id):
        delete_visit(visit_id)
        load_visits()

    def do_delete_hive(e):
        def confirm_yes(e):
            delete_hive(hive_id)
            dialog.open = False
            page.update()
            navigate("home")

        def confirm_no(e):
            dialog.open = False
            page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("¿Eliminar colmena?"),
            content=ft.Text(f"Se eliminará '{hive['name']}' y todas sus visitas."),
            actions=[
                ft.TextButton("Cancelar", on_click=confirm_no),
                ft.TextButton("Eliminar", on_click=confirm_yes, style=ft.ButtonStyle(color=DANGER)),
            ],
        )
        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    load_visits()

    return ft.View(
        f"/hive/{hive_id}",
        [
            # App bar
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=lambda e: navigate("home"),
                        ),
                        ft.Container(
                            content=ft.Icon(ft.Icons.HEXAGON, color=hive_color, size=22),
                            width=36,
                            height=36,
                            border_radius=18,
                            bgcolor=hive_color_light,
                            alignment=ft.alignment.center,
                        ),
                        ft.Text(
                            hive["name"],
                            size=18,
                            weight=ft.FontWeight.W_600,
                            color=TEXT_PRIMARY,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.EDIT,
                            icon_color=TEXT_SECONDARY,
                            icon_size=20,
                            on_click=lambda e: navigate("edit_hive", hive_id),
                            tooltip="Editar nombre",
                        ),
                        ft.IconButton(
                            icon=ft.Icons.DELETE_OUTLINE,
                            icon_color=DANGER,
                            icon_size=20,
                            on_click=do_delete_hive,
                            tooltip="Eliminar colmena",
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=4,
                ),
                padding=ft.padding.only(left=4, right=8, top=8, bottom=4),
            ),
            # Visit content
            ft.Container(
                content=content_col,
                expand=True,
                padding=ft.padding.symmetric(horizontal=16, vertical=4),
            ),
            # FAB - add visit
            ft.Container(
                content=ft.FloatingActionButton(
                    icon=ft.Icons.ADD,
                    bgcolor=AMBER,
                    foreground_color=CARD_BG,
                    on_click=lambda e: navigate("add_visit", hive_id),
                    tooltip="Nueva visita",
                ),
                alignment=ft.alignment.bottom_right,
                padding=ft.padding.only(right=16, bottom=16),
            ),
        ],
        bgcolor=BG,
        padding=0,
        spacing=0,
    )
