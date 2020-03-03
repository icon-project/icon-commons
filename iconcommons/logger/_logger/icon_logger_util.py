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
from datetime import time
from enum import Flag
from logging import Logger as builtinLogger, FileHandler, StreamHandler, Formatter, Handler
from typing import Union

from .icon_period_and_bytes_file_handler import IconPeriodAndBytesFileHandler
from .icon_rotating_file_handler import IconRotatingFileHandler
from .icon_time_rotating_file_handler import IconTimeRotatingFileHandler

import re
weekly_p = re.compile("^weekly[0-6]$")


class OutputType(Flag):
    NONE = 0
    CONSOLE = 1
    FILE = 2


class RotateType(Flag):
    NONE = 0
    PERIOD = 1
    BYTES = 2
    BOTH = PERIOD | BYTES


class RotateConfig:
    def __init__(self,
                 rotate_type: 'RotateType',
                 period: str,
                 at_time: 'time',
                 interval: int,
                 max_bytes: int,
                 backup_count: int):
        self.rotate_type: 'RotateType' = rotate_type
        self.period: str = period
        self.at_time: 'time' = at_time
        self.interval: int = interval
        self.max_bytes: int = max_bytes
        self.backup_count: int = backup_count

    @classmethod
    def from_dict(cls, src_config: dict):
        config: dict = src_config.get('rotate')
        if config is None:
            return

        rotate_type: 'RotateType' = RotateType.NONE

        rotate_types: str = config.get('type')
        if rotate_types:
            rotates = rotate_types.split('|')
            for rotate in rotates:
                rotate_type |= RotateType[rotate.upper()]

        period: str = cls._convert_period(config.get('period', "daily"))
        at_time: 'time' = cls._convert_at_time(config.get("atTime", 0))
        interval: int = config.get('interval')
        max_bytes: int = config.get('maxBytes')
        backup_count: int = config.get("backupCount")

        return RotateConfig(rotate_type=rotate_type,
                            period=period,
                            at_time=at_time,
                            interval=interval,
                            max_bytes=max_bytes,
                            backup_count=backup_count)

    @classmethod
    def _convert_at_time(cls, value: int) -> 'time':
        return time(hour=value)

    @classmethod
    def _convert_period(cls, value: str):
        if value == 'daily':
            return 'D'
        elif value == 'hourly':
            return 'H'
        elif value == 'minutely':
            return 'M'
        elif value == 'secondly':
            return 'S'
        elif value == 'midnight':
            return 'MIDNIGHT'
        elif weekly_p.match(value):
            d_index = value[-1]
            return f'W{d_index}'
        else:
            raise ValueError("Invalid period")


class LogConfig:
    DEFAULT_FORMAT = "%(asctime)s %(process)d %(thread)d %(levelname)s %(filename)s(%(lineno)d) %(message)s"

    def __init__(self,
                 name: str,
                 level: str,
                 file_path: str,
                 fmt: str,
                 output_type: 'OutputType',
                 rotate_config: 'RotateConfig'):

        self.name: str = name
        self.level: str = level
        self.file_path: str = file_path
        self.fmt: str = fmt
        self.output_type: 'OutputType' = output_type
        self.rotate_config: 'RotateConfig' = rotate_config

    @classmethod
    def from_dict(cls, src_config: dict):
        config: dict = src_config.get('log')
        if config is None:
            return

        name: str = config.get('name', "ICONLogger")
        level: str = config.get('level', 'info').upper()
        file_path: str = config.get('filePath', "")
        fmt: str = config.get('format', cls.DEFAULT_FORMAT)
        output_type: 'OutputType' = OutputType.NONE

        output_types: str = config.get('outputType')
        if output_types:
            outputs = output_types.split('|')
            for output in outputs:
                output_type |= OutputType[output.upper()]

        rotate_config: 'RotateConfig' = RotateConfig.from_dict(config)
        return LogConfig(name, level, file_path, fmt, output_type, rotate_config)


