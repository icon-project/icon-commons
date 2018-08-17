#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import unittest
import os.path

from logging import Logger as builtin_logger

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger
from iconcommons.logger.icon_rotationg_file_handler import IconRotatingFileHandler

TAG = 'logger'

default_icon_config = {
    "log": {
        "logger": "iconservice",
        "colorLog": True,
        "level": "info",
        "filePath": "./log/iconservice.log",
        "outputType": "console|file",
        "rotate": {
            "type": "bytes",
            "backupCount": 10,
            "maxBytes": 10485760
        }
    },
    "scoreRootPath": ".score",
    "stateDbRootPath": ".statedb",
    "channel": "loopchain_default",
    "amqpKey": "7100",
    "amqpTarget": "127.0.0.1",
    "builtinScoreOwner": "hxebf3a409845cd09dcb5af31ed5be5e34e2af9433",
    "service": {
        "fee": False,
        "audit": False
    }
}


class TestLogger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.conf = IconConfig(str(), default_icon_config)
        cls.conf.load()
        Logger.load_config(cls.conf)
        Logger.print_config(cls.conf, 'test')

        file_path = os.path.join(os.path.dirname(__file__), 'logger_old.json')
        cls.conf = IconConfig(file_path, default_icon_config)
        cls.conf.load()
        Logger.load_config(cls.conf, file_path)

        file_path = os.path.join(os.path.dirname(__file__), 'logger.json')
        cls.conf = IconConfig(file_path, default_icon_config)
        cls.conf.load()
        Logger.load_config(cls.conf, file_path)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_get_logger_level(self):
        level_name = Logger.get_logger_level("")
        self.assertEqual(level_name, "WARNING")

    def test_debug(self):
        Logger.debug('debug log')
        Logger.debug('debug log', TAG)

    def test_info(self):
        Logger.info('info log')
        Logger.info('info log', TAG)

    def test_warning(self):
        Logger.warning('warning log')
        Logger.warning('warning log', TAG)

    def test_exception(self):
        Logger.exception('exception log')
        Logger.exception('exception log', TAG)

    def test_error(self):
        Logger.error('error log')
        Logger.error('error log', TAG)

    def test_config(self):
        logger: builtin_logger = Logger._logger_mapper.get(Logger.DEFAULT_LOGGER)
        self.assertEqual(logger.name, self.conf['log']['logger'])
        log_str: str = self.conf['log']['level']
        log_str = log_str.upper()
        self.assertEqual(logger.level, Logger.LogLevel[log_str].value)
        self.assertEqual(2, len(logger.handlers))
        handler = logger.handlers[1]
        if not isinstance(handler, IconRotatingFileHandler):
            raise Exception


if __name__ == '__main__':
    unittest.main()
