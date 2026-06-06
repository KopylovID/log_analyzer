from pydantic import DirectoryPath, FilePath
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)
from pathlib import Path

from .config_default import config as config_default, logger_config

BASE_PATH = Path(__file__).resolve().parent


class ConfigBase(BaseSettings):
    model_config = SettingsConfigDict(
        env_file_encoding='UTF-8',
        case_sensitive=False,
    )


class ReportConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='REPORT_', extra='ignore')

    size: int = config_default['REPORT_SIZE']
    dir: DirectoryPath = config_default['REPORT_SIZE']
    name_template: str = config_default['REPORT_NAME_TEMPLATE']
    template_path: FilePath = BASE_PATH.joinpath(config_default['REPORT_TEMPLATE_PATH'])


class LogConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='LOG_', extra='ignore')

    dir: DirectoryPath = config_default['LOG_DIR']
    name: str | None = None
    name_template: str = config_default['LOG_NAME_TEMPLATE']
    error_threshold: int = config_default['LOG_ERROR_THRESHOLD']


class Config:
    def __init__(self, env_file: str | None = '.env', **kwargs):
        self.report: ReportConfig = ReportConfig(_env_file=env_file)
        self.log: LogConfig = LogConfig(_env_file=env_file)
        self.logger = logger_config

    @classmethod
    def load(cls, env_file: str = '.env') -> 'Config':
        return cls(env_file)
