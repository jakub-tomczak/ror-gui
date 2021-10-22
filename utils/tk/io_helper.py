from ror.Dataset import RORDataset
from ror.RORParameters import RORParameters
from utils.Severity import Severity
from utils.type_aliases import LoggerFunc
from datetime import datetime


def save_model(dataset: RORDataset, parameters: RORParameters, filename: str, logger: LoggerFunc):
    format = 'txt'
    if dataset is not None:
        # remove extensions (if exist)
        _filename = filename
        splited = filename.split(f'.{format}')
        if splited[-1] == '':
            # there was .txt at the end
            # recreate filename without .txt extension
            _filename = ''.join(splited[:-1])
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
        name = f'{_filename}_{date_time}'
        try:
            dataset.save_to_file(f'{name}.{format}', parameters)
            logger(f'Saved dataset to {name}.{format}')
        except Exception as e:
            logger(f'Failed to save a file: {e}', severity=Severity.ERROR)
            raise e
    else:
        logger('Dataset is empty')
