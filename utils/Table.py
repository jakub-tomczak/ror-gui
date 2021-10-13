from tkinter import ttk
from typing import List
from ror.Dataset import Dataset
import tksheet
import numpy as np
import pandas as pd


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

    def remove_data(self):
        self.destroy()


    def set_data(self, data: Dataset):
        headers = ["id"]
        headers.extend([criterion_name for (criterion_name, _) in data.criteria])
        self.headers(newheaders=headers)
        ids = [[alternative] for alternative in data.alternatives]
        data_with_alternative_names = np.hstack([ids, data.matrix])
        self.set_sheet_data(data_with_alternative_names.tolist())

    def set_pandas_data(self, data: pd.DataFrame):
        headers=['alternative']
        headers.extend(list(data.columns))
        self.headers(headers)
        numpy_data = data.to_numpy()
        # add alternative names
        ids = [[id] for id in list(data.index)]
        data_with_alternative_names = np.hstack([ids, numpy_data])
        self.set_sheet_data(data_with_alternative_names.tolist())
