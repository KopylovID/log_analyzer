from http.client import responses

from .core import Config
from logging import Logger
import os
import re
from pathlib import Path
from typing import Dict
from tqdm import tqdm


class LogAnalizer:
    """Класс предназначенный для анализа журналов ngnix"""

    def __init__(self, config: Config, log: Logger):
        self.config = config
        self.log = log
        self.pattern = self.__get_pattern__()

    def __count_lines__(self, log_path: Path):
        """Оптимальный способ для больших файлов"""
        with open(log_path, 'rb') as f:
            return sum(1 for _ in f)

    def __try_cast_to_float__(value: str, default=0.0):
        if value is None:
            return default

        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def __get_pattern__(self):
        """Возвращает скомпилированный паттерн"""
        return re.compile(
            r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d{3})\s+(?P<size>\d+)\s+"[^"]*"\s+'
            r'.*?'
            r'\s+(?P<response_duration>[\d.]+)$'
        )

    def analize(self):
        self.log.debug('Получаем путь к анализируемому журналу')
        log_path = self.__get_log_path__()
        self.log.debug('Путь к анализируемому журналу', log_path=log_path)

        pattern = self.__get_pattern__()
        analize: Dict = dict()
        file_count_lines = self.__count_lines__(log_path)

        # count    # сколько раз встречается URL, абсолютное значение
        # count_perc# сколько раз встречается URL, в процентнах относительно общего числа запросов
        # time_sum # суммарный $request_time для данного URL'а, абсолютное значение
        # time_perc # суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов
        # time_avg # средний $request_time для данного URL'а
        # time_max # максимальный $request_time для данного URL'а
        # time_med # медиана $request_time для данного URL'а

        response_amount = 0
        with tqdm(total=file_count_lines) as pbar:
            for line in self.__read_file__(log_path):
                response_amount += 1
                result = pattern.match(line.strip())
                if result:
                    data = result.groupdict()

                    url = data.get('url', '')
                    response_duration = data.get('response_duration')
                    if url not in analize:
                        analize[url] = {
                            'request_time_list': []
                        }
                    analize[url]['request_time_list'].append(self.__try_cast_to_float__(response_duration))
                    pbar.update(1)




    def __read_file__(self, log_path: Path):

        try:
            with open(log_path, 'r', encoding='UTF-8') as file:
                for line in file:
                    yield line.rstrip('\n')
        except FileNotFoundError:
            print(f"Файл '{log_path.name}' не найден")
        except Exception as e:
            print(f'Ошибка при чтении файла: {e}')

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
