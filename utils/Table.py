from tkinter import ttk
from typing import List
from ror.Dataset import Dataset
import tksheet
import numpy as np


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

    def remove_data(self, data: Dataset):
        for id in range(len(data.criteria)+1):
            self.delete_column_position(id)
        for id in range(len(data.alternatives)):
            self.delete_row_position(id)


    def set_data(self, data: Dataset):
        headers = ["id"]
        headers.extend([criterion_name for (criterion_name, _) in data.criteria])
        self.headers(newheaders=headers)
        ids = [[alternative] for alternative in data.alternatives]
        data_with_alternative_names = np.hstack([ids, data.matrix])
        self.set_sheet_data(data_with_alternative_names.tolist())