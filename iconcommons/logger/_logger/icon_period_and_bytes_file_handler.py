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

from .icon_rotating_file_handler import IconRotatingFileHandler
from .icon_time_rotating_file_handler import IconTimeRotatingFileHandler


class IconPeriodAndBytesFileHandler(BaseRotatingHandler):
    def __init__(self, filename,
                 mode='a',
                 maxBytes=0,
                 backupCount=0,
                 encoding=None,
                 delay=0,
                 when='h',
                 interval=1,
                 utc=False,
                 atTime=None):
        super().__init__(filename, mode, encoding, delay)

        '''
        In fact the difference between adding methods dynamically at run time and your example is huge:

        in your case, you just attach a function to an object, you can call it of course but it is unbound, 
        it has no relation with the object itself (ie. you cannot use self inside the function)
        when added with MethodType, you create a bound method and it behaves like a normal Python method for the object, 
        you have to take the object it belongs to as first argument 
        (it is normally called self) and you can access it inside the function
        This example shows the difference:
        
        def func(obj):
          print 'I am called from', obj
        class A:
          pass
        a=A()
        a.func=func
        a.func()
        This fails with a TypeError: func() takes exactly 1 argument (0 given), whereas this code works as expected:
        
        import types
        a.func = types.MethodType(func, a, A)
        a.func()
        '''

        self.computeRollover = types.MethodType(IconTimeRotatingFileHandler.computeRollover, self)
        self.doRollover_bytes = types.MethodType(IconRotatingFileHandler.doRollover, self)
        self.getFilesToDelete = types.MethodType(IconRotatingFileHandler.getFilesToDelete, self)
        self.shouldRollover_period = types.MethodType(IconTimeRotatingFileHandler.shouldRollover, self)
        self.shouldRollover_bytes = types.MethodType(IconRotatingFileHandler.shouldRollover, self)

        # period
        self.maxBytes = maxBytes
        self.backupCount = backupCount
        self.when = when.upper()
        self.interval = interval
        self.utc = utc
        self.atTime = atTime

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

        # bytes
        self.rotator = types.MethodType(IconRotatingFileHandler.custom_rotator, self)
        self.logger_index = 0

    def doRollover(self):
        # custom bytes + period

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

        # support multify file
        return self.doRollover_bytes()

    def shouldRollover(self, record):
        return self.shouldRollover_period(record) or self.shouldRollover_bytes(record)
