from ror.Dataset import RORDataset
from ror.RORParameters import RORParameters
from ror.RORModel import RORModel
from utils.Severity import Severity
from utils.type_aliases import LoggerFunc
from tkinter.filedialog import asksaveasfilename
from tkinter import ttk
from os import path


def save_model(root: ttk.Frame, dataset: RORDataset, parameters: RORParameters, proposed_filename: str, logger: LoggerFunc):
    format = 'txt'
    file_basename = path.basename(proposed_filename)
    if dataset is not None:
        # ask for filename to save
        _filename = asksaveasfilename(
            parent=root,
            defaultextension=f".{format}",
            initialfile=file_basename,
            title="Save dataset"
        )
        if _filename is None or _filename == '':
            logger('Cancelled file saving')
            return
        if not _filename.endswith(f'.{format}'):
            _filename += f'.{format}'
        try:
            dataset.save_to_file(_filename, parameters)
            logger(f'Saved dataset to {_filename}', Severity.SUCCESS)
        except Exception as e:
            logger(f'Failed to save a file: {e}', severity=Severity.ERROR)
            raise e
    else:
        logger('Dataset is empty', Severity.ERROR)

def save_model_latex(root: ttk.Frame, model: RORModel, parameters: RORParameters, proposed_filename: str, logger: LoggerFunc):
    format = 'tex'
    file_basename = path.basename(proposed_filename)
    if model is not None:
        # ask for filename to save
        _filename = asksaveasfilename(
            parent=root,
            defaultextension=f".{format}",
            initialfile=file_basename,
            title="Save model in latex"
        )
        if _filename is None or _filename == '':
            logger('Cancelled exporting to tex')
            return
        if _filename.endswith(f'.{format}'):
            _filename += f'.{format}'
        try:
            model.export_to_latex(_filename)
            logger(f'Saved latex model to {_filename}', Severity.SUCCESS)
        except Exception as e:
            logger(f'Failed to save model to tex file: {e}', severity=Severity.ERROR)
            raise e
    else:
        logger('Model is empty', Severity.WARNING)