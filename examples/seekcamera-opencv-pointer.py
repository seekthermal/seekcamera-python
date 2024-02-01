#!/usr/bin/env python3
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

from threading import Condition

import cv2
import numpy as np 
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
    """Contains camera and image data required to render images to the screen."""

    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):

    frame = camera_frame.thermography_float

    print(
        "frame available: {cid} (size: {w}x{h})".format(
            cid=_camera.chipid, w=frame.width, h=frame.height
        )
    )

    # Append the frame to the CSV file.
    # np.savetxt(file, frame.data, fmt="%.1f")
    # print(frame,"5555555555555555555555555555555555555555555555555555555")
    """Async callback fired whenever a new frame is available.
    
    Parameters
    ----------
    _camera: SeekCamera
        Reference to the camera for which the new frame is available.
    camera_frame: SeekCameraFrame
        Reference to the class encapsulating the new frame (potentially
        in multiple formats).
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the renderer object.
    """

    # Acquire the condition variable and notify the main thread
    # that a new frame is ready to render. This is required since
    # all rendering done by OpenCV needs to happen on the main thread.
    with renderer.frame_condition:
        renderer.frame = camera_frame.thermography_float
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    """Async callback fired whenever a camera event occurs.

    Parameters
    ----------
    camera: SeekCamera
        Reference to the camera on which an event occurred.
    event_type: SeekCameraManagerEvent
        Enumerated type indicating the type of event that occurred.
    event_status: Optional[SeekCameraError]
        Optional exception type. It will be a non-None derived instance of
        SeekCameraError if the event_type is SeekCameraManagerEvent.ERROR.
    renderer: Renderer
        User defined data passed to the callback. This can be anything
        but in this case it is a reference to the Renderer object.
    """
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return

        # Claim the renderer.
        # This is required in case of multiple cameras.
        renderer.busy = True
        renderer.camera = camera
        
        # Indicate the first frame has not come in yet.
        # This is required to properly resize the rendering window.
        renderer.first_frame = True

        # Set a custom color palette.
        # Other options can set in a similar fashion.
        camera.color_palette = SeekCameraColorPalette.TYRIAN

        # Start imaging and provide a custom callback to be called
        # every time a new frame is received.
        camera.register_frame_available_callback(on_frame, renderer)
        # camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
        # Check that the camera disconnecting is one actually associated with
        # the renderer. This is required in case of multiple cameras.
        if renderer.camera == camera:
            # Stop imaging and reset all the renderer state.
            camera.capture_session_stop()
            renderer.camera = None
            renderer.frame = None
            renderer.busy = False

    elif event_type == SeekCameraManagerEvent.ERROR:
        print("{}: {}".format(str(event_status), camera.chipid))

    elif event_type == SeekCameraManagerEvent.READY_TO_PAIR:
        return

selected_point = (-1, -1)
selected_blue_value = -1
def main():
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    
    
    # Create a context structure responsible for managing all connected USB cameras.
    # Cameras with other IO types can be managed by using a bitwise or of the
    # SeekCameraIOType enum cases.
    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        # Start listening for events.
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)

        while True:
            # Wait a maximum of 150ms for each frame to be received.
            # A condition variable is used to synchronize the access to the renderer;
            # it will be notified by the user defined frame available callback thread.
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    thermography_float_data = renderer.frame.data
                    def thermal_to_rgb(thermography_data):
                        # Normalize temperature values to the range [0, 1]
                        normalized_data = (thermography_data - np.min(thermography_data)) / (np.max(thermography_data) - np.min(thermography_data))
                        from matplotlib import pyplot as plt
                        # Use a colormap to map normalized temperatures to RGB values
                        colormap = plt.get_cmap('viridis')  # You can choose other colormaps like viridis, jet, plasma, cividis, inferno, magma, gray, bone, coolwarm, seismic, rainbow, cubehelix, twilight, ocean, spectral, YlGnBu, YlOrRd, RdYlBu, PiYG, PuOr, PRGn, RdGy, BrBG, RdBu, and GnBu..
                        rgb_data = (colormap(normalized_data)[:, :, :3] * 255).astype(np.uint8)

                        return rgb_data

                    img = thermal_to_rgb(thermography_float_data)


                    # Resize the rendering window.
                    if renderer.first_frame:
                        (height, width,_) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    # Render the image to the window.
                    # def get_pixel_value(event, x, y, flags, param):
                    #     if event == cv2.EVENT_LBUTTONDOWN:
                    #         # Get the pixel value at the selected point
                    #         blue_value = img[y, x, 0]  # Assuming image is in BGR format, so 0 corresponds to blue channel

                    #         # Display the blue pixel value
                    #         print(f"Blue Pixel Value at ({x}, {y}): {blue_value}")

                    #         # Draw a circle at the selected point
                    #         cv2.circle(img, (x, y), 5, (0, 255, 0), -1)  # Green circle at selected point
                    #         cv2.putText(img, f'({x}, {y}) - Blue: {blue_value}', (x + 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                    #         # Update the image display
                    #         cv2.imshow(window_name, img)
                    def get_pixel_value(event, x, y, flags, param):
                        global selected_point, selected_blue_value

                        if event == cv2.EVENT_LBUTTONDOWN:
                            # Get the pixel value at the selected point
                            selected_blue_value = img[y, x, 0]  # Assuming image is in BGR format, so 0 corresponds to blue channel
                            selected_point = (x, y)
                            

                    if selected_point != (-1, -1):
                        
                        x, y = selected_point
                        cv2.circle(img, (x, y), 5, (0, 255, 0), -1)  # Green circle at selected point
                        # selected_blue_value = img[y, x, 0]
                        
                        temp_value = thermography_float_data[x][y]
                        print(temp_value,"555555555555555555555")
                        # SeekFrame(<seekcamera._clib.CSeekFrame object at 0x000001713AACDF40>, THERMOGRAPHY_FLOAT) 55555
                        
                        cv2.putText(img, f'({x}, {y}) - Blue: {temp_value}', (x + 10, y - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

                    cv2.setMouseCallback(window_name, get_pixel_value)
                    cv2.imshow(window_name, img)

            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            # Check if the window has been closed manually.
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()

