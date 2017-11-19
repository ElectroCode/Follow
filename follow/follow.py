#!/usr/bin/env python

"""
Follow class implements "tail -f" functionality to incrementally
read text and binary files as they grow.
"""

__author__ = "Phil Budne"
__revision__ = "$Revision: 1.5 $"
__version__ = '0.2'

#       Copyright (c) 2010 Philip Budne (phil@ultimate.com)
#       Licensed under the MIT licence: 
#       
#       Permission is hereby granted, free of charge, to any person
#       obtaining a copy of this software and associated documentation
#       files (the "Software"), to deal in the Software without
#       restriction, including without limitation the rights to use,
#       copy, modify, merge, publish, distribute, sublicense, and/or sell
#       copies of the Software, and to permit persons to whom the
#       Software is furnished to do so, subject to the following
#       conditions:
#       
#       The above copyright notice and this permission notice shall be
#       included in all copies or substantial portions of the Software.
#       
#       THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#       EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#       OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#       NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#       HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#       WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#       FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#       OTHER DEALINGS IN THE SOFTWARE.

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

def test():
    """test routine"""
    import sys

    files = [ (path, Follow(path)) for path in sys.argv[1:] ]

    if not files:
        print "Usage: follow.py files ...."
        sys.exit(1)

    inisleep = 0.25
    sleep = inisleep
    while True:
        lines = False
        for fname, filep in files:
            line = filep.readline()
            if line:
                lines = True
                sys.stdout.write("%s: %s" % (fname, line))
                sleep = inisleep
        if not lines:
            time.sleep(sleep)
            sleep *= 2
            if sleep > 10:
                sleep = inisleep

if __name__ == "__main__":
    test()
