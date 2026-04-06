import flet as ft
import os
import shutil
import uuid
from datetime import datetime
from database import create_visit, get_visit, update_visit, get_photos_dir
from theme import *


def visit_form_view(page: ft.Page, hive_id: int, navigate, visit_id=None):
    """Form to add or edit a visit."""
    editing = visit_id is not None
    existing = None
    if editing:
        existing = get_visit(visit_id)

    def val(field, default=""):
        if existing:
            return existing.get(field, default)
        return default

    title = "Editar visita" if editing else "Nueva visita"

    # --- Form fields ---
    date_field = ft.TextField(
        label="Fecha (YYYY-MM-DD)",
        value=val("date", datetime.now().strftime("%Y-%m-%d")),
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    weather_field = ft.Dropdown(
        label="Clima",
        value=val("weather", "Soleado"),
        options=[
            ft.dropdown.Option("Soleado"),
            ft.dropdown.Option("Nublado"),
            ft.dropdown.Option("Lluvioso"),
            ft.dropdown.Option("Ventoso"),
            ft.dropdown.Option("Frío"),
            ft.dropdown.Option("Caluroso"),
        ],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    total_frames = ft.TextField(
        label="Cuadros totales",
        value=str(val("total_frames", 0)),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    sealed_brood = ft.TextField(
        label="Cría cerrada",
        value=str(val("sealed_brood_frames", 0)),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    open_brood = ft.TextField(
        label="Cría abierta",
        value=str(val("open_brood_frames", 0)),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    honey_frames_field = ft.TextField(
        label="Cuadros con miel",
        value=str(val("honey_frames", 0)),
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    bee_amount_dd = ft.Dropdown(
        label="Cantidad de abejas",
        value=val("bee_amount", "Media"),
        options=[
            ft.dropdown.Option("Poca"),
            ft.dropdown.Option("Media"),
            ft.dropdown.Option("Mucha"),
        ],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    queen_cells_sw = ft.Switch(
        label="Realeras",
        value=bool(val("has_queen_cells", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    drone_level_dd = ft.Dropdown(
        label="Nivel de zánganos",
        value=val("drone_level", "Bajo"),
        options=[
            ft.dropdown.Option("Bajo"),
            ft.dropdown.Option("Medio"),
            ft.dropdown.Option("Alto"),
        ],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    feeding_dd = ft.Dropdown(
        label="Alimentación",
        value=val("feeding_type", "Ninguna"),
        options=[
            ft.dropdown.Option("Ninguna"),
            ft.dropdown.Option("Sólida"),
            ft.dropdown.Option("Líquida"),
        ],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    varroa_sw = ft.Switch(
        label="Tratamiento varroa",
        value=bool(val("varroa_treatment", "") == "Sí") if isinstance(val("varroa_treatment", ""), str) else bool(val("varroa_treatment", "")),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    has_varroa_sw = ft.Switch(
        label="Tiene varroa",
        value=bool(val("has_varroa", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    hive_opened_sw = ft.Switch(
        label="Colmena abierta",
        value=bool(val("hive_opened", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    extra_food_sw = ft.Switch(
        label="Comida extra",
        value=bool(val("extra_food", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    super_sw = ft.Switch(
        label="Alza",
        value=bool(val("has_super", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    queen_excluder_sw = ft.Switch(
        label="Excluidor de reinas",
        value=bool(val("has_queen_excluder", 0)),
        active_color=AMBER,
        inactive_thumb_color="#D6D3D1",
        inactive_track_color="#E7E5E4",
        label_style=ft.TextStyle(color=TEXT_PRIMARY),
    )

    grid_mode_dd = ft.Dropdown(
        label="Rejilla",
        value=val("grid_mode", "Invierno"),
        options=[
            ft.dropdown.Option("Verano"),
            ft.dropdown.Option("Invierno"),
        ],
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    notes_field = ft.TextField(
        label="Notas",
        value=val("notes", ""),
        multiline=True,
        min_lines=2,
        max_lines=4,
        border_radius=8,
        border_color=BORDER,
        focused_border_color=AMBER,
        text_size=14,
    )

    # --- Photo ---
    photo_path = [val("photo_path", "")]
    photo_preview = ft.Column(spacing=4)

    def build_photo_preview():
        photo_preview.controls.clear()
        if photo_path[0] and os.path.exists(photo_path[0]):
            photo_preview.controls.append(
                ft.Container(
                    content=ft.Stack(
                        [
                            ft.Image(
                                src=photo_path[0],
                                width=280,
                                height=200,
                                fit=ft.ImageFit.COVER,
                                border_radius=ft.border_radius.all(8),
                            ),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.Icons.DELETE,
                                    icon_color=CARD_BG,
                                    icon_size=20,
                                    bgcolor="#00000088",
                                    on_click=remove_photo,
                                    tooltip="Quitar foto",
                                ),
                                alignment=ft.alignment.top_right,
                            ),
                        ],
                    ),
                    border_radius=8,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )
            )

    def remove_photo(e):
        photo_path[0] = ""
        build_photo_preview()
        page.update()

    file_picker = ft.FilePicker()

    def on_file_picked(e: ft.FilePickerResultEvent):
        if e.files and len(e.files) > 0:
            picked = e.files[0]
            photos_dir = get_photos_dir()
            ext = os.path.splitext(picked.name)[1] if picked.name else ".jpg"
            dest_name = f"{uuid.uuid4().hex}{ext}"
            dest_path = os.path.join(photos_dir, dest_name)
            if picked.path:
                shutil.copy2(picked.path, dest_path)
                photo_path[0] = dest_path
            elif picked.bytes:
                with open(dest_path, "wb") as f:
                    f.write(picked.bytes)
                photo_path[0] = dest_path
            build_photo_preview()
            page.update()

    file_picker.on_result = on_file_picked
    page.overlay.append(file_picker)

    def pick_photo(e):
        file_picker.pick_files(
            dialog_title="Seleccionar foto",
            allow_multiple=False,
            allowed_extensions=["jpg", "jpeg", "png", "webp"],
            with_data=True,
        )

    build_photo_preview()

    def _int(tf):
        try:
            return int(tf.value)
        except (ValueError, TypeError):
            return 0

    def on_number_focus(e):
        """Clear the field if it contains only '0' when focused."""
        if e.control.value == "0":
            e.control.value = ""
            e.control.update()

    def on_number_blur(e):
        """Restore '0' if the field is empty when unfocused."""
        if not e.control.value or e.control.value.strip() == "":
            e.control.value = "0"
            e.control.update()

    # Attach focus/blur handlers to numeric fields
    for nf in [total_frames, sealed_brood, open_brood, honey_frames_field]:
        nf.on_focus = on_number_focus
        nf.on_blur = on_number_blur

    def save(e):
        data = {
            "date": date_field.value or datetime.now().strftime("%Y-%m-%d"),
            "weather": weather_field.value or "",
            "total_frames": _int(total_frames),
            "sealed_brood_frames": _int(sealed_brood),
            "open_brood_frames": _int(open_brood),
            "honey_frames": _int(honey_frames_field),
            "bee_amount": bee_amount_dd.value or "Media",
            "has_queen_cells": queen_cells_sw.value,
            "drone_level": drone_level_dd.value or "Bajo",
            "feeding_type": feeding_dd.value or "Ninguna",
            "varroa_treatment": "Sí" if varroa_sw.value else "No",
            "has_varroa": has_varroa_sw.value,
            "has_super": super_sw.value,
            "has_queen_excluder": queen_excluder_sw.value,
            "grid_mode": grid_mode_dd.value or "Invierno",
            "hive_opened": hive_opened_sw.value,
            "extra_food": extra_food_sw.value,
            "notes": notes_field.value or "",
            "photo_path": photo_path[0],
        }

        if editing:
            update_visit(visit_id, data)
        else:
            create_visit(hive_id, data)

        navigate("detail", hive_id)

    def section_title(text):
        return ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=AMBER_DARK)

    return ft.Column(
        [
            # App bar
            ft.Container(
                content=ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_color=TEXT_PRIMARY,
                            on_click=lambda e: navigate("detail", hive_id),
                        ),
                        ft.Text(
                            title,
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
            # Form
            ft.Container(
                content=ft.Column(
                    [
                        section_title("General"),
                        date_field,
                        weather_field,
                        ft.Container(
                            content=hive_opened_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Divider(height=1, color=BORDER),
                        section_title("Cuadros"),
                        total_frames,
                        sealed_brood,
                        open_brood,
                        honey_frames_field,
                        ft.Divider(height=1, color=BORDER),
                        section_title("Población"),
                        bee_amount_dd,
                        drone_level_dd,
                        ft.Container(
                            content=queen_cells_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Divider(height=1, color=BORDER),
                        section_title("Manejo"),
                        feeding_dd,
                        ft.Container(
                            content=extra_food_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Container(
                            content=has_varroa_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Container(
                            content=varroa_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Container(
                            content=super_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        ft.Container(
                            content=queen_excluder_sw,
                            padding=ft.padding.symmetric(vertical=4),
                        ),
                        grid_mode_dd,
                        ft.Divider(height=1, color=BORDER),
                        section_title("Observaciones"),
                        notes_field,
                        ft.Divider(height=1, color=BORDER),
                        section_title("Foto"),
                        photo_preview,
                        ft.OutlinedButton(
                            "Adjuntar foto",
                            icon=ft.Icons.CAMERA_ALT,
                            on_click=pick_photo,
                            style=ft.ButtonStyle(
                                color=AMBER_DARK,
                                side=ft.BorderSide(1, BORDER),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.Container(height=12),
                        ft.ElevatedButton(
                            "Guardar visita",
                            icon=ft.Icons.SAVE,
                            bgcolor=AMBER,
                            color=CARD_BG,
                            on_click=save,
                            width=250,
                            height=46,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=10),
                            ),
                        ),
                        ft.Container(height=20),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    scroll=ft.ScrollMode.AUTO,
                    spacing=8,
                ),
                expand=True,
                padding=ft.padding.symmetric(horizontal=20, vertical=4),
            ),
        ],
        expand=True,
        spacing=0,
    )
