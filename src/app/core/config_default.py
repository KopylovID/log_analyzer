config = {
    'REPORT_SIZE': 1000,
    'REPORT_DIR': './reports',
    'REPORT_NAME_TEMPLATE': 'report-${report_date}.html',
    'REPORT_TEMPLATE_PATH': './template/report.html',
    'LOG_DIR': './logs',
    'LOG_NAME_TEMPLATE': r'nginx-access-ui\.log-(?P<log_date>\d{4})(\d{2})(\d{2})(\.gz){0,1}',
    'LOG_ERROR_THRESHOLD': 50,
}

logger_config = {
    'version': 1,
    'formatters': {'simple': {'format': '%(asctime)s::%(name)s::%(levelname)s::%(message)s'}},
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'level': 'DEBUG', 'formatter': 'simple'},
        'file_handler': {
            'class': 'logging.FileHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
            'filename': './app-logs/app.log',
            'mode': 'w',
        },
    },
    'root': {'level': 'DEBUG', 'handlers': ['console', 'file_handler']},
}
