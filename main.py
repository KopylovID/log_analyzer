import argparse

import structlog
import logging.config

from src.app import Config
from src.app import LogAnalizer
import json

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

def main():

    parser = argparse.ArgumentParser(description='Анализатор журналов NGNIX')
    parser.add_argument('-e', '--env-file', type=str, help='Путь к .env файлу', default='.env')
    args = parser.parse_args()

    config = Config.load(env_file=args.env_file)
    logging.config.dictConfig(config.logger)
    logger: logging.Logger = structlog.get_logger(__name__)

    logger.info('Начало')

    try:

        logger.debug('Запуск сервиса')
        la = LogAnalizer(config, logger)
        la.analize()

    except Exception as exc:
        logger.error(exc, exc_info=True)

    logger.info('Завершение')


if __name__ == '__main__':
    main()

