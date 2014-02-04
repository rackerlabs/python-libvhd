# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2014, Rackspace Hosting, Inc.
# Copyright 2011, Chris Behrens <cbehrens@codestud.com>
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
"""
Module for interfacing with xen's vhd library.
"""

import ctypes
import ctypes.util
import os
from utils.utils import _call

import utils.utils as utils
import utils.exceptions as exceptions


VHD_SECTOR_SIZE = 512
VHD_BLOCK_SHIFT = 21

VHD_DISK_TYPES = {
        'fixed': 2,
        'dynamic': 3,
        'differencing': 4}

VHD_OPEN_FLAGS = {
        'rdonly': 0x00000001,
        'rdwr': 0x00000002,
        'fast': 0x00000004,
        'strict': 0x00000008,
        'ignore_disabled': 0x00000010}

VHD_PLATFORM_CODES = {
        'PLAT_CODE_NONE': 0x0,
        'PLAT_CODE_WI2R': 0x57693272,  # deprecated
        'PLAT_CODE_WI2K': 0x5769326B,  # deprecated
        'PLAT_CODE_W2RU': 0x57327275,  # Windows relative path (UTF-16)
        'PLAT_CODE_W2KU': 0x57326B75,  # Windows absolute path (UTF-16)
        'PLAT_CODE_MAC' : 0x4D616320,  # MacOS alias stored as a blob
        'PLAT_CODE_MACX': 0x4D616358,  # File URL (UTF-8), see RFC 2396.
}

class VHDVersion(object):

    def __init__(self, major_minor=None, version=None):
        """Construct a VHDVersion object.
        major_minor must be a tuple in the form (<major>, <minor>)
        version is a single int representing the version with the upper
        16 bits being major and lower 16 bits minor.
        If both are provided, version is ignored."""

        if major_minor:
            self._version = (major_minor[0] << 16) | major_minor[1]
        elif version:
            self._version = version
        else:
            self._version = 0L

    @property
    def version(self):
        return self._version

    @property
    def major(self):
        return self._version >> 16

    @property
    def minor(self):
        return self._version & 0x0000FFFF

    def __repr__(self):
        return str.format("VHDVersion(%d, %d)" % (self.major, self.minor))


class ListHead(ctypes.Structure):
    pass

ListHead._fields_ = [
            ('next', ctypes.POINTER(ListHead)),
            ('prev', ctypes.POINTER(ListHead))]


class VHDPrtLoc(ctypes.Structure):
    _fields_ = [
            ('code', ctypes.c_uint),
            ('data_space', ctypes.c_uint),
            ('data_len', ctypes.c_uint),
            ('res', ctypes.c_uint),
            ('data_offset', ctypes.c_ulonglong)]


class VHDHeader(ctypes.Structure):
    _fields_ = [
            ('cookie', ctypes.c_char * 8),
            ('data_offset', ctypes.c_ulonglong),
            ('table_offset', ctypes.c_ulonglong),
            ('hdr_ver', ctypes.c_uint),
            ('max_bat_size', ctypes.c_uint),
            ('block_size', ctypes.c_uint),
            ('checksum', ctypes.c_uint),
            ('prt_uuid', ctypes.c_char * 16),
            ('prt_ts', ctypes.c_uint),
            ('res1', ctypes.c_uint),
            ('prt_name', ctypes.c_char * 512),
            ('loc', VHDPrtLoc * 8),
            ('res2', ctypes.c_char * 256)]


class VHDFooter(ctypes.Structure):
    _fields_ = [
            ('cookie', ctypes.c_char * 8),
            ('features', ctypes.c_uint),
            ('ff_version', ctypes.c_uint),
            ('data_offset', ctypes.c_ulonglong),
            ('timestamp', ctypes.c_uint),
            ('crtr_app', ctypes.c_char * 4),
            ('crtr_ver', ctypes.c_uint),
            ('crtr_os', ctypes.c_uint),
            ('orig_size', ctypes.c_ulonglong),
            ('curr_size', ctypes.c_ulonglong),
            ('geometry', ctypes.c_uint),
            ('type', ctypes.c_uint),
            ('checksum', ctypes.c_uint),
            ('uuid', ctypes.c_char * 16),
            ('saved', ctypes.c_char),
            ('hidden', ctypes.c_char),
            ('reserved', ctypes.c_char * 426)]


class VHDBat(ctypes.Structure):
    _fields_ = [
            ('spb', ctypes.c_uint),
            ('entries', ctypes.c_uint),
            ('bat', ctypes.c_void_p)]


class VHDBatMapHeader(ctypes.Structure):
    _fields_ = [
            ('cookie', ctypes.c_char * 8),
            ('batmap_offset', ctypes.c_ulonglong),
            ('batmap_size', ctypes.c_uint),
            ('batmap_version', ctypes.c_uint),
            ('checksum', ctypes.c_uint)]


