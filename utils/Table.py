from tkinter import ttk
from typing import List, Tuple, Union
from ror.Dataset import Dataset
from ror.dataset_constants import CRITERION_TYPES
from ror.number_utils import format_number
import tksheet
import pandas as pd


class Table(tksheet.Sheet):
    def __init__(self, parent: ttk.Frame):
        super().__init__(parent)
        self.enable_bindings(
            (
                "single_select",
                "row_select",
                "column_width_resize",
                "arrowkeys",
            )
        )

    def remove_data(self):
        self.destroy()

    def set_data(self, data: Dataset, display_precision: int = 2):
        headers = ["id"]
        headers.extend([criterion_name for (
            criterion_name, _) in data.criteria])
        self.headers(newheaders=headers)
        # round data - numpy.tolist will convert data to float and the precision will be lost
        # therefore we can't use it
        # so we convert data earlier to strings
        data_str = []
        for alternative, row in zip(data.alternatives, data.matrix):
            # add alternative at the first index
            new_row = [alternative]
            # add results on the rest of columns, flip values if column is of cost type (already filpped)
            for (_, criterion_type), value in zip(data.criteria, row):
                if criterion_type == CRITERION_TYPES["cost"]:
                    new_row.append(format_number(-value, display_precision))
                else:
                    new_row.append(format_number(value, display_precision))
            # add new row
            data_str.append(new_row)
        self.set_sheet_data(data_str)

    def set_pandas_data(self, data: pd.DataFrame, display_precision: int = 2, headers=None, indices=None):
        headers: List[str] = list(data.columns) if headers is None else headers
        self.headers(headers)
        rows: List[str] = list(data.index) if indices is None else indices
        data = data.to_numpy()
        
        _data: List[List[str]] = []
        for row_name, row_data in zip(rows, data):
            _new_row = [row_name]
            _new_row.extend([format_number(value, display_precision)
                           for value in row_data])
            _data.append(_new_row)
        self.set_sheet_data(_data)

    def set_alternatives_pandas_data(self, data: pd.DataFrame, display_precision: int = 2):
        headers = ['alternative']
        headers.extend([item[:12] for item in data.columns])
        self.headers(headers)
        numpy_data = data.to_numpy()
        # round data - numpy.tolist will convert data to float and the precision will be lost
        # therefore we can't use it
        # so we convert data earlier to strings
        data_str: List[List[Union[float, str]]] = []
        for alternative, data in zip(list(data.index), numpy_data):
            new_row = [alternative]
            new_row.extend([format_number(value, display_precision)
                           for value in data])
            data_str.append(new_row)
        self.set_sheet_data(data_str)

    def set_simple_data(self, data: List[Tuple[str, str]]):
        self.headers(['parameter name', 'value'])
        self.set_sheet_data(data)
