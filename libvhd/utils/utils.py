# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014, Rackspace Hosting, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
#    implied. See the License for the specific language governing
#    permissions and limitations under the License.

import ctypes
from libvhd.utils import exceptions


class AlignedBuffer(object):
    def __init__(self, size, alignment=None):
        if alignment is None:
            alignment = 512
        elif alignment < 1:
            raise exceptions.BufferInvalidAlignment()

        if size < 0:
            raise exceptions.BufferInvalidSize("Buffer size must be >= 0")

        self._alignment = alignment
        self.size = size
        buf_size = self._alignment + self.size - 1

        self.buf = ctypes.create_string_buffer(buf_size)
        self.buf_addr = ctypes.addressof(self.buf)
        if self.buf_addr % self._alignment:
            self.buf_addr += self._alignment - (self.buf_addr % self._alignment)

    def get_pointer(self, offset=0, size=None):
        """Return a pointer into the aligned buffer at an offset, where
        the offset defaults to 0.  An optional size can be specified to
        ensure that the resulting pointer is at least size bytes from the
        end of the buffer.
        """

        if offset < 0:
            raise exceptions.BufferInvalidOffset("Offset must be >= 0")
        diff = self.size - offset
        if diff <= 0:
            raise exceptions.BufferInvalidOffset("Offset must be < buffer size")

        if size is None:
            size = diff
        elif size < 0:
            raise exceptions.BufferInvalidSize("Size must be >= 0")
        elif size > diff:
            raise exceptions.BufferInvalidSize("Size too large for given offset")

        t = ctypes.c_char * size
        return ctypes.pointer(t.from_address(self.buf_addr + offset))

    def write(self, data, offset=0):
        """Write data into the aligned buffer at a specific offset,
        where the offset defaults to 0.
        """
        p = self.get_pointer(offset=offset)
        p.contents.raw = data

    def read(self, offset=0, size=None):
        """Return data from the buffer at a specific offset.  An optional
        size can be specified to limit the data returned.  Size will
        default to the rest of the buffer.
        """
        p = self.get_pointer(offset=offset, size=size)
        return p.contents.raw
