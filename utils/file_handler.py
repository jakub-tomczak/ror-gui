from tkinter.filedialog import askopenfilename
from typing import Tuple
from ror.data_loader import LoaderResult, read_dataset_from_txt
from os import path


def get_file() -> str:
    initial_path = path.abspath(path.dirname(__file__))
    return askopenfilename(filetypes=[('ROR files', '*.txt')], initialdir=initial_path)


def open_file(filename: str) -> LoaderResult:
    return read_dataset_from_txt(filename)
