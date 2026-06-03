from .core import Config
from logging import Logger
from pydantic import FilePath
from pathlib import Path
import os
import re
from pathlib import Path
from typing import Dict

class LogAnalizer:
    """Класс предназначенный для анализа журналов ngnix"""

    def __init__(self, config: Config, log: Logger):
        self.config = config
        self.log = log

    def analize(self):
        self.log.debug('Получаем путь к анализируемому журналу')
        log_path = self.__get_log_path__()
        self.log.debug('Путь к анализируемому журналу', log_path=log_path)


    def __scan_dir__(self, path: str, template: str) -> Dict[str, Path]:
        result = {}
        regex = re.compile(template)

        try:
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_file() and regex.search(entry.name):
                        result[entry.name] = Path(entry.path)
        except PermissionError:
            pass

        return result

    def __get_log_path__(self) -> Path:

        log_path: Path = None

        log_dir_path = Path(self.config.log.dir)
        if self.config.log.name is None:
            file_dict = self.__scan_dir__(log_dir_path, self.config.log.name_template)
            log_path = file_dict[max(file_dict)]
        else:
            log_path = log_dir_path.joinpath(self.config.log.name)
            log_path = log_path if log_path.is_file() and re.search(self.config.log.name_template) else None

        return log_path





