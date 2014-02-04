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

    if ret and (ret.value != 0):
        raise exceptions.VHDUtilCoalesceError(errcode=ret.value)