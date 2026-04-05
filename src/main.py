import flet as ft
import traceback


def main(page: ft.Page):
    page.title = "Berny"
    page.bgcolor = "#FAFAF9"

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

        # File pickers only on desktop
        do_export = None
        do_import = None
        snack = ft.SnackBar(ft.Text(""))
        page.overlay.append(snack)

        def show_snack(msg, color=SUCCESS):
            snack.content = ft.Text(msg)
            snack.bgcolor = color
            snack.open = True
            page.update()

        if not is_mobile:
            async def do_export(e):
                try:
                    path = await ft.FilePicker().save_file(
                        dialog_title="Exportar base de datos",
                        file_name="berny_backup.db",
                    )
                    if path:
                        export_db(path)
                        show_snack("Base de datos exportada correctamente")
                except Exception as exc:
                    show_snack(f"Error al exportar: {exc}", DANGER)

            async def do_import(e):
                try:
                    files = await ft.FilePicker().pick_files(
                        dialog_title="Importar base de datos",
                        allow_multiple=False,
                    )
                    if files:
                        src = files[0].path
                        import_db(src)
                        show_snack("Base de datos importada. Recargando...")
                        navigate("home")
                except ValueError as exc:
                    show_snack(str(exc), DANGER)

        def navigate(route, *args):
            page.controls.clear()
            if route == "home":
                page.controls.append(home_view(page, navigate, do_export, do_import))
            elif route == "detail":
                hive_id = args[0]
                page.controls.append(hive_detail_view(page, hive_id, navigate))
            elif route == "edit_hive":
                hive_id = args[0]
                page.controls.append(edit_hive_view(page, hive_id, navigate))
            elif route == "add_visit":
                hive_id = args[0]
                page.controls.append(visit_form_view(page, hive_id, navigate))
            elif route == "edit_visit":
                hive_id = args[0]
                visit_id = args[1]
                page.controls.append(visit_form_view(page, hive_id, navigate, visit_id))
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
