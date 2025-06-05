import os
import configparser
from typing import Any, Optional, Union



class ConfigReader:
    """增强版配置读取工具类，支持环境变量覆盖"""

    def __init__(self, config_file: str = 'config.ini', env_prefix: str = None):
        """
        初始化配置读取器
        :param config_file: 配置文件路径，默认为 config.ini
        :param env_prefix: 环境变量前缀（如 'APP_'）
        """
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.env_prefix = env_prefix
        self.load_config()

    def load_config(self) -> None:
        """加载配置文件"""
        try:
            self.config.read(self.config_file, encoding='utf-8')
        except Exception as e:
            raise ConfigError(f"Failed to load config file: {e}")

    def _get_env_name(self, section: str, option: str) -> str:
        """生成环境变量名"""
        if not self.env_prefix:
            return None

        # 转换格式：如将 [database] user_name 转为 APP_DATABASE_USER_NAME
        section_part = section.upper()
        option_part = option.upper()
        return f"{self.env_prefix}{section_part}_{option_part}"

    def get(self, section: str, option: str,
            default: Any = None, required: bool = False) -> Any:
        """
        获取配置值（优先从环境变量读取）
        :param section: 配置节
        :param option: 配置项
        :param default: 默认值（当配置不存在时返回）
        :param required: 是否为必填项（为True时如果不存在会抛出异常）
        :return: 配置值
        """
        # 1. 首先尝试从环境变量获取
        env_name = self._get_env_name(section, option)
        if env_name and env_name in os.environ:
            return os.environ[env_name]

        # 2. 从配置文件获取
        try:
            if not self.config.has_section(section):
                if required:
                    raise ConfigError(f"Section '{section}' not found in config file")
                return default

            if not self.config.has_option(section, option):
                if required:
                    raise ConfigError(f"Option '{option}' not found in section '{section}'")
                return default

            return self.config.get(section, option)
        except Exception as e:
            if required:
                raise ConfigError(f"Error reading config: {e}")
            return default

        def get_int(self, section: str, option: str,
                    default: int = None, required: bool = False) -> int:
            """获取整数型配置"""
        value = self.get(section, option, default, required)
        if value is None:
            return None
        try:
            return int(value)
        except ValueError:
            if required:
                raise ConfigError(f"Option '{option}' in section '{section}' must be an integer")
            return default

    def get_float(self, section: str, option: str,
                  default: float = None, required: bool = False) -> float:
        """获取浮点型配置"""
        value = self.get(section, option, default, required)
        if value is None:
            return None
        try:
            return float(value)
        except ValueError:
            if required:
                raise ConfigError(f"Option '{option}' in section '{section}' must be a float")
            return default

    def get_boolean(self, section: str, option: str,
                    default: bool = None, required: bool = False) -> bool:
        """获取布尔型配置"""
        value = self.get(section, option, default, required)
        if value is None:
            return None
        if isinstance(value, bool):
            return value
        if value.lower() in ('true', 'yes', '1'):
            return True
        elif value.lower() in ('false', 'no', '0'):
            return False
        else:
            if required:
                raise ConfigError(f"Option '{option}' in section '{section}' must be a boolean")
            return default


class ConfigError(Exception):
    """配置异常类"""
    pass