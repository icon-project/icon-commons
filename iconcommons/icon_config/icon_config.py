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
import json


class IconConfig(dict):

    def __init__(self, config_path: str, default_config: dict = None):
        super().__init__()

        self._config_path = config_path

        if default_config is not None:
            self.update(default_config)

    def load(self, config_path: str = None):
        for path in [config_path, self._config_path]:
            if path and self._load(path):
                break

    @staticmethod
    def valid_conf_path(path: str):
        return os.path.exists(path)

    def _load(self, conf_path: str) -> bool:
        if not self.valid_conf_path(conf_path):
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
                if value is not None:
                    src_conf[key] = value
            else:
                src_dict = src_conf.get(key)
                conf_dict = conf.get(key, {})
                if src_dict is None:
                    src_conf[key] = conf_dict
                else:
                    self.update_conf(conf_dict, src_conf[key])
