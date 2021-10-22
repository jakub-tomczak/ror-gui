from ror.Dataset import RORDataset
from ror.RORParameters import RORParameters
from utils.Severity import Severity
from utils.type_aliases import LoggerFunc
from tkinter.filedialog import asksaveasfilename
from tkinter import ttk
from os import path


def save_model(root: ttk.Frame, dataset: RORDataset, parameters: RORParameters, initial_filename: str, logger: LoggerFunc):
    format = 'txt'
    file_basename = path.basename(initial_filename)
    if dataset is not None:
        # ask for filename to save
        _filename = asksaveasfilename(
            parent=root,
            defaultextension=f".{format}",
            initialfile=file_basename,
            title="Save"
        )
        if _filename is None or _filename == '':
            logger('Cancelled file saving')
            return
        if not _filename.endswith(f'.{format}'):
            _filename += f'.{format}'
        try:
            dataset.save_to_file(_filename, parameters)
            logger(f'Saved dataset to {_filename}')
        except Exception as e:
            logger(f'Failed to save a file: {e}', severity=Severity.ERROR)
            raise e
    else:
        logger('Dataset is empty')
