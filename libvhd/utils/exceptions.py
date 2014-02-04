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

class ErrMessage(object):
    def __init__(self, mnemonic, code, description):
        self.mnemonic = mnemonic
        self.code = code
        self.description = description


ERRNO = [
    ErrMessage('ENONE', 0, "No error code provided"),
    ErrMessage('EPERM', 1, "Operation not permitted"),
    ErrMessage('ENOENT', 2, "No such file or directory"),
    ErrMessage('ESRCH', 3, "No such process"),
    ErrMessage('EINTR', 4, "Interrupted system call"),
    ErrMessage('EIO', 5, "I/O error"),
    ErrMessage('ENXIO', 6, "No such device or address"),
    ErrMessage('E2BIG', 7, "Argument list too long"),
    ErrMessage('ENOEXEC', 8, "Exec format error"),
    ErrMessage('EBADF', 9, "Bad file number"),
    ErrMessage('ECHILD', 10, "No child processes"),
    ErrMessage('EAGAIN', 11, "Try again"),
    ErrMessage('ENOMEM', 12, "Out of memory"),
    ErrMessage('EACCES', 13, "Permission denied"),
    ErrMessage('EFAULT', 14, "Bad address"),
    ErrMessage('ENOTBLK', 15, "Block device required"),
    ErrMessage('EBUSY', 16, "Device or resource busy"),
    ErrMessage('EEXIST', 17, "File exists"),
    ErrMessage('EXDEV', 18, "Cross-device link"),
    ErrMessage('ENODEV', 19, "No such device"),
    ErrMessage('ENOTDIR', 20, "Not a directory"),
    ErrMessage('EISDIR', 21, "Is a directory"),
    ErrMessage('EINVAL', 22, "Invalid argument"),
    ErrMessage('ENFILE', 23, "File table overflow"),
    ErrMessage('EMFILE', 24, "Too many open files"),
    ErrMessage('ENOTTY', 25, "Not a typewriter"),
    ErrMessage('ETXTBSY', 26, "Text file busy"),
    ErrMessage('EFBIG', 27, "File too large"),
    ErrMessage('ENOSPC', 28, "No space left on device"),
    ErrMessage('ESPIPE', 29, "Illegal seek"),
    ErrMessage('EROFS', 30, "Read-only file system"),
    ErrMessage('EMLINK', 31, "Too many links"),
    ErrMessage('EPIPE', 32, "Broken pipe"),
    ErrMessage('EDOM', 33, "Math argument out of domain of func"),
    ErrMessage('ERANGE', 34, "Math result not representable")
]

class BaseException(Exception):
    """
    The base exception class for all exceptions this library raises.
    """
    def __init__(self, message=None):
        self.message = message or self.__class__.message

    def __str__(self):
        return self.message

#
# Exceptions for base VHD operations
#

class VHDException(BaseException):

    def __init__(self, message=None):
        super(VHDException, self).__init__(message)


class VHDInvalidSize(VHDException):

    def __init__(self, message=None):
        super(VHDInvalidSize, self).__init__(message)


class VHDInvalidDiskType(VHDException):

    def __init__(self, message=None):
        super(VHDInvalidDiskType, self).__init__(message)


class VHDInvalidOpenFlag(VHDException):

    def __init__(self, message=None):
        super(VHDInvalidOpenFlag, self).__init__(message)


class VHDWriteError(VHDException):

    def __init__(self, message=None):
        super(VHDWriteError, self).__init__(message)


class VHDReadError(VHDException):

    def __init__(self, message=None):
        super(VHDReadError, self).__init__(message)


class VHDOpenFailure(VHDException):

    def __init__(self, message=None):
        super(VHDOpenFailure, self).__init__(message)


class VHDInvalidBuffer(VHDException):

    def __init__(self, message=None):
        super(VHDInvalidBuffer, self).__init__(message)


#
# Exceptions for VHD utility operations
#

class VHDUtilException(BaseException):

    def __init__(self, message=None):
        super(VHDUtilException, self).__init__(message)

class VHDUtilMissingArgument(VHDUtilException):

    def __init__(self, message=None):
        super(VHDUtilMissingArgument, self).__init__(message)


class VHDUtilMutuallyExclusiveArguments(VHDUtilException):

    def __init__(self, message=None):
        super(VHDUtilMutuallyExclusiveArguments, self).__init__(message)


class VHDUtilCoalesceError(VHDUtilException):

    def __init__(self, errcode=0, message=None):
        if (errcode >= 0) and (errcode < len(ERRNO)):
            self.err_msg = ERRNO[errcode]
        else:
            self.err_msg = ERRNO[0]

        if message is None:
            message = "Error: %s(%d) - %s" % \
                      (self.err_msg.mnemonic, self.err_msg.code,
                       self.err_msg.description)
        super(VHDUtilCoalesceError, self).__init__(message)


#
# Exceptions for AlignedBuffer operations
#

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
