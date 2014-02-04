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

import unittest
from libvhd.libvhd import VHDVersion


class TestVHDVersion(unittest.TestCase):

    def test_create_from_tuple(self):
        major = 1
        minor = 5
        version = major << 16 | minor
        v = VHDVersion(major_minor=(major, minor))

        self.assertEqual(major, v.major)
        self.assertEqual(minor, v.minor)
        self.assertEqual(version, v.version)

    def test_create_from_version(self):
        major = 1
        minor = 5
        version = major << 16 | minor
        v = VHDVersion(version=version)

        self.assertEqual(major, v.major)
        self.assertEqual(minor, v.minor)
        self.assertEqual(version, v.version)

    def get_create_from_defaults(self):
        major = 0
        minor = 0
        version = major << 16 | minor
        v = VHDVersion()

        self.assertEqual(major, v.major)
        self.assertEqual(minor, v.minor)
        self.assertEqual(version, v.version)
