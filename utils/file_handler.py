from tkinter.filedialog import askopenfilename
from ror.data_loader import read_dataset_from_txt
from ror.Dataset import Dataset
from os import path


def open_file() -> Dataset:
    initial_path = path.abspath(path.dirname(__file__))
    filename = askopenfilename(filetypes=[('ROR files', '*.txt')], initialdir=initial_path)
    return read_dataset_from_txt(filename)