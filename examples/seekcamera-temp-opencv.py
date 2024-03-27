#!/usr/bin/env python3

from threading import Condition

import cv2

from seekcamera import (
    SeekCameraIOType,
    SeekCameraColorPalette,
    SeekCameraManager,
    SeekCameraManagerEvent,
    SeekCameraFrameFormat,
    SeekCamera,
    SeekFrame, SeekCameraShutterMode, SeekCameraAGCMode, SeekCameraTemperatureUnit
)

class Renderer:
    def __init__(self):
        self.busy = False
        self.frame = SeekFrame()
        self.camera = SeekCamera()
        self.frame_condition = Condition()
        self.first_frame = True


def on_frame(_camera, camera_frame, renderer):
    with renderer.frame_condition:
        renderer.frame1 = camera_frame.thermography_float
        renderer.frame = camera_frame.color_argb8888
        renderer.frame_condition.notify()


def on_event(camera, event_type, event_status, renderer):
    print("{}: {}".format(str(event_type), camera.chipid))

    if event_type == SeekCameraManagerEvent.CONNECT:
        if renderer.busy:
            return
        renderer.busy = True
        renderer.camera = camera
        renderer.first_frame = True
        camera.color_palette = SeekCameraColorPalette.TYRIAN
        camera.shutter_mode = SeekCameraShutterMode.MANUAL
        camera.agMode =  SeekCameraAGCMode.LINEAR
        camera.tempunit = SeekCameraTemperatureUnit.CELSIUS
        camera.register_frame_available_callback(on_frame, renderer)
        camera.capture_session_start(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT | SeekCameraFrameFormat.COLOR_ARGB8888)
        # camera.capture_session_start(SeekCameraFrameFormat.COLOR_ARGB8888)

    elif event_type == SeekCameraManagerEvent.DISCONNECT:
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

def on_click(event, x, y, p1, temp_params):
    temp,img = temp_params
    if event == cv2.EVENT_LBUTTONDOWN:
        print("Pixel Temperature is: ", temp[y, x]," °C. At coordinate: ",x, y)
        cv2.circle(img, (x, y), 3, (0, 0, 0), -1)
        cv2.imshow("Seek Thermal - Python OpenCV Sample", img)

def main():
    window_name = "Seek Thermal - Python OpenCV Sample"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    with SeekCameraManager(SeekCameraIOType.USB) as manager:
        renderer = Renderer()
        manager.register_event_callback(on_event, renderer)


        while True:
            with renderer.frame_condition:
                if renderer.frame_condition.wait(150.0 / 1000.0):
                    img = renderer.frame.data
                    temp = renderer.frame1.data

                    if renderer.first_frame:
                        (height, width,_ ) = img.shape
                        cv2.resizeWindow(window_name, width * 2, height * 2)
                        renderer.first_frame = False

                    cv2.setMouseCallback(window_name, on_click,(temp,img))
                    cv2.imshow(window_name, img)

            key = cv2.waitKey(1)
            if key == ord("q"):
                break

            if not cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE):
                break

    cv2.destroyWindow(window_name)


if __name__ == "__main__":
    main()
