import flet as ft
import traceback


def main(page: ft.Page):
    page.title = "Berny"
    page.bgcolor = "#FAFAF9"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.theme = ft.Theme(
        color_scheme_seed="#F59E0B",
    )

    try:
        from database import init_db, export_db, import_db
        from views.home import home_view
        from views.hive_detail import hive_detail_view
        from views.edit_hive import edit_hive_view
        from views.visit_form import visit_form_view
        from theme import SUCCESS, DANGER

        init_db()

        # Detect platform safely
        is_mobile = False
        try:
            is_mobile = page.platform.is_mobile()
        except Exception:
            try:
                p = str(page.platform).upper()
                is_mobile = "ANDROID" in p or "IOS" in p
            except Exception:
                pass

        # Window size only on desktop
        if not is_mobile:
            try:
                page.window.width = 400
                page.window.height = 740
            except Exception:
                pass

        # Export/import
        snack = ft.SnackBar(ft.Text(""))
        page.overlay.append(snack)

        def show_snack(msg, color=SUCCESS):
            snack.content = ft.Text(msg)
            snack.bgcolor = color
            snack.open = True
            page.update()

        file_picker = ft.FilePicker()
        if is_mobile:
            page.overlay.append(file_picker)

        async def do_export(e):
            try:
                from database import get_db_path
                import sqlite3
                db_path = get_db_path()
                # Force WAL checkpoint so all data is in the main file
                conn = sqlite3.connect(db_path)
                conn.execute("PRAGMA wal_checkpoint(FULL)")
                conn.close()
                # Read DB bytes (required for mobile)
                with open(db_path, "rb") as f:
                    db_bytes = f.read()
                result = await file_picker.save_file(
                    dialog_title="Exportar base de datos",
                    file_name="berny_backup.db",
                    src_bytes=db_bytes,
                )
                if result:
                    show_snack("Base de datos exportada correctamente")
            except Exception as exc:
                show_snack(f"Error al exportar: {exc}", DANGER)

        async def do_import(e):
            try:
                files = await file_picker.pick_files(
                    dialog_title="Importar base de datos",
                    allow_multiple=False,
                    with_data=True,
                )
                if files:
                    f = files[0]
                    if hasattr(f, 'bytes') and f.bytes:
                        import tempfile, os
                        tmp = os.path.join(tempfile.gettempdir(), "berny_import.db")
                        with open(tmp, "wb") as tf:
                            tf.write(f.bytes)
                        import_db(tmp)
                        os.remove(tmp)
                    elif hasattr(f, 'path') and f.path:
                        import_db(f.path)
                    show_snack("Base de datos importada. Recargando...")
                    navigate("home")
            except ValueError as exc:
                show_snack(str(exc), DANGER)
            except Exception as exc:
                show_snack(f"Error al importar: {exc}", DANGER)

        def navigate(route, *args):
            page.controls.clear()
            content = None
            if route == "home":
                content = home_view(page, navigate, do_export, do_import)
            elif route == "detail":
                hive_id = args[0]
                content = hive_detail_view(page, hive_id, navigate)
            elif route == "edit_hive":
                hive_id = args[0]
                content = edit_hive_view(page, hive_id, navigate)
            elif route == "add_visit":
                hive_id = args[0]
                content = visit_form_view(page, hive_id, navigate)
            elif route == "edit_visit":
                hive_id = args[0]
                visit_id = args[1]
                content = visit_form_view(page, hive_id, navigate, visit_id)
            page.controls.append(ft.SafeArea(content=content, expand=True))
            page.update()

        navigate("home")

    except Exception:
        err = traceback.format_exc()
        print(f"BERNY ERROR: {err}")
        page.controls.clear()
        page.add(
            ft.SafeArea(
                content=ft.Column([
                    ft.Text("Error al iniciar Berny", size=18, weight=ft.FontWeight.BOLD, color="#EF4444"),
                    ft.Container(height=10),
                    ft.Text(err, size=11, selectable=True, color="#1C1917"),
                ], scroll=ft.ScrollMode.AUTO, expand=True),
                expand=True,
            )
        )


ft.run(main)