class VHDBatMap(ctypes.Structure):
    _fields_ = [
            ('header', VHDBatMapHeader),
            ('map', ctypes.c_void_p)]


class VHDContext(ctypes.Structure):
    _fields_ = [
            ('fd', ctypes.c_int),
            ('file', ctypes.c_char_p),
            ('oflags', ctypes.c_int),
            ('isblock', ctypes.c_int),
            ('spb', ctypes.c_uint),
            ('bm_secs', ctypes.c_uint),
            ('header', VHDHeader),
            ('footer', VHDFooter),
            ('bat', VHDBat),
            ('batmap', VHDBatMap),
            ('next', ListHead),
            ('custom_parent', ctypes.c_char_p)]


class VHD(object):
    _closed = True

    def __init__(self, filename, flags=None):
        """Open a VHD."""
        if flags is None:
            flags = 'rdonly'
        open_flags = 0
        try:
            for flag in flags.split(','):
                open_flags |= VHD_OPEN_FLAGS[flag]
        except KeyError:
            valid_flags = ','.join(VHD_OPEN_FLAGS.iterkeys())
            raise exceptions.VHDInvalidOpenFlag("Valid open flags are: %s" % valid_flags)

        self.filename = filename
        self.open_flags = flags
        self.vhd_context = VHDContext()

        ret = _call('vhd_open',
                    ctypes.pointer(self.vhd_context),
                    ctypes.c_char_p(filename), ctypes.c_int(open_flags))
        if ret:
            raise exceptions.VHDOpenFailure("Error opening: %s" % ctypes.get_errno())
        self._closed = False

    def close(self):
        """Close a VHD."""
        if self._closed:
            return
        _call('vhd_close', ctypes.pointer(self.vhd_context))
        self._closed = True
        self.vhd_context = None

    def __del__(self):
        """Make sure the VHD gets closed."""
        self.close()

    def get_footer(self):
        """Get the VHD footer data."""
        ftr = {}
        footer = self.vhd_context.footer
        for field, _ in footer._fields_:
            ftr[field] = getattr(footer, field)
        return ftr

    def get_header(self):
        """Get the VHD header data."""
        hdr = {}
        header = self.vhd_context.header
        for field, _ in header._fields_:
            val = getattr(header, field)
            if field == 'prt_name':
                buf_type = ctypes.c_char * 512
                buf_p = ctypes.POINTER(buf_type)()
                ret = _call('vhd_header_decode_parent',
                            ctypes.pointer(self.vhd_context),
                            ctypes.pointer(header),
                            ctypes.pointer(buf_p))
                if ret:
                    val = 'Cannot read parent name'
                else:
                    val = buf_p.contents.value

            elif field == 'prt_uuid':
                val = utils.uuid_unparse(val)

            elif field == 'hdr_ver':
                val = VHDVersion(version=val)

            elif field == 'loc':
                val = self._get_locators(val)

            hdr[field] = val
        return hdr

    def _get_locators(self, raw_locs):
        locators = []
        for raw_loc in raw_locs:
            locator = {}
            for name, _ in raw_loc._fields_:
                locator[name] = getattr(raw_loc, name)
            if locator['code'] != 0L:
                locators.append(locator)

        return locators

    def get_max_virtual_size(self):
        header = self.vhd_context.header
        max_bat_size = getattr(header, 'max_bat_size')
        max_virtual_size = max_bat_size << (VHD_BLOCK_SHIFT - 20)

        return max_virtual_size

    def get_chain_depth(self):
        chain_len = ctypes.c_int()

        ret = _call("vhd_chain_depth", ctypes.pointer(self.vhd_context),
                    ctypes.byref(chain_len))
        if ret:
            raise exceptions.VHDException("Cannot compute chain depth. Err %d" % ret)

        return chain_len.value

    def io_write(self, buf, cur_sec, num_secs):
        """Write sectors from an aligned buffer into a VHD."""
        if not isinstance(buf, utils.AlignedBuffer):
            raise exceptions.VHDInvalidBuffer("buf argument should be a AlignedBuffer"
                    " instance")
        ret = _call('vhd_io_write',
                ctypes.pointer(self.vhd_context),
                buf.get_pointer(),
                ctypes.c_ulonglong(cur_sec),
                ctypes.c_uint(num_secs))
        if not ret:
            return
        errno = ctypes.get_errno()
        raise exceptions.VHDWriteError("Error writing: %s" % errno)

    def io_read(self, buf, cur_sec, num_secs):
        """Read sectors from a VHD into an aligned buffer."""
        if not isinstance(buf, utils.AlignedBuffer):
            raise exceptions.VHDInvalidBuffer("buf argument should be a AlignedBuffer"
                    " instance")
        ret = _call('vhd_io_read',
                ctypes.pointer(self.vhd_context),
                buf.get_pointer(),
                ctypes.c_ulonglong(cur_sec),
                ctypes.c_uint(num_secs))
        if not ret:
            return
        errno = ctypes.get_errno()
        raise exceptions.VHDReadError("Error reading: %s" % errno)

    def __repr__(self):
        if self._closed:
            return "<%s: closed>" % self.filename
        footer_values = self.get_footer()
        return "<%s: opened '%s', footer '%s'>" % (
                self.filename, self.open_flags, footer_values)



