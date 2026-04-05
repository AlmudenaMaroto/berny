import flet as ft
from database import init_db, set_db_dir, export_db, import_db
from views.home import home_view
from views.hive_detail import hive_detail_view
from views.edit_hive import edit_hive_view
from views.visit_form import visit_form_view
from theme import SUCCESS, DANGER
import os
import traceback


def main(page: ft.Page):
    try:
        page.title = "Berny"
        page.bgcolor = "#FAFAF9"

        is_mobile = page.platform in (ft.PagePlatform.ANDROID, ft.PagePlatform.IOS)

        # Window size only on desktop
        if not is_mobile:
            page.window.width = 400
            page.window.height = 740

        # Set DB directory
        if is_mobile:
            storage_dir = os.path.join(os.path.expanduser("~"), ".berny")
            set_db_dir(storage_dir)

        init_db()

        # File pickers only on desktop (not supported well on mobile)
        export_picker = None
        import_picker = None
        if not is_mobile:
            def on_export_result(e: ft.FilePickerResultEvent):
                if not e.path:
                    return
                try:
                    export_db(e.path)
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Base de datos exportada correctamente"),
                        bgcolor=SUCCESS,
                    )
                    page.snack_bar.open = True
                except Exception as exc:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(f"Error al exportar: {exc}"),
                        bgcolor=DANGER,
                    )
                    page.snack_bar.open = True
                page.update()

            def on_import_result(e: ft.FilePickerResultEvent):
                if not e.files:
                    return
                src = e.files[0].path
                try:
                    import_db(src)
                    page.snack_bar = ft.SnackBar(
                        ft.Text("Base de datos importada. Recargando..."),
                        bgcolor=SUCCESS,
                    )
                    page.snack_bar.open = True
                    navigate("home")
                except ValueError as exc:
                    page.snack_bar = ft.SnackBar(
                        ft.Text(str(exc)),
                        bgcolor=DANGER,
                    )
                    page.snack_bar.open = True
                page.update()

            export_picker = ft.FilePicker(on_result=on_export_result)
            import_picker = ft.FilePicker(on_result=on_import_result)
            page.overlay.extend([export_picker, import_picker])

        def navigate(route, *args):
            page.views.clear()
            if route == "home":
                page.views.append(home_view(page, navigate, export_picker, import_picker))
            elif route == "detail":
                hive_id = args[0]
                page.views.append(hive_detail_view(page, hive_id, navigate))
            elif route == "edit_hive":
                hive_id = args[0]
                page.views.append(edit_hive_view(page, hive_id, navigate))
            elif route == "add_visit":
                hive_id = args[0]
                page.views.append(visit_form_view(page, hive_id, navigate))
            elif route == "edit_visit":
                hive_id = args[0]
                visit_id = args[1]
                page.views.append(visit_form_view(page, hive_id, navigate, visit_id))
            page.update()

        navigate("home")
    except Exception:
        traceback.print_exc()
        page.views.clear()
        page.views.append(
            ft.View("/error", [ft.Text(f"Error: {traceback.format_exc()}", selectable=True)])
        )
        page.update()


ft.app(target=main)
