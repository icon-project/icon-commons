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

from logging.handlers import TimedRotatingFileHandler


class IconPeriodFileHandler(TimedRotatingFileHandler):
    def __init__(self, filename, when='h', interval=1, backupCount=0,
                 encoding=None, delay=False, utc=False, atTime=None):
        super().__init__(filename, when, interval, backupCount, encoding, delay, utc, atTime)

    def computeRollover(self, currentTime):
        return super().computeRollover(currentTime)

    def shouldRollover(self, record):
        return super().shouldRollover(record)

    def getFilesToDelete(self):
        return super().getFilesToDelete()

    def doRollover(self):
        super().doRollover()
