#!/usr/bin/env python
"""
Follow class implements "tail -f" functionality to incrementally
read text and binary files as they grow.
"""
# Copyright (C) 2017 - Ken Spencer
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
__author__ = "Ken Spencer"
__version__ = '0.2'


import os
import time

class Follow(object):
    """file Follower class"""
    def __init__(self, fname, start=False, new_file_check=60, *open_args):
        """create file Follower instance.
           if start is True, read from start of file.
           new_file_check is period for file turnover check in seconds.
           additional open_args are passed to file open()."""
        self.fname = os.path.abspath(fname)
        self.pos = 0
        self.file = None
        self.stat = None
        self.stat_time = 0
        self.stat_time_min = new_file_check
        self.open_args = open_args
        self._reopen(start)

    def _reopen(self, start):
        """internal method to (re)open underlying file"""
        if self.file:
            self.file.close()
        self.file = open(self.fname, *self.open_args)
        self.stat = os.fstat(self.file.fileno())
        self.stat_time = time.time()
        if start:
            # the beginning: a very good place to start
            self.pos = 0
        else:
            # skip to the end. I always do....
            self.pos = self.stat.st_size

    def _preread(self):
        """internal method to call before attempting to read"""
        if not self.file:
            self._reopen(False)
            return
        now = time.time()
        if now >= self.stat_time + self.stat_time_min:
            nstat = os.stat(self.fname)
            self.stat_time = now
            if nstat.st_dev != self.stat.st_dev or \
                    nstat.st_ino != self.stat.st_ino:
                # start at top of new file
                self._reopen(True)
                return
        # should clear previous EOF condition
        self.file.seek(self.pos)

    def _postread(self, result):
        """internal method to call after attempting to read"""
        if result:
            self.pos = self.file.tell()

    def readline(self):
        """returns next line from the file, as a string.
           returns empty string if no additional data currently available."""
        self._preread()
        result = self.file.readline()
        self._postread(result)
        return result

    def readlines(self, *args):
        """returns list of strings, each a line from the file.
           returns empty string if no additional data currently available."""
        self._preread()
        result = self.file.readlines(*args)
        self._postread(result)
        return result

    def read(self, *args):
        """read([size]) -> read at most size bytes, returned as a string.
           returns empty string if no additional data currently available."""
        self._preread()
        result = self.file.read(*args)
        self._postread(result)
        return result

    def close(self):
        """Close the currently open file. A new read operation wil reopen."""
        if self.file:
            self.file.close()
            self.file = None
