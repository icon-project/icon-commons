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
import os
import unittest

from iconcommons.icon_config import IconConfig
from iconcommons.logger import icon_logger, IconLoggerUtil, Logger

TAG = 'logger'

default_icon_config = {
    "log": {
        "logger": "iconservice",
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
        conf = IconConfig(str(), default_icon_config)
        conf.load()
        IconLoggerUtil.apply_config(icon_logger, conf)
        IconLoggerUtil.print_config(icon_logger, conf)

        file_path = os.path.join(os.path.dirname(__file__), 'logger.json')
        conf = IconConfig(file_path, default_icon_config)
        conf.load()
        IconLoggerUtil.apply_config(icon_logger, conf)
        IconLoggerUtil.print_config(icon_logger, conf)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_debug(self):
        icon_logger.debug(IconLoggerUtil.make_log_msg(TAG, 'debug log'))

    def test_info(self):
        icon_logger.info(IconLoggerUtil.make_log_msg(TAG, 'info log'))

    def test_warning(self):
        icon_logger.warning(IconLoggerUtil.make_log_msg(TAG, 'warning log'))

    def test_exception(self):
        try:
            raise Exception()
        except:
            icon_logger.exception(IconLoggerUtil.make_log_msg(TAG, 'exception log'))

    def test_error(self):
        icon_logger.error(IconLoggerUtil.make_log_msg(TAG, 'error log'))

    def test_many_debug(self):
        for i in range(100):
            icon_logger.debug(IconLoggerUtil.make_log_msg(TAG, f'debug log{i}'))


class TestLoggerOld(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conf = IconConfig(str(), default_icon_config)
        conf.load()
        Logger.load_config(conf)
        Logger.print_config(conf, TAG)

        file_path = os.path.join(os.path.dirname(__file__), 'logger.json')
        conf = IconConfig(file_path, default_icon_config)
        conf.load()
        Logger.load_config(conf)
        Logger.print_config(conf, TAG)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_debug(self):
        Logger.debug(TAG, 'debug log')

    def test_info(self):
        Logger.info(TAG, 'info log')

    def test_warning(self):
        Logger.warning(TAG, 'warning log')

    def test_exception(self):
        try:
            raise Exception()
        except:
            Logger.exception(TAG, 'exception log')

    def test_error(self):
        Logger.error(TAG, 'error log')

    def test_many_debug(self):
        for i in range(100):
            Logger.debug(TAG, f'debug log{i}')


if __name__ == '__main__':
    unittest.main()
