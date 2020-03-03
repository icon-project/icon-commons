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
import time
from logging.handlers import RotatingFileHandler

from .utils import suffix as rotate_suffix, extMatch as rotate_extMatch


class IconRotatingFileHandler(RotatingFileHandler):
    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
        super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)

        self.rotator = self.custom_rotator
        self.logger_index = 0

    def custom_rotator(self, source, dest):
        if os.path.exists(dest):
            self.logger_index += 1
            os.rename(source, f"{dest}.{self.logger_index}")
        elif os.path.exists(source):
            self.logger_index = 0
            os.rename(source, dest)

    def doRollover(self):
        """
        Do a rollover, as described in __init__().
        """
        if self.stream:
            self.stream.close()
            self.stream = None
        dfn = self.rotation_filename(self.baseFilename + "." +
                                     time.strftime(rotate_suffix, time.localtime()))
        self.rotate(self.baseFilename, dfn)
        for s in self.getFilesToDelete():
            os.remove(s)
        if not self.delay:
            self.stream = self._open()

    # reference TimedRotatingFileHandler
    def getFilesToDelete(self):
        """
        Determine the files to delete when rolling over.

        More specific than the earlier method, which just used glob.glob().
        """
        dirName, baseName = os.path.split(self.baseFilename)
        fileNames = os.listdir(dirName)
        result = []
        prefix = baseName + "."
        plen = len(prefix)
        for fileName in fileNames:
            if fileName[:plen] == prefix:
                suffix = fileName[plen:]
                if rotate_extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result
