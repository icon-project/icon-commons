# Copyright [theloop]
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

from logging import Logger as BuiltinLogger
from logging.handlers import TimedRotatingFileHandler
from enum import IntFlag
from typing import Union

from iconcommons.icon_config import IconConfig


default_log_config = {
    "log": {
        "format": "%(asctime)s %(levelname)s %(message)s",
        "colorLog": True,
        "level": "debug",
        "filePath": "./logger.log",
        "outputType": "console|file|daily"
    }
}


class Logger:
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
        DAILY = 4

    CATEGORY = 'log'
    OUTPUT_TYPE = 'outputType'
    FILE_PATH = 'filePath'
    FORMAT = 'format'
    LEVEL = 'level'
    COLOR = 'colorLog'
    DEFAULT_LOG_TAG = "LOG"

    @staticmethod
    def load_config(config: 'IconConfig' = None, config_path: str = None):
        if config is None:
            conf = IconConfig(config_path, default_log_config)
        else:
            conf = config

        conf = conf[Logger.CATEGORY]
        Logger._update_logger(conf)

        Logger._update_other_logger_level('pika', Logger.LogLevel.WARNING.value)
        Logger._update_other_logger_level('aio_pika', Logger.LogLevel.WARNING.value)
        Logger._update_other_logger_level('sanic.access', Logger.LogLevel.WARNING.value)
        Logger._update_other_logger_level('jsonrpcclient.client.request', Logger.LogLevel.WARNING.value)
        Logger._update_other_logger_level('jsonrpcclient.client.response', Logger.LogLevel.WARNING.value)

    @staticmethod
    def _update_logger(conf: 'IconConfig', logger: 'BuiltinLogger'=None):
        if logger is None:
            logger = logging.root

        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        log_level = Logger.LogLevel[conf[Logger.LEVEL].upper()]
        if logger is logging.root:
            handlers = Logger._make_handler(conf)
            log_format = conf.get(Logger.FORMAT, default_log_config[Logger.CATEGORY][Logger.FORMAT])

            logging.basicConfig(handlers= handlers,
                                format=log_format,
                                datefmt="%m-%d %H:%M:%S",
                                level=log_level)

            log_color = conf[Logger.COLOR]
            if log_color:
                Logger._update_log_color_set(log_format, log_level, logger)
        else:
            logger.setLevel(log_level)

    @staticmethod
    def _make_handler(conf: 'IconConfig') -> []:
        handlers = []

        handler_type = Logger.LogHandlerType.NONE
        log_file_path = conf[Logger.FILE_PATH]
        output_type: str = conf[Logger.OUTPUT_TYPE]
        outputs = output_type.split('|')
        for output in outputs:
            handler_type |= Logger.LogHandlerType[output.upper()]
        if handler_type & Logger.LogHandlerType.CONSOLE:
            handlers.append(logging.StreamHandler())

        if handler_type & Logger.LogHandlerType.FILE:
            Logger._ensure_dir(log_file_path)
            handlers.append(
                logging.FileHandler(log_file_path, 'w', 'utf-8'))

        if handler_type & Logger.LogHandlerType.DAILY:
            Logger._ensure_dir(log_file_path)
            handlers.append(
                TimedRotatingFileHandler(log_file_path, when='D'))

        return handlers

    @staticmethod
    def _update_log_color_set(log_format: str, log_level: str, logger: 'BuiltinLogger'):
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
                            fmt=log_format,
                            datefmt="%m-%d %H:%M:%S",
                            level=log_level,
                            milliseconds=True)

    @staticmethod
    def _update_other_logger_level(logger_name: str, log_level: int):
        logger = logging.getLogger(logger_name)
        if logger is not None:
            logger.setLevel(log_level)

    @staticmethod
    def _ensure_dir(file_path):
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    def debug(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logging.debug(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def info(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logging.info(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def warning(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logging.warning(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def error(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logging.error(Logger.__make_log_msg(msg, tag))

    @staticmethod
    def exception(msg: Union[str, BaseException], tag: str = DEFAULT_LOG_TAG):
        logging.exception(Logger.__make_log_msg(msg, tag), exc_info=True)

    @staticmethod
    def __make_log_msg(msg: Union[str, BaseException], tag: str):
        return f'[{tag}] {msg}'