def vhd_create(filename, size, disk_type=None, create_flags=None):
    """Create a new empty VHD file."""

    if disk_type is None:
        disk_type = 'dynamic'
    if create_flags is None:
        create_flags = 0

    try:
        disk_type = VHD_DISK_TYPES[disk_type]
    except KeyError:
        valid_disk_types = ','.join(VHD_DISK_TYPES.iterkeys())
        raise exceptions.VHDInvalidDiskType("Valid disk types are: %s" %
                valid_disk_types)
    size = int(size)
    create_flags = int(create_flags)

    if size % VHD_SECTOR_SIZE:
        raise exceptions.VHDInvalidSize("size is not a multiple of %d" %
                VHD_SECTOR_SIZE)
    return _call('vhd_create', ctypes.c_char_p(filename),
            ctypes.c_ulonglong(size),
            ctypes.c_int(disk_type),
            ctypes.c_uint(create_flags))


def vhd_convert_from_raw(src_filename, dest_filename, disk_type=None,
        sparse=False):
    """Convert a RAW disk image to a VHD."""

    if disk_type is None:
        disk_type = 'dynamic'

    size = os.stat(src_filename).st_size
    if size % VHD_SECTOR_SIZE:
        size += VHD_SECTOR_SIZE - (size % VHD_SECTOR_SIZE)

    cur_sec = 0
    num_secs_to_read = 4096
    buf_size = VHD_SECTOR_SIZE * num_secs_to_read
    buf = utils.AlignedBuffer(buf_size, alignment=VHD_SECTOR_SIZE)

    all_zero_sector = '\x00' * VHD_SECTOR_SIZE

    def _write_sectors(data, start, end, start_sec):
        buf.write(data[start:end])
        num_secs = (end - start) / VHD_SECTOR_SIZE
        vhd.io_write(buf, start_sec, num_secs)

    with open(src_filename, 'rb') as f:
        fileno = f.fileno()
        vhd_create(dest_filename, size, disk_type)
        vhd = VHD(dest_filename, 'rdwr')

        while True:
            data = os.read(fileno, buf_size)
            if len(data) == 0:
                break
            data_len = len(data)
            if (data_len < buf_size and
                    data_len % VHD_SECTOR_SIZE):
                pad = VHD_SECTOR_SIZE - (data_len % VHD_SECTOR_SIZE)
                data += '\x00' * pad
                data_len += pad

            max_num = data_len / VHD_SECTOR_SIZE

            if not sparse:
                _write_sectors(data, 0, data_len)
                cur_sec += max_num
                continue

            non_zero_start = None
            for i in xrange(max_num):
                beginning = i * VHD_SECTOR_SIZE
                ending = beginning + VHD_SECTOR_SIZE
                sector = data[beginning:ending]
                if sector == all_zero_sector:
                    if non_zero_start is not None:
                        # We can write the previous sectors
                        _write_sectors(data, non_zero_start, non_zero_end,
                                start_sec)
                        non_zero_start = None
                else:
                    if non_zero_start is None:
                        # First non-zero sector
                        non_zero_start = beginning
                        start_sec = cur_sec
                    non_zero_end = ending
                cur_sec += 1
            if non_zero_start is not None:
                _write_sectors(data, non_zero_start, non_zero_end, start_sec)
        vhd.close()


def vhd_convert_to_raw(src_filename, dest_filename, sparse=False):
    """Convert a VHD disk image to RAW."""

    vhd = VHD(src_filename, 'rdonly')
    file_size = vhd.get_footer()['curr_size']
    total_sectors = file_size / VHD_SECTOR_SIZE

    with open(dest_filename, 'wb') as f:
        fileno = f.fileno()
        cur_sec = 0
        num_secs_to_read = 4096
        buf_size = VHD_SECTOR_SIZE * num_secs_to_read
        buf = utils.AlignedBuffer(buf_size, alignment=VHD_SECTOR_SIZE)

        while cur_sec < total_sectors:
            if cur_sec + num_secs_to_read > total_sectors:
                num_secs_to_read = total_sectors - cur_sec
            vhd.io_read(buf, cur_sec, num_secs_to_read)
            data = buf.read()
            total_bytes = num_secs_to_read * VHD_SECTOR_SIZE
            os.write(fileno, data)
            cur_sec += num_secs_to_read
    vhd.close()
