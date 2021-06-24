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


class SeekCameraVersion:
    """Version of the seekcamera-python library.

    The version number scheme is [MAJOR].[MINOR].[PATCH].

    Attributes
    ----------
    MAJOR: int
        Major version number of the library.
    MINOR: int
        Minor version number of the library.
    PATCH: int
        Patch version number of the library.
    """

    MAJOR = 1
    MINOR = 1
    PATCH = 1

    def __str__(self):
        return "{}.{}.{}".format(self.MAJOR, self.MINOR, self.PATCH)

    def __repr__(self):
        return "SeekCameraVersion({}, {}, {})".format(
            self.MAJOR, self.MINOR, self.PATCH
        )
