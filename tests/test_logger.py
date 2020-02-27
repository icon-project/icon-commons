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

from iconcommons import Logger, IconConfig


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
    }
}

default_icon_config2 = {
    "log": {
        "logger": "test",
        "level": "debug",
        "filePath": "./log/icon_service.log",
        "outputType": "console|file",
        "rotate": {
            "type": "period|bytes",
            "period": "daily",
            "atTime": 1,
            "interval": 1,
            "maxBytes": 10485760,
            "backupCount": 10
        }
    }
}


class TestLogger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        conf = IconConfig(str(), default_icon_config2)
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
