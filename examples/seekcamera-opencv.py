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

from threading import Condition

import cv2

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame,
)


class Renderer:
    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    # Notify the main thread that a new frame is available.
    with renderer.frame_condition:
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    print("%s: %s" % (str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        renderer.busy = True
        renderer.first_frame = True
        camera.color_palette = SeekCameraColorPalette.TYRIAN
        renderer.camera = camera

        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        if renderer.camera == camera:
            camera.capture_session_stop()

            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print(str(event_status))


def main():
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)
        while True:
            # Wait a maximum of 150ms for each frame to come in.
            # A condition variable is used to synchronize the access to the renderer.
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    img = renderer.frame.data

                    # Resize the rendering window.
                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    cv2.imshow(window_name, img)

            key = cv2.waitKey(1)

            # Process key events.
            if key == ord("q"):
                break

            # Check if the window has been closed manually.
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
