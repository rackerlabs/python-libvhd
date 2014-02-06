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
import mock
import unittest
import libvhd.utils.utils as utils
import libvhd.utils.exceptions as exceptions
from libvhd import vhdutils


class TestCheck(unittest.TestCase):

    def test_no_name(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMissingArgument,
                              vhdutils.check, name=None)

    def test_skip_check_overlap_and_stats(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMutuallyExclusiveArguments,
                              vhdutils.check, name='fred',
                              skip_bat_overlap_check=True,
                              stats=True)

    def test_skip_check_overlap_and_check_bitmaps(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMutuallyExclusiveArguments,
                              vhdutils.check, name='fred',
                              skip_bat_overlap_check=True,
                              check_bitmaps=True)
