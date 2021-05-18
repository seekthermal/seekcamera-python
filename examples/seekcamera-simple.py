#!/usr/bin/env python3
# Copyright 2021 Seek Thermal Inc.
#
# Author: Michael S. Mead <mmead@thermal.com>
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

from time import sleep

import numpy as np

from seekcamera import (
    SeekCameraIOType,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
)


def on_frame(camera, camera_frame, file):
    frame = camera_frame.thermography_float

    print(
        "frame available: {cid} (size: {w}x{h})".format(
            cid=camera.chipid, w=frame.width, h=frame.height
        )
    )

    np.savetxt(file, frame.data, fmt="%.1f")


def on_event(camera, event_type, event_status, _user_data):
    print("%s: %s" % (str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        try:
            file = open("thermography-" + camera.chipid + ".csv", "w")
        except OSError as e:
            print("Failed to open file: %s" % str(e))
            return

        camera.register_frame_available_callback(on_frame, file)
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        camera.capture_session_stop()

    elif event_type == SeekCameraManagerEvent.ERROR:
        print(str(event_status) + ": " + camera.chipid)

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        pass


if __name__ == "__main__":
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        manager.register_event_callback(on_event)
        while True:
            sleep(1.0)
