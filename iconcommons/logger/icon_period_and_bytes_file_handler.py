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
import types
from logging.handlers import BaseRotatingHandler
from stat import ST_MTIME

from iconcommons.logger.logger_utils import suffix, extMatch
from .icon_bytes_file_handler import IconBytesFileHandler
from .icon_period_file_handler import IconPeriodFileHandler


class IconPeriodAndBytesFileHandler(BaseRotatingHandler):
    suffix = suffix
    extMatch = extMatch

    def __init__(self, filename, mode='a', maxBytes=0, backupCount=0,
                 encoding=None, delay=0, when='h', interval=1, utc=False):
        super().__init__(filename, mode, encoding, delay)
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.when = when.upper()
        self.interval = interval
        self.utc = utc

        self.computeRollover = types.MethodType(IconPeriodFileHandler.computeRollover, self)
        self.doRollover_bytes = types.MethodType(IconBytesFileHandler.doRollover, self)
        self.getFilesToDelete = types.MethodType(IconBytesFileHandler.getFilesToDelete, self)
        self.shouldRollover_period = types.MethodType(IconPeriodFileHandler.shouldRollover, self)
        self.shouldRollover_bytes = types.MethodType(IconBytesFileHandler.shouldRollover, self)

        if self.when == 'S':
            self.interval = 1 # one second
        elif self.when == 'M':
            self.interval = 60 # one minute
        elif self.when == 'H':
            self.interval = 60 * 60 # one hour
        elif self.when == 'D' or self.when == 'MIDNIGHT':
            self.interval = 60 * 60 * 24 # one day
        elif self.when.startswith('W'):
            self.interval = 60 * 60 * 24 * 7 # one week
            if len(self.when) != 2:
                raise ValueError("You must specify a day for weekly rollover from 0 to 6 (0 is Monday): %s" % self.when)
            if self.when[1] < '0' or self.when[1] > '6':
                raise ValueError("Invalid day specified for weekly rollover: %s" % self.when)
            self.dayOfWeek = int(self.when[1])
        else:
            raise ValueError("Invalid rollover interval specified: %s" % self.when)

        self.interval = self.interval * interval # multiply by units requested
        # The following line added because the filename passed in could be a
        # path object (see Issue #27493), but self.baseFilename will be a string
        filename = self.baseFilename
        if os.path.exists(filename):
            t = os.stat(filename)[ST_MTIME]
        else:
            t = int(time.time())
        self.rolloverAt = self.computeRollover(t)

    def doRollover(self):
        # get from logging.handlers.TimedRotatingFileHandler.doRollover()
        current_time = int(time.time())
        dst_now = time.localtime(current_time)[-1]
        new_rollover_at = self.computeRollover(current_time)

        while new_rollover_at <= current_time:
            new_rollover_at = new_rollover_at + self.interval

        # If DST changes and midnight or weekly rollover, adjust for this.
        if (self.when == 'MIDNIGHT' or self.when.startswith('W')) and not self.utc:
            dst_at_rollover = time.localtime(new_rollover_at)[-1]
            if dst_now != dst_at_rollover:
                if not dst_now:  # DST kicks in before next rollover, so we need to deduct an hour
                    addend = -3600
                else:  # DST bows out before next rollover, so we need to add an hour
                    addend = 3600
                new_rollover_at += addend
        self.rolloverAt = new_rollover_at

        return self.doRollover_bytes()

    def shouldRollover(self, record):
        return self.shouldRollover_period(record) or self.shouldRollover_bytes(record)
