from tkinter import ttk
import tksheet


class Table(tksheet.Sheet):
    def __init__(self, parent: ttk.Frame):
        super().__init__(parent, width=500)
        self.enable_bindings(
            (
                "single_select",
                "row_select",
                "column_width_resize",
                "arrowkeys",
                "right_click_popup_menu",
                "rc_select",
                "rc_insert_row",
                "rc_delete_row",
                "copy",
                "cut",
                "paste",
                "delete",
                "undo",
                "edit_cell"
            )
        )


    def set_data(self):
        self.set_sheet_data([[f"{ri+cj}" for cj in range(4)] for ri in range(1)])