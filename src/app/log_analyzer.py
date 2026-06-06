from .core import Config
from logging import Logger
import os
import re
from pathlib import Path
from typing import Dict
from tqdm import tqdm
import statistics
from string import Template


class LogAnalizer:
    """Класс предназначенный для анализа журналов ngnix"""

    def __init__(self, config: Config, log: Logger):
        self.config = config
        self.log = log
        self.pattern = self._get_pattern()

    def _count_lines(self, log_path: Path):
        """Получение общего количества строк в файле"""
        with open(log_path, 'rb') as f:
            return sum(1 for _ in f)

    def _try_cast_to_float(self, value: str, default=0.0):
        """Попытка преобразование во float"""
        if value is None:
            return default

        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _get_pattern(self):
        """Возвращает скомпилированный паттерн для парсинга логов"""
        return re.compile(
            r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<time>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+(?P<protocol>[^"]+)"\s+(?P<status>\d{3})\s+(?P<size>\d+)\s+"[^"]*"\s+'
            r'.*?'
            r'\s+(?P<response_duration>[\d.]+)$'
        )

    def analize(self):
        """Основная процедура запуска парсинга логов"""
        self.log.debug('Получаем путь к анализируемому журналу')
        log_path = self._get_log_path()
        self.log.debug('Путь к анализируемому журналу', log_path=log_path)

        pattern = self._get_pattern()
        analize: Dict = dict()
        file_count_lines = self._count_lines(log_path)

        self.log.debug('Парсинг')
        response_amount = 0
        error_amount = 0
        with tqdm(total=file_count_lines, desc='Парсинг') as pbar:
            for line in self._read_file_lines(log_path):
                response_amount += 1
                result = pattern.match(line.strip())
                if result:
                    data = result.groupdict()

                    url = data.get('url', '')
                    response_duration = data.get('response_duration')
                    if url not in analize:
                        analize[url] = {'request_time_list': []}
                    analize[url]['request_time_list'].append(self._try_cast_to_float(response_duration))
                    pbar.update(1)
                else:
                    error_amount += 1
            else:
                error_prc = int((error_amount * 100) / response_amount)
                if error_prc > self.config.log.error_threshold:
                    raise Exception(
                        f'Превышен допустимый порог {self.config.log.error_threshold} ошибочного парсинга сообщений - {error_prc}!'
                    )

        self.log.debug('Очистка данных')
        result_data = []
        result_json = {
            'url': '',
            'count': 0,  # сколько раз встречается URL, абсолютное значение
            'count_perc': 0.00,  # сколько раз встречается URL, в процентнах относительно общего числа запросов
            'time_sum': 0.00,  # суммарный $request_time для данного URL'а, абсолютное значение
            'time_perc': 0.00,  # суммарный $request_time для данного URL'а, в процентах относительно общего $request_time всех запросов
            'time_avg': 0.00,  # средний $request_time для данного URL'а
            'time_max': 0.00,  # максимальный $request_time для данного URL'а
            'time_med': 0.00,  # медиана $request_time для данного URL'а
        }

        request_amount = len(analize)
        for key, value in tqdm(analize.items(), desc='Расчет показателей'):
            rec = result_json.copy()
            rec['url'] = key
            rec['count'] = len(value['request_time_list'])
            rec['count_perc'] = round(rec['count'] * 100 / request_amount, 2)
            rec['time_sum'] = round(sum(value['request_time_list']), 2)
            rec['time_perc'] = round(sum(value['request_time_list']) * 100 / request_amount, 2)
            rec['time_avg'] = round(statistics.mean(value['request_time_list']), 2)
            rec['time_max'] = round(max(value['request_time_list']), 2)
            rec['time_med'] = round(statistics.median(value['request_time_list']), 2)
            result_data.append(rec)

        result_data_trunc = sorted(result_data, key=lambda rec: rec['time_sum'], reverse=True)[
            : self.config.report.size
        ]

        self.log.debug('Формирование отчета')
        template = Template('\n'.join(list(self._read_file_lines(self.config.report.template_path))))
        report_data = template.safe_substitute(table_json=result_data_trunc)

        match = re.search(self.config.log.name_template, str(log_path))
        report_date = ''.join(match.groups('log_date')[:-1]) if match else ''

        self._write_report(self._get_report_path(report_date), report_data)

    def _read_file_lines(self, log_path: Path):
        """Функиця построчного чтение файла"""
        try:
            with open(log_path, mode='r', encoding='UTF-8') as file:
                for line in file:
                    yield line.rstrip('\n')
        except FileNotFoundError:
            self.log.error('Файл не найден', log_file_name=log_path.name)
        except Exception:
            self.log.error('Ошибка при чтении файла', log_file_name=log_path.name, exc_info=True)

    def _get_report_path(self, report_date: str):
        """Функиця получения пути сохранения отчета"""
        report_dir = Path(self.config.report.dir)
        return report_dir.joinpath(Template(self.config.report.name_template).safe_substitute(report_date=report_date))

    def _write_report(self, report_path: Path, data: str):
        """Функиця записи в файл отчета"""
        try:
            with open(report_path, 'w', encoding='UTF-8') as file:
                file.write(data)
        except FileNotFoundError:
            self.log.error('Файл не найден', log_file_name=report_path.name)
        except Exception:
            self.log.error('Ошибка при чтении файла', log_file_name=report_path.name, exc_info=True)

    def _scan_dir(self, path: str, template: str) -> Dict[str, Path]:
        """Функиця сканирования репозитория логов"""
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

    def _get_log_path(self) -> Path:
        """Функиця поиска актуального журнала"""
        log_path: Path = None

        log_dir_path = Path(self.config.log.dir)
        if self.config.log.name is None:
            file_dict = self._scan_dir(log_dir_path, self.config.log.name_template)
            log_path = file_dict[max(file_dict)]
        else:
            log_path = log_dir_path.joinpath(self.config.log.name)
            log_path = log_path if log_path.is_file() and re.search(self.config.log.name_template) else None

        return log_path
