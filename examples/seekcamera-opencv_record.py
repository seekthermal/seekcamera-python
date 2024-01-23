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
import numpy
import PIL.Image
import os
import glob

from PIL import Image, ImageFont, ImageDraw

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCameraShutterMode,
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
        renderer.frame = camera_frame.color_argb8888
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
        camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

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

def bgra2rgb( bgra ):
    row, col, ch = bgra.shape

    assert ch == 4, 'ARGB image has 4 channels.'

    rgb = numpy.zeros( (row, col, 3), dtype='uint8' )
    # convert to rgb expected to generate the jpeg image
    rgb[:,:,0] = bgra[:,:,2]
    rgb[:,:,1] = bgra[:,:,1]
    rgb[:,:,2] = bgra[:,:,0]

    return rgb

def main():
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    fileName = "image"
    counter  = 100000
    capture  = False
    record   = False
    ts_first = 0
    ts_last  = 0
    frame_count = 0
   
    from PIL import Image
    from pathlib import Path
    for f in glob.glob(fileName + '*.jpg'):
        os.remove(f)

    print("\nuser controls:")
    print("c:    capture")
    print("r:    record")
    print("q:    quit")

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
                    img = renderer.frame.data

                    # Resize the rendering window.
                    if renderer.first_frame:
                        (height, width, _) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    # Render the image to the window.
                    cv2.imshow(window_name, img)

                    # if capture or recording, convert the frame image
                    # to RGB and generate the file.
                    # Currently counter is a big number to allow easy ordering
                    # of frames when recording.
                    if capture or record:
                        rgbimg = bgra2rgb(img)
                        frame_count += 1
                        im = Image.fromarray(rgbimg).convert('RGB')
                        jpgName = Path('.', fileName + str(counter)).with_suffix('.jpg')
                        im.save(jpgName)
                        counter += 1
                        capture = False
                        if record:                            
                            ts_last = renderer.frame.header.timestamp_utc_ns
                            if ts_first == 0:
                                ts_first = renderer.frame.header.timestamp_utc_ns                        
            # Process key events.
            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            if key == ord("c"):
                capture = True

            if key == ord("r"):
                if record == False:
                    record = True  
                    renderer.camera.shutter_mode = SeekCameraShutterMode.MANUAL
                    print("\nRecording! Press 'r' to stop recording")
                    print("Note: shutter is disabled while recording...so keep the videos relatively short")
                else:
                    # Stop the recording and squish all the jpeg files together
                    # and generate the .avi file.
                    record = False
                    renderer.camera.shutter_mode = SeekCameraShutterMode.AUTO
                    
                    time_s = (ts_last - ts_first)/1000000000                    
                    
                    print("\nRecording stopped and video is in myVideo.avi")
                    img_array = []
                    for filename in glob.glob('image*.jpg'):
                        img = cv2.imread(filename)
                        height, width, layers = img.shape
                        size = (width,height)
                        img_array.append(img)                        
                    out = cv2.VideoWriter('myVideo.avi', cv2.VideoWriter_fourcc(*'DIVX'), frame_count/time_s, size)
                    
                    frame_count = ts_first = ts_last = 0
                    
                    for i in range(len(img_array)):
                        out.write(img_array[i])
                    out.release()

            # Check if the window has been closed manually.
            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
