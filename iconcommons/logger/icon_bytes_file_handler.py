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
from logging.handlers import BaseRotatingHandler
from iconcommons.logger.logger_utils import suffix, extMatch


class IconBytesFileHandler(BaseRotatingHandler):
    suffix = suffix
    extMatch = extMatch

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):

        if maxBytes > 0:
            mode = 'a'

        super().__init__(filename, mode, encoding, delay)

        self.maxBytes = maxBytes
        self.backupCount = backupCount
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
                                     time.strftime(self.suffix, time.localtime()))
        self.rotate(self.baseFilename, dfn)
        for s in self.getFilesToDelete():
            os.remove(s)
        if not self.delay:
            self.stream = self._open()

    def shouldRollover(self, record):
        """
        Determine if rollover should occur.

        Basically, see if the supplied record would cause the file to exceed
        the size limit we have.
        """
        if self.stream is None:                 # delay was set...
            self.stream = self._open()
        if self.maxBytes > 0:                   # are we rolling over?
            msg = "%s\n" % self.format(record)
            self.stream.seek(0, 2)  #due to non-posix-compliant Windows feature
            if self.stream.tell() + len(msg) >= self.maxBytes:
                return 1
        return 0

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
                if self.extMatch.match(suffix):
                    result.append(os.path.join(dirName, fileName))
        if len(result) < self.backupCount:
            result = []
        else:
            result.sort()
            result = result[:len(result) - self.backupCount]
        return result
