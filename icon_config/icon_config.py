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
import os
import json


class IconConfig(dict):

    def __init__(self, config_path: str, default_config: dict = None):
        super().__init__()

        self._config_path = config_path

        if default_config is not None:
            self.update(default_config)

    def load(self, user_input=None):
        if user_input is None:
            user_input = {}
        for path in [user_input.get('config', ""), self._config_path]:
            if path and self._load(path):
                break

        if user_input:
            self.update({k: v for k, v in user_input.items() if v})

    def _load(self, conf_path: str):
        if not os.path.exists(conf_path):
            return False
        with open(conf_path) as f:
            conf: dict = json.load(f)
            self.update(conf)
            return True
