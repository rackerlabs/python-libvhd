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

class BaseException(Exception):
    """
    The base exception class for all exceptions this library raises.
    """
    def __init__(self, message=None):
        self.message = message or self.__class__.message

    def __str__(self):
        return self.message


class VHDException(BaseException):
    pass


class VHDInvalidSize(VHDException):
    pass


class VHDInvalidDiskType(VHDException):
    pass


class VHDInvalidOpenFlag(VHDException):
    pass


class VHDWriteError(VHDException):
    pass


class VHDReadError(VHDException):
    pass


class VHDOpenFailure(VHDException):
    pass


class VHDInvalidBuffer(VHDException):
    pass


class BufferFailure(BaseException):

    def __init__(self, message=None):
        super(BufferFailure, self).__init__(message)


class BufferInvalidOffset(BufferFailure):

    def __init__(self, message=None):
        super(BufferInvalidOffset, self).__init__(message)


class BufferInvalidSize(BufferFailure):

    def __init__(self, message=None):
        super(BufferInvalidSize, self).__init__(message)


class BufferInvalidAlignment(BufferFailure):

    def __init__(self, message=None):
        super(BufferInvalidAlignment, self).__init__(message)
