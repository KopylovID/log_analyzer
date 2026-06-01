from pydantic import DirectoryPath
from pydantic_settings import BaseSettings, SettingsConfigDict

from .config_default import config as config_default


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
    name_template: str = config_default['LOG_NAME_TEMPLATE']
    name_template_arch: str = config_default['LOG_NAME_TEMPLATE_ARCH']


class Config:

    def __init__(self, env_file:str = '.env'):
        self.__env_file: str = env_file
        self.report: ReportConfig = ReportConfig(_env_file=env_file)
        self.log: LogConfig = LogConfig(_env_file=env_file)

    @classmethod
    def load(cls, env_file: str = '.env') -> 'Config':
        return cls(env_file)
