import flet as ft
from database import init_db
from views.home import home_view
from views.hive_detail import hive_detail_view
from views.edit_hive import edit_hive_view
from views.visit_form import visit_form_view


def main(page: ft.Page):
    page.title = "Berny"
    page.window.width = 400
    page.window.height = 740
    page.bgcolor = "#FAFAF9"
    page.fonts = {
        "default": "Roboto",
    }

    init_db()

    def navigate(route, *args):
        page.views.clear()
        if route == "home":
            page.views.append(home_view(page, navigate))
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


ft.app(target=main)
