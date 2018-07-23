#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2017-2018 theloop Inc.
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

from iconcommons.icon_config import IconConfig
from iconcommons.logger import Logger


TAG = 'logger'

default_icon_config = {
    "log": {
        "loggerName": "iconservice",
        "colorLog": True,
        "level": "info",
        "filePath": "./log/iconservice.log",
        "outputType": "console|file"
    },
    "config": './conf/iconservice_config.json',
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
        file_path = os.path.join(os.path.dirname(__file__), 'logger.json')
        conf = IconConfig(file_path, default_icon_config)
        conf.load()
        Logger.load_config(conf, file_path)

    @classmethod
    def tearDownClass(cls):
        pass

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


if __name__ == '__main__':
    unittest.main()
