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


class TestCoalesce(unittest.TestCase):

    def test_no_name(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMissingArgument,
                              vhdutils.coalesce, name=None)

    def test_none_given_of_output_ancestor_step_parent(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMutuallyExclusiveArguments,
                              vhdutils.coalesce, name='fred.vhd')

    def test_too_many_given_of_output_ancestor_step_parent(self):
        mock_libvhd = mock.MagicMock()
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilMutuallyExclusiveArguments,
                              vhdutils.coalesce, name='fred.vhd',
                              output='foo.vhd', ancestor='foo2.vhd',
                              step_parent='foo3.vhd')

    def test_calls_coalesce_output(self):
        name = 'fred.vhd'
        output = 'foo.vhd'

        mock_libvhd = mock.MagicMock()
        mock_libvhd.vhd_util_coalesce_out.return_value = ctypes.c_int(0)
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            vhdutils.coalesce(name=name, output=output)

        self.assertEqual(1, mock_libvhd.vhd_util_coalesce_out.call_count)
        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_ancestor.call_count)
        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_parent.call_count)

    def test_calls_coalesce_ancestor(self):
        name = 'fred.vhd'
        ancestor = 'foo.vhd'

        mock_libvhd = mock.MagicMock()
        mock_libvhd.vhd_util_coalesce_ancestor.return_value = ctypes.c_int(0)
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            vhdutils.coalesce(name=name, ancestor=ancestor)

        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_out.call_count)
        self.assertEqual(1, mock_libvhd.vhd_util_coalesce_ancestor.call_count)
        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_parent.call_count)

    def test_calls_coalesce_parent(self):
        name = 'fred.vhd'
        step_parent = 'foo.vhd'

        mock_libvhd = mock.MagicMock()
        mock_libvhd.vhd_util_coalesce_parent.return_value = ctypes.c_int(0)
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            vhdutils.coalesce(name=name, step_parent=step_parent)

        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_out.call_count)
        self.assertEqual(0, mock_libvhd.vhd_util_coalesce_ancestor.call_count)
        self.assertEqual(1, mock_libvhd.vhd_util_coalesce_parent.call_count)

    def test_raises_error_on_nonzero_return(self):
        name = 'fred.vhd'
        output = 'foo.vhd'

        mock_libvhd = mock.MagicMock()
        mock_libvhd.vhd_util_coalesce_out.return_value = ctypes.c_int(1)
        with mock.patch.object(utils, '_get_libvhd_handle',
                               return_value=mock_libvhd):
            self.assertRaises(exceptions.VHDUtilCoalesceError,
                              callableObj=vhdutils.coalesce,
                              name=name, output=output)

