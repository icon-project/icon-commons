# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
import coloredlogs

from logging import Logger as BuiltinLogger, FileHandler
from enum import IntFlag
from typing import Union, Optional

from iconcommons.icon_config import IconConfig
from .icon_period_and_bytes_file_handler import IconPeriodAndBytesFileHandler
from .icon_period_file_handler import IconPeriodFileHandler
from .icon_bytes_file_handler import IconBytesFileHandler


default_log_config = {
    "log": {
        "format": "[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s",
        "outputType": "console"
    }
}


class Logger:
    _logger_mapper = {}

    class LogLevel(IntFlag):
        NOTSET = 0
        DEBUG = 10
        INFO = 20
        WARNING = 30
        ERROR = 40
        CRITICAL = 50

    class LogHandlerType(IntFlag):
        NONE = 0
        CONSOLE = 1
        FILE = 2

    class LogRotateType(IntFlag):
        NONE = 0
        PERIOD = 1
        BYTES = 2
        BOTH = PERIOD | BYTES

    CATEGORY = 'log'
    LOGGER_NAME = 'logger'
    OUTPUT_TYPE = 'outputType'
    FILE_PATH = 'filePath'
    FORMAT = 'format'
    LEVEL = 'level'
    COLOR = 'colorLog'
    ROTATE = 'rotate'
    ROTATE_TYPE = 'type'
    ROTATE_PERIOD = 'period'
    ROTATE_INTERVAL = 'interval'
    ROTATE_MAX_BYTES = 'maxBytes'
    ROTATE_BACKUP_COUNT = 'backupCount'

    DEFAULT_LOG_TAG = "LOG"

    DEFAULT_LOGGER = 'default_logger'
    EXC_CONSOLE_LOGGER = 'exc_console_logger'
    EXC_FILE_LOGGER = 'exc_file_logger'

    @staticmethod
    def load_config(config: 'IconConfig' = None, config_path: Optional[str] = None) -> None:
        if config is None:
            conf = IconConfig(config_path, default_log_config)
        else:
            conf = IconConfig("", default_log_config)
            conf.update_conf(config)
        log_conf = conf[Logger.CATEGORY]

        Logger._init_logger(log_conf[Logger.LOGGER_NAME])
        Logger._update_logger(log_conf)

    @staticmethod
    def print_config(conf: dict, tag: str = DEFAULT_LOG_TAG):
        Logger.info(f'====================LOG CONFIG====================', tag)
        Logger._print_config(conf, "CONFIG", tag)
        Logger.info(f'====================LOG CONFIG====================', tag)

    @staticmethod
    def get_logger_level(logger_name: str) -> str:
        logger = logging.getLogger(logger_name)
        return logging.getLevelName(logger.level)

    @staticmethod
    def _print_config(conf: dict, prefix: str, tag: str):
        for key, value in conf.items():
            if not isinstance(value, dict):
                tmp_prefix = '{}.{}'.format(prefix, key)
                Logger.info(f'[{tmp_prefix}] > {value}', tag)
            else:
                tmp_prefix = '{}.{}'.format(prefix, key)
                Logger._print_config(value, tmp_prefix, tag)

    @staticmethod
    def _update_logger(conf: dict):
        Logger._clear_logger_handler()
        Logger._apply_conf(conf)

    @staticmethod
    def _init_logger(logger_name: str):
        Logger._logger_mapper.clear()
        Logger._register_logger_mapper(logger_name, Logger.DEFAULT_LOGGER)
        Logger._register_logger_mapper(logger_name + 'exc_file', Logger.EXC_FILE_LOGGER)
        Logger._register_logger_mapper(logger_name + 'exc_console', Logger.EXC_CONSOLE_LOGGER)

    @staticmethod
    def _register_logger_mapper(logger_name: str, logger_type: str):
        logger = logging.getLogger(logger_name)
        Logger._logger_mapper[logger_type] = logger

    @staticmethod
    def _clear_logger_handler():
        for logger in Logger._logger_mapper.values():
            for handler in logger.handlers[:]:
                logger.removeHandler(handler)
            logger.setLevel(Logger.LogLevel.CRITICAL)

    @staticmethod
    def _apply_conf(conf: dict) -> None:
        log_level = Logger.LogLevel[conf.get(Logger.LEVEL, 'info').upper()]
        formatter = logging.Formatter(conf[Logger.FORMAT])
        enable_color = conf.get(Logger.COLOR, False)
        log_file_path = conf.get(Logger.FILE_PATH, str())

        handler_type = Logger.LogHandlerType.NONE
        output_type: str = conf.get(Logger.OUTPUT_TYPE, 'console')
        outputs = output_type.split('|')
        for output in outputs:
            handler_type |= Logger.LogHandlerType[output.upper()]

        if Logger._is_flag_on(handler_type, Logger.LogHandlerType.CONSOLE):
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            Logger._apply_console_logger(Logger.DEFAULT_LOGGER, handler, enable_color, formatter, log_level)
            Logger._apply_console_logger(Logger.EXC_CONSOLE_LOGGER, handler, enable_color, formatter, log_level)

        if Logger._is_flag_on(handler_type, Logger.LogHandlerType.FILE):
            rotation_conf: dict = conf.get(Logger.ROTATE)
            if rotation_conf is not None:
                rotate_type = Logger.LogRotateType.NONE
                rotate_types: str = rotation_conf[Logger.ROTATE_TYPE]
                outputs = rotate_types.split('|')
                for output in outputs:
                    rotate_type |= Logger.LogRotateType[output.upper()]

                if Logger._is_flag_on(rotate_type, Logger.LogRotateType.BOTH):
                    rotate_period = Logger._convert_interval_key(rotation_conf[Logger.ROTATE_PERIOD])
                    rotate_interval = rotation_conf[Logger.ROTATE_INTERVAL]
                    rotate_max_bytes = rotation_conf[Logger.ROTATE_MAX_BYTES]
                    backup_count = rotation_conf[Logger.ROTATE_BACKUP_COUNT]

                    Logger._apply_icon_rotate_file_logger(
                        Logger.DEFAULT_LOGGER, log_file_path, rotate_period, rotate_interval,
                        rotate_max_bytes, backup_count, formatter, log_level)
                    Logger._apply_icon_rotate_file_logger(
                        Logger.EXC_FILE_LOGGER, log_file_path, rotate_period, rotate_interval,
                        rotate_max_bytes, backup_count, formatter, log_level)
                elif Logger._is_flag_on(rotate_type, Logger.LogRotateType.PERIOD):
                    rotate_period = Logger._convert_interval_key(rotation_conf[Logger.ROTATE_PERIOD])
                    rotate_interval = rotation_conf[Logger.ROTATE_INTERVAL]
                    backup_count = rotation_conf[Logger.ROTATE_BACKUP_COUNT]

                    Logger._apply_time_rotate_file_logger(
                        Logger.DEFAULT_LOGGER, log_file_path, rotate_period, rotate_interval,
                        backup_count, formatter, log_level)
                    Logger._apply_time_rotate_file_logger(
                        Logger.EXC_FILE_LOGGER, log_file_path, rotate_period, rotate_interval,
                        backup_count, formatter, log_level)
                elif Logger._is_flag_on(rotate_type, Logger.LogRotateType.BYTES):
                    rotate_max_bytes = rotation_conf[Logger.ROTATE_MAX_BYTES]
                    backup_count = rotation_conf[Logger.ROTATE_BACKUP_COUNT]

                    Logger._apply_rotate_file_logger(
                        Logger.DEFAULT_LOGGER, log_file_path, rotate_max_bytes, backup_count, formatter, log_level)
                    Logger._apply_rotate_file_logger(
                        Logger.EXC_FILE_LOGGER, log_file_path, rotate_max_bytes, backup_count, formatter, log_level)
            else:
                Logger._apply_file_logger(Logger.DEFAULT_LOGGER, log_file_path, formatter, log_level)

    @staticmethod
    def _is_flag_on(src_flag: int, dest_flag: int) -> bool:
        return src_flag & dest_flag == dest_flag

    @staticmethod
    def _apply_console_logger(logger_type: str,
                              handler: 'logging.Handler',
                              enable_color: bool,
                              fmt: 'logging.Formatter',
                              level: str) -> None:
        logger = Logger._logger_mapper[logger_type]
        logger.addHandler(handler)
        logger.setLevel(level)
        if enable_color:
            Logger._update_log_color_set(fmt, level, logger)

    @staticmethod
    def _apply_file_logger(logger_type: str,
                           file_path: str,
                           fmt: 'logging.Formatter',
                           level: str) -> None:
        file_path = Logger._make_log_path(logger_type, file_path)
        Logger._ensure_dir(file_path)
        handler = FileHandler(file_path, 'a')
        handler.setFormatter(fmt)
        logger = Logger._logger_mapper[logger_type]
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def _apply_icon_rotate_file_logger(logger_type: str,
                                       file_path: str,
                                       when: str,
                                       interval: int,
                                       max_bytes: int,
                                       backup_count: int,
                                       fmt: 'logging.Formatter',
                                       level: str):
        file_path = Logger._make_log_path(logger_type, file_path)
        Logger._ensure_dir(file_path)
        handler = IconPeriodAndBytesFileHandler(file_path, maxBytes=max_bytes,
                                                when=when, interval=interval,
                                                backupCount=backup_count)
        handler.setFormatter(fmt)
        logger = Logger._logger_mapper[logger_type]
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def _apply_time_rotate_file_logger(logger_type: str,
                                       file_path: str,
                                       when: str,
                                       interval: int,
                                       backup_count: int,
                                       fmt: 'logging.Formatter',
                                       level: str):
        file_path = Logger._make_log_path(logger_type, file_path)
        Logger._ensure_dir(file_path)
        handler = IconPeriodFileHandler(file_path, when=when, interval=interval, backupCount=backup_count)
        handler.setFormatter(fmt)
        logger = Logger._logger_mapper[logger_type]
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def _apply_rotate_file_logger(logger_type: str,
                                  file_path: str,
                                  max_bytes: int,
                                  backup_count: int,
                                  fmt: 'logging.Formatter',
                                  level: str):
        file_path = Logger._make_log_path(logger_type, file_path)
        Logger._ensure_dir(file_path)
        handler = IconBytesFileHandler(file_path, maxBytes=max_bytes, backupCount=backup_count)
        handler.setFormatter(fmt)
        logger = Logger._logger_mapper[logger_type]
        logger.addHandler(handler)
        logger.setLevel(level)

    @staticmethod
    def _make_log_path(logger_type: str, src_path: str) -> str:
        if logger_type == Logger.DEFAULT_LOGGER:
            return src_path
        else:
            src_filename = src_path.rpartition('/')[-1]
            converted_path = src_path.replace(src_filename, "exc/" + src_filename)
            return converted_path

    @staticmethod
    def _update_log_color_set(log_format: 'logging.Formatter', log_level: str, logger: 'BuiltinLogger'):
        coloredlogs.DEFAULT_FIELD_STYLES = {
            'hostname': {'color': 'magenta'},
            'programname': {'color': 'cyan'},
            'name': {'color': 'blue'},
            'levelname': {'color': 'black', 'bold': True},
            'asctime': {'color': 'magenta'}}

        coloredlogs.DEFAULT_LEVEL_STYLES = {
            'info': {'color': 'green'},
            'notice': {'color': 'magenta'},
            'verbose': {'color': 'blue'},
            'success': {'color': 'green', 'bold': True},
            'spam': {'color': 'cyan'},
            'critical': {'color': 'red', 'bold': True},
            'error': {'color': 'red'},
            'debug': {'color': 'white'},
            'warning': {'color': 'yellow'}}

        coloredlogs.install(logger=logger,
                            fmt=log_format._fmt,
                            datefmt="%m-%d %H:%M:%S",
                            level=log_level,
                            milliseconds=True)

    @staticmethod
    def _ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def debug(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logger = Logger._logger_mapper.get(Logger.DEFAULT_LOGGER)
        if logger is None:
            logging.debug(Logger._make_log_msg(msg, tag))
        else:
            logger.debug(Logger._make_log_msg(msg, tag))

    @staticmethod
    def info(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logger = Logger._logger_mapper.get(Logger.DEFAULT_LOGGER)
        if logger is None:
            logging.info(Logger._make_log_msg(msg, tag))
        else:
            logger.info(Logger._make_log_msg(msg, tag))

    @staticmethod
    def warning(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logger = Logger._logger_mapper.get(Logger.DEFAULT_LOGGER)
        if logger is None:
            logging.warning(Logger._make_log_msg(msg, tag))
        else:
            logger.warning(Logger._make_log_msg(msg, tag))

    @staticmethod
    def error(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logger = Logger._logger_mapper.get(Logger.DEFAULT_LOGGER)
        if logger is None:
            logging.error(Logger._make_log_msg(msg, tag))
        else:
            logger.error(Logger._make_log_msg(msg, tag))

    @staticmethod
    def exception(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        console_logger = Logger._logger_mapper.get(Logger.EXC_CONSOLE_LOGGER)
        file_logger = Logger._logger_mapper.get(Logger.EXC_FILE_LOGGER)

        is_root_enable = True
        if console_logger is not None:
            console_logger.exception(Logger._make_log_msg(msg, tag), exc_info=True)
            is_root_enable = False
        if file_logger is not None:
            file_logger.exception(Logger._make_log_msg(msg, tag), exc_info=True)
            is_root_enable = False
        if is_root_enable:
            logging.exception(Logger._make_log_msg(msg, tag), exc_info=True)

    @staticmethod
    def _make_log_msg(msg: Union[str, BaseException], tag: str):
        return f'[{tag}] {msg}'

    @staticmethod
    def _convert_interval_key(config_key: str):
        if config_key == 'daily':
            return 'D'
        elif config_key == 'weekly':
            return 'W'
        elif config_key == 'hourly':
            return 'H'
        elif config_key == 'minutely':
            return 'M'
        else:
            return 'D'
