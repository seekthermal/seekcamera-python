# Copyright 2021 Seek Thermal Inc.
#
# Original author: Michael S. Mead <mmead@thermal.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


class SeekCameraError(Exception):
    """Base class for SeekCamera errors."""

    @classmethod
    def _exception_for(cls, status):
        pass


class SeekCameraDeviceCommunicationError(SeekCameraError):
    """Raised when device communication fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -1


class SeekCameraInvalidParameterError(SeekCameraError):
    """Raised when an invalid parameter is passed."""

    @classmethod
    def _exception_for(cls, status):
        return status == -2


class SeekCameraPermissionsError(SeekCameraError):
    """Raised when a permissions error occurs."""

    @classmethod
    def _exception_for(cls, status):
        return status == -3


class SeekCameraNoDeviceError(SeekCameraError):
    """Raised when a command is issued and there is not device."""

    @classmethod
    def _exception_for(cls, status):
        return status == -4


class SeekCameraDeviceNotFoundError(SeekCameraError):
    """Raised when a device is expected to be found but is not."""

    @classmethod
    def _exception_for(cls, status):
        return status == -5


class SeekCameraDeviceBusyError(SeekCameraError):
    """Raised when a request is made but the device is busy."""

    @classmethod
    def _exception_for(cls, status):
        return status == -6


class SeekCameraTimeoutError(SeekCameraError):
    """Raised when an operation times out."""

    @classmethod
    def _exception_for(cls, status):
        return status == -7


class SeekCameraOverflowError(SeekCameraError):
    """Raised when overflow is detected."""

    @classmethod
    def _exception_for(cls, status):
        return status == -8


class SeekCameraUnknownRequestError(SeekCameraError):
    """Raised when an unknown request is made."""

    @classmethod
    def _exception_for(cls, status):
        return status == -9


class SeekCameraInterruptedError(SeekCameraError):
    """Raised when an operation is interrupted."""

    @classmethod
    def _exception_for(cls, status):
        return status == -10


class SeekCameraOutOfMemoryError(SeekCameraError):
    """Raised when the host runs out of memory."""

    @classmethod
    def _exception_for(cls, status):
        return status == -11


class SeekCameraNotSupportedError(SeekCameraError):
    """Raised when a request is made but it is not supported."""

    @classmethod
    def _exception_for(cls, status):
        return status == -12


class SeekCameraOtherError(SeekCameraError):
    """Raised when an unknown error occurs."""

    @classmethod
    def _exception_for(cls, status):
        return status == -99


class SeekCameraCannotPerformRequestError(SeekCameraError):
    """Raised when a request cannot be performed."""

    @classmethod
    def _exception_for(cls, status):
        return status == -103


class SeekCameraFlashAccessFailure(SeekCameraError):
    """Raised when flash access fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -104


class SeekCameraImplementationError(SeekCameraError):
    """Raised when there is an implementation error."""

    @classmethod
    def _exception_for(cls, status):
        return status == -105


class SeekCameraRequestPendingError(SeekCameraError):
    """Raised when a request is already pending."""

    @classmethod
    def _exception_for(cls, status):
        return status == -106


class SeekCameraInvalidFirmwareImageError(SeekCameraError):
    """Raised when an invalid firmware image is encountered."""

    @classmethod
    def _exception_for(cls, status):
        return status == -107


class SeekCameraInvalidKeyError(SeekCameraError):
    """Raised when an invalid key is encountered."""

    @classmethod
    def _exception_for(cls, status):
        return status == -108


class SeekCameraSensorCommunicationError(SeekCameraError):
    """Raised when sensor communication fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -109


class SeekCameraOutOfRangeError(SeekCameraError):
    """Raised when a value is out of range."""

    @classmethod
    def _exception_for(cls, status):
        return status == -301


class SeekCameraVerifyFailedError(SeekCameraError):
    """Raised when a verification function fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -302


class SeekCameraSystemCallFailedError(SeekCameraError):
    """Raised when a generic system call fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -303


class SeekCameraFileDoesNotExistError(SeekCameraError):
    """Raised when file does not exist but should."""

    @classmethod
    def _exception_for(cls, status):
        return status == -400


class SeekCameraDirectoryDoesNotExistError(SeekCameraError):
    """Raised when a directory does not exist but should."""

    @classmethod
    def _exception_for(cls, status):
        return status == -401


class SeekCameraFileReadFailedError(SeekCameraError):
    """Raised when a file read fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -402


class SeekCameraFileWriteFailedError(SeekCameraError):
    """Raised when a file write fails."""

    @classmethod
    def _exception_for(cls, status):
        return status == -403


class SeekCameraNotImplementedError(SeekCameraError):
    """Raised when a function is not implemented."""

    @classmethod
    def _exception_for(cls, status):
        return status == -1000


class SeekCameraNotPairedError(SeekCameraError):
    """Raised when a function is called on a non-paired device."""

    @classmethod
    def _exception_for(cls, status):
        return status == -1001


def is_error(status):
    """Checks if the input status code is an error or not.

    Parameters
    ----------
    status: int
        Integer status code returned by the C API.

    Returns
    -------
    bool
        True if the status code corresponds to an error; false otherwise.
    """
    return status != 0


def error_from_status(status):
    """Makes a SeekCamera base class or derived class from a status code.

    Parameters
    ----------
    status: int
        Integer status code returned by the C API.

    Returns
    -------
    SeekCameraError
        Base class or derived class.

    Raises
    ------
    SeekCameraInvalidParameterError
        If the input status code does not correspond to an error.
    """
    if not is_error(status):
        raise SeekCameraInvalidParameterError

    for cls in SeekCameraError.__subclasses__():
        if cls._exception_for(status):
            return cls

    return SeekCameraError
