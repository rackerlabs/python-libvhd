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

import ctypes
import utils.exceptions as exceptions
from utils.utils import _call
from libvhd import ListHead


class VHDUtilCheckOptions(ctypes.Structure):
    _fields_ = [
        ('ignore_footer', ctypes.c_char),
        ('ignore_parent_uuid', ctypes.c_char),
        ('ignore_timestamps', ctypes.c_char),
        ('check_data', ctypes.c_char),
        ('no_check_bat', ctypes.c_char),
        ('collect_stats', ctypes.c_char)]


class VHDUtilCheckStats(ctypes.Structure):
    _fields_ = [
        ('name', ctypes.c_char_p),
        ('bitmap', ctypes.c_char_p),
        ('secs_total', ctypes.c_uint64),
        ('secs_allocated', ctypes.c_uint64),
        ('secs_written', ctypes.c_uint64),
        ('next', ListHead)]


class VHDUtilCheckCtx(ctypes.Structure):
    _fields_ = [
        ('opts', VHDUtilCheckOptions),
        ('stats', ListHead),
        ('primary_footer_missing', ctypes.c_int)]


def coalesce(name, output=None, ancestor=None, step_parent=None, sparse=False):
    """Coalesce the VHD given by 'name'.
    Exactly one of 'output', 'ancestor', or 'step_parent' is required.
    """
    if name is None:
        raise exceptions.VHDUtilMissingArgument("'name' must be specified")

    def _f(x, y):
        if y:
            return x + 1
        else:
            return x

    c = reduce(_f, [output, ancestor, step_parent], 0)

    if c != 1:
        raise exceptions.VHDUtilMutuallyExclusiveArguments(
            "Exactly one of 'output', 'ancestor', or 'step_parent' is required.")

    sparse_i = 0
    if sparse:
        sparse_i = 1

    ret = None
    if output:
        ret = _call('vhd_util_coalesce_out',
                    ctypes.c_char_p(name), ctypes.c_char_p(output),
                    ctypes.c_int(sparse_i), ctypes.c_int(0))
    elif ancestor:
        ret = _call('vhd_util_coalesce_ancestor',
                    ctypes.c_char_p(name), ctypes.c_char_p(ancestor),
                    ctypes.c_int(sparse_i), ctypes.c_int(0))
    elif step_parent:
        ret = _call('vhd_util_coalesce_parent',
                    ctypes.c_char_p(name), ctypes.c_int(sparse_i),
                    ctypes.c_int(0), ctypes.c_char_p(step_parent))

    if ret != 0:
        raise exceptions.VHDUtilCoalesceError(errcode=ret.value)

def _set_bool_opt(obj, attr, bool_val):
    val = 1 if bool_val else 0
    setattr(obj, attr, ctypes.c_char(chr(val)))

def check(name, ignore_missing_primary_footers=False, ignore_parent_uuids=False,
          ignore_timestamps=False, skip_bat_overlap_check=False,
          check_parents=False, check_bitmaps=False):

    if name is None:
        raise exceptions.VHDUtilMissingArgument("'name' must be specified")

    if skip_bat_overlap_check and check_bitmaps:
        raise exceptions.VHDUtilMutuallyExclusiveArguments(
            "Cannot specify 'check_bitmaps' as True when "
            "'no_bat_overlap_check' is also True")

    o = VHDUtilCheckOptions()
    _set_bool_opt(o, 'ignore_footer', ignore_missing_primary_footers)
    _set_bool_opt(o, 'ignore_parent_uuid', ignore_parent_uuids)
    _set_bool_opt(o, 'ignore_timestamps', ignore_timestamps)
    _set_bool_opt(o, 'check_data', check_bitmaps)
    _set_bool_opt(o, 'no_check_bat', skip_bat_overlap_check)
    _set_bool_opt(o, 'collect_stats', False)

    list_head = ListHead()
    setattr(list_head, 'next', ctypes.pointer(list_head))
    setattr(list_head, 'prev', ctypes.pointer(list_head))

    vhd_check_ctx = VHDUtilCheckCtx()
    setattr(vhd_check_ctx, 'opts', o)
    setattr(vhd_check_ctx, 'stats', list_head)

    ret = _call('vhd_util_check_vhd',
                ctypes.pointer(vhd_check_ctx),
                ctypes.c_char_p(name))

    if ret == 0:
        if check_parents:
            ret = _call('vhd_util_check_parents',
                        ctypes.pointer(vhd_check_ctx),
                        ctypes.c_char_p(name))

    if ret != 0:
        raise exceptions.VHDUtilCheckError(errcode=ret.value)
