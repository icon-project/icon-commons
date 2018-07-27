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

    def _load(self, conf_path: str) -> bool:
        if not os.path.exists(conf_path):
            return False
        with open(conf_path) as f:
            conf: dict = json.load(f)
            self.update_conf(conf)
            return True

    def update_conf(self, conf: dict, src_conf: dict= None) -> None:
        if src_conf is None:
            src_conf = self

        for key, value in conf.items():
            if not isinstance(value, dict):
                src_conf[key] = conf[key]
            else:
                src_dict = src_conf.get(key)
                conf_dict = conf.get(key, {})
                if src_dict is None:
                    src_conf[key] = conf_dict
                else:
                    self.update_conf(conf_dict, src_conf[key])
