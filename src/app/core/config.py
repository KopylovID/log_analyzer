from pydantic import DirectoryPath, Field
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
    JsonConfigSettingsSource,
)

from .config_default import config as config_default, logger_config
from typing import Optional


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


class LogConfig(ConfigBase):
    model_config = SettingsConfigDict(env_prefix='LOG_', extra='ignore')

    dir: DirectoryPath = config_default['LOG_DIR']
    name: str | None = None
    name_template: str = config_default['LOG_NAME_TEMPLATE']


class Config:
    def __init__(self, env_file: Optional[str] = '.env', **kwargs):
        self.report: ReportConfig = ReportConfig(_env_file=env_file)
        self.log: LogConfig = LogConfig(_env_file=env_file)
        self.logger = logger_config

    @classmethod
    def load(cls, env_file: str = '.env') -> 'Config':
        return cls(env_file)
