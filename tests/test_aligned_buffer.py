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
import unittest
from libvhd.utils.utils import AlignedBuffer
import libvhd.utils.exceptions as exceptions

class TestAlignedBuffer(unittest.TestCase):

    def _assert_buffer_address_for_alignment(self, buf, alignment):
        buf_addr = ctypes.addressof(buf.buf)
        offset = buf_addr % alignment
        expected_addr = buf_addr + (alignment - offset)
        self.assertEqual(expected_addr, buf.buf_addr)

    def test_init_default_alignment(self):
        alignment = 512
        buf_size = 10
        buf = AlignedBuffer(buf_size)

        self.assertEqual(buf_size, buf.size)
        self.assertEqual(alignment, buf._alignment)
        self._assert_buffer_address_for_alignment(buf, alignment)

    def test_init_given_alignment(self):
        alignment = 300
        buf_size = 10
        buf = AlignedBuffer(buf_size, alignment)

        self.assertEqual(buf_size, buf.size)
        self.assertEqual(alignment, buf._alignment)
        self._assert_buffer_address_for_alignment(buf, alignment)

    def test_init_bad_alignment(self):
        alignment = 0
        buf_size = 10

        self.assertRaises(exceptions.BufferInvalidAlignment, AlignedBuffer,
                          buf_size, alignment)

    def test_init_bad_size(self):
        alignment = 1
        buf_size = -1

        self.assertRaises(exceptions.BufferInvalidSize, AlignedBuffer,
                          buf_size, alignment)

    def test_read_empty(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = '\x00' * buf_size

        actual = buf.read()

        self.assertEqual(expected, actual)

    def test_write_read(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        actual = buf.read()

        # Without size read returns all contents, so expect nulls after data
        expected += '\x00' * (buf_size - len(expected))
        self.assertEqual(expected, actual[:len(expected)])

    def test_write_read_with_size(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        actual = buf.read(size=5)

        self.assertEqual(expected[:5], actual)

    def test_write_read_with_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = 6
        actual = buf.read(offset=offset)

        expected = expected[6:]
        expected += '\x00' * (buf_size - len(expected) - offset)
        self.assertEqual(expected, actual)

    def test_write_read_with_size_and_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = 6
        size = 5
        actual = buf.read(size=size, offset=offset)

        expected = expected[offset:offset + size]
        self.assertEqual(expected, actual)

    def test_get_pointer(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        ptr = buf.get_pointer()

        actual = ptr.contents.raw

        # Without size read returns all contents, so expect nulls after data
        expected += '\x00' * (buf_size - len(expected))
        self.assertEqual(expected, actual[:len(expected)])

    def test_get_pointer_with_size(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        size = 5
        ptr = buf.get_pointer(size=size)

        actual = ptr.contents.raw

        self.assertEqual(expected[:5], actual[:len(expected)])

    def test_get_pointer_with_size_and_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = 6
        size = 5
        ptr = buf.get_pointer(size=size, offset=offset)

        actual = ptr.contents.raw

        expected = expected[offset:offset + size]
        self.assertEqual(expected, actual)

    def test_get_pointer_with_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = 6
        ptr = buf.get_pointer(offset=offset)

        actual = ptr.contents.raw

        expected = expected[6:]
        expected += '\x00' * (buf_size - len(expected) - offset)
        self.assertEqual(expected, actual)

    def test_get_pointer_with_too_large_size(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        size = buf_size + 1

        self.assertRaises(exceptions.BufferInvalidSize, buf.get_pointer,
                          size=size)

    def test_get_pointer_with_negative_size(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        size = -1

        self.assertRaises(exceptions.BufferInvalidSize, buf.get_pointer,
                          size=size)

    def test_get_pointer_with_too_large_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = buf_size + 1

        self.assertRaises(exceptions.BufferInvalidOffset, buf.get_pointer,
                          offset=offset)

    def test_get_pointer_with_negative_offset(self):
        buf_size = 20

        buf = AlignedBuffer(buf_size)

        expected = "Hello world!"
        buf.write(expected)

        offset = -1

        self.assertRaises(exceptions.BufferInvalidOffset, buf.get_pointer,
                          offset=offset)