class IconLoggerUtil(object):
    _formatter: 'Formatter' = None

    @classmethod
    def apply_config(cls, logger: 'builtinLogger', config: dict) -> None:
        log_config: 'LogConfig' = LogConfig.from_dict(config)

        logger.handlers.clear()
        logger.name = log_config.name
        logger.setLevel(log_config.level)
        cls._apply_config(logger, log_config)

    @classmethod
    def print_config(cls, logger: 'builtinLogger', config: dict):
        logger.info(f'====================LOG CONFIG START====================')
        cls._view_config_info(logger, config, "CONFIG")
        logger.info(f'====================LOG CONFIG END======================')

    @classmethod
    def _view_config_info(cls, logger: 'builtinLogger', conf: dict, prefix: str):
        for key, value in conf.items():
            if not isinstance(value, dict):
                tmp_prefix = '{}.{}'.format(prefix, key)
                logger.info(f'[{tmp_prefix}] > {value}')
            else:
                tmp_prefix = '{}.{}'.format(prefix, key)
                cls._view_config_info(logger, value, tmp_prefix)

    @classmethod
    def _apply_config(cls, logger: 'builtinLogger', log_config: 'LogConfig'):
        cls._formatter = Formatter(log_config.fmt)

        if cls._is_flag_on(log_config.output_type, OutputType.CONSOLE):
            handler = StreamHandler()
            handler.setFormatter(cls._formatter)
            logger.addHandler(handler)

        if cls._is_flag_on(log_config.output_type, OutputType.FILE):
            cls._ensure_dir(log_config.file_path)

            if log_config.rotate_config is None:
                handler = cls.make_file_handler(log_config.file_path, cls._formatter)
                logger.addHandler(handler)
            else:
                rotate_type: 'Flag' = log_config.rotate_config.rotate_type
                if cls._is_flag_on(rotate_type, RotateType.BOTH):
                    handler = cls.make_period_and_bytes_file_handler(log_config.file_path,
                                                                     log_config.rotate_config.period,
                                                                     log_config.rotate_config.interval,
                                                                     log_config.rotate_config.max_bytes,
                                                                     log_config.rotate_config.backup_count,
                                                                     log_config.rotate_config.at_time)
                    logger.addHandler(handler)
                elif cls._is_flag_on(rotate_type, RotateType.PERIOD):
                    handler = cls.make_period_file_handler(log_config.file_path,
                                                           log_config.rotate_config.period,
                                                           log_config.rotate_config.interval,
                                                           log_config.rotate_config.backup_count,
                                                           log_config.rotate_config.at_time)
                    logger.addHandler(handler)
                elif cls._is_flag_on(rotate_type, RotateType.BYTES):
                    handler = cls.make_bytes_file_handler(log_config.file_path,
                                                          log_config.rotate_config.max_bytes,
                                                          log_config.rotate_config.backup_count)
                    logger.addHandler(handler)

    @classmethod
    def _is_flag_on(cls, src_flag: 'Flag', dest_flag: 'Flag') -> bool:
        return src_flag & dest_flag == dest_flag

    @classmethod
    def _make_exc_log_path(cls, src_path: str) -> str:
        if src_path.endswith(".log"):
            converted = src_path[:-4] + "_exc.log"
        else:
            converted = src_path + "_exc"
        return converted

    @classmethod
    def _ensure_dir(cls, file_path: str):
        directory = os.path.dirname(os.path.abspath(file_path))
        os.makedirs(directory, exist_ok=True)

    @classmethod
    def make_log_msg(cls, tag: str, msg: Union[str, BaseException]):
        return f'{tag} {msg}'

    @classmethod
    def make_file_handler(cls,
                          file_path: str,
                          formatter: 'Formatter') -> 'Handler':
        handler = FileHandler(file_path, 'a')
        handler.setFormatter(formatter)
        return handler

    @classmethod
    def make_period_and_bytes_file_handler(cls,
                                           file_path: str,
                                           when: str,
                                           interval: int,
                                           max_bytes: int,
                                           backup_count: int,
                                           at_time: 'time') -> 'Handler':
        handler = IconPeriodAndBytesFileHandler(file_path,
                                                maxBytes=max_bytes,
                                                when=when,
                                                interval=interval,
                                                backupCount=backup_count,
                                                atTime=at_time)
        handler.setFormatter(cls._formatter)
        return handler

    @classmethod
    def make_period_file_handler(cls,
                                 file_path: str,
                                 when: str,
                                 interval: int,
                                 backup_count: int,
                                 at_time: 'time') -> 'Handler':
        handler = IconTimeRotatingFileHandler(file_path,
                                              when=when,
                                              interval=interval,
                                              backupCount=backup_count,
                                              atTime=at_time)
        handler.setFormatter(cls._formatter)
        return handler

    @classmethod
    def make_bytes_file_handler(cls,
                                file_path: str,
                                max_bytes: int,
                                backup_count: int) -> 'Handler':
        handler = IconRotatingFileHandler(file_path,
                                          maxBytes=max_bytes,
                                          backupCount=backup_count)
        handler.setFormatter(cls._formatter)
        return handler


icon_logger = builtinLogger("ICONLogger")
