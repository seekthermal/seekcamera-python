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

import ctypes
import os


# DLL handle
_cdll = None

# seekcamera_frame_available_callback_t
_SEEKCAMERA_FRAME_AVAILABLE_CALLBACK_T = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.py_object
)

# seekcamera_memory_access_callback_t
_SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_size_t, ctypes.py_object
)

# seekcamera_manager_event_callback_t
_SEEKCAMERA_MANAGER_EVENT_CALLBACK_T = ctypes.CFUNCTYPE(
    ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.py_object
)


def configure_dll():
    global _cdll

    if _cdll is not None:
        return

    min_runtime_version_major = 4
    min_runtime_version_minor = 1
    min_runtime_version_patch = 0

    if os.name == "nt":
        lib = "seekcamera.dll"

        if "SEEKTHERMAL_LIB_DIR" in os.environ:
            path = os.path.join(os.environ["SEEKTHERMAL_LIB_DIR"], lib)
            try:
                _cdll = ctypes.CDLL(path)
            except Exception:
                raise RuntimeError("Failed to load %s from %s" % (lib, path))
        else:
            basedir = os.path.join(
                "C:\\", "Program Files", "Seek Thermal", "Seek Thermal SDK"
            )

            versions = []
            subdirs = [d for d in os.scandir(basedir) if d.is_dir()]
            for d in subdirs:
                parts = d.name.split(".")
                if len(parts) == 3:
                    try:
                        major = int(parts[0])
                        minor = int(parts[1])
                        patch = int(parts[2])
                    except ValueError:
                        pass
                    else:
                        versions.append("%i.%i.%i" % (major, minor, patch))

            versions.sort()
            version = versions[-1]

            min_runtime_version = "%i.%i.%i" % (
                min_runtime_version_major,
                min_runtime_version_minor,
                min_runtime_version_patch,
            )

            if version < min_runtime_version:
                raise RuntimeError("Failed to locate suitable installed SDK version")

            path = os.path.join(basedir, version, "x64-windows", "lib", lib)

            try:
                _cdll = ctypes.CDLL(path)
            except Exception:
                raise RuntimeError("Failed to load %s from %s" % (lib, path))
    else:
        lib = "libseekcamera.so"

        if "SEEKTHERMAL_LIB_DIR" in os.environ:
            path = os.path.join(os.environ["SEEKTHERMAL_LIB_DIR"], lib)
            try:
                _cdll = ctypes.CDLL(path)
            except Exception:
                raise RuntimeError("Failed to import %s from %s" % (lib, path))
        else:
            try:
                _cdll = ctypes.CDLL(lib)
            except Exception:
                raise RuntimeError("Failed to load %s from default system paths" % lib)

    # seekcamera_version_get_major
    _cdll.seekcamera_version_get_major.restype = ctypes.c_uint32
    _cdll.seekcamera_version_get_major.argtypes = []

    # seekcamera_version_get_minor
    _cdll.seekcamera_version_get_minor.restype = ctypes.c_uint32
    _cdll.seekcamera_version_get_minor.argtypes = []

    # seekcamera_version_get_patch
    _cdll.seekcamera_version_get_patch.restype = ctypes.c_uint32
    _cdll.seekcamera_version_get_patch.argtypes = []

    # seekcamera_version_get_internal
    _cdll.seekcamera_version_get_internal.restype = ctypes.c_uint32
    _cdll.seekcamera_version_get_internal.argtypes = []

    # seekcamera_version_get_qualifier
    _cdll.seekcamera_version_get_qualifier.restype = ctypes.c_char_p
    _cdll.seekcamera_version_get_qualifier.argtypes = []

    def assert_runtime_version_met(version, min_version, name):
        if version < min_version:
            raise RuntimeError(
                "Library runtime %s version is insufficient (minimum: %i, got: %i)"
                % (name, min_version, version)
            )

    assert_runtime_version_met(
        cseekcamera_version_get_major(), min_runtime_version_major, "major"
    )

    assert_runtime_version_met(
        cseekcamera_version_get_minor(), min_runtime_version_minor, "minor"
    )

    assert_runtime_version_met(
        cseekcamera_version_get_patch(), min_runtime_version_patch, "patch"
    )

    # seekcamera_manager_create
    _cdll.seekcamera_manager_create.restype = ctypes.c_int32
    _cdll.seekcamera_manager_create.argtypes = [
        ctypes.POINTER(ctypes.c_void_p),
        ctypes.c_uint32,
    ]

    # seekcamera_manager_destroy
    _cdll.seekcamera_manager_destroy.restype = ctypes.c_int32
    _cdll.seekcamera_manager_destroy.argtypes = [ctypes.POINTER(ctypes.c_void_p)]

    # seekcamera_manager_get_event_str
    _cdll.seekcamera_manager_get_event_str.restype = ctypes.c_char_p
    _cdll.seekcamera_manager_get_event_str.argtypes = [ctypes.c_int32]

    # seekcamera_error_get_str
    _cdll.seekcamera_error_get_str.restype = ctypes.c_char_p
    _cdll.seekcamera_error_get_str.argtypes = [ctypes.c_int32]

    # seekcamera_get_io_type
    _cdll.seekcamera_get_io_type.restype = ctypes.c_int32
    _cdll.seekcamera_get_io_type.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_get_io_properties
    _cdll.seekcamera_get_io_properties.restype = ctypes.c_int32
    _cdll.seekcamera_get_io_properties.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(CSeekCameraIOProperties),
    ]

    # seekcamera_get_chipid
    _cdll.seekcamera_get_chipid.restype = ctypes.c_int32
    _cdll.seekcamera_get_chipid.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_char * 16),
    ]

    # seekcamera_get_serial_number
    _cdll.seekcamera_get_serial_number.restype = ctypes.c_int32
    _cdll.seekcamera_get_serial_number.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_char * 16),
    ]

    # seekcamera_get_core_part_number
    _cdll.seekcamera_get_core_part_number.restype = ctypes.c_int32
    _cdll.seekcamera_get_core_part_number.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_char * 32),
    ]

    # seekcamera_get_firmware_version
    _cdll.seekcamera_get_firmware_version.restype = ctypes.c_int32
    _cdll.seekcamera_get_firmware_version.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(CSeekCameraFirmwareVersion),
    ]

    # seekcamera_get_thermography_window
    _cdll.seekcamera_get_thermography_window.restype = ctypes.c_int32
    _cdll.seekcamera_get_thermography_window.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
        ctypes.POINTER(ctypes.c_size_t),
    ]

    # seekcamera_set_thermography_window
    _cdll.seekcamera_set_thermography_window.restype = ctypes.c_int32
    _cdll.seekcamera_set_thermography_window.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
    ]

    # seekcamera_update_firmware
    _cdll.seekcamera_update_firmware.restype = ctypes.c_int32
    _cdll.seekcamera_update_firmware.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_store_calibration_data
    _cdll.seekcamera_store_calibration_data.restype = ctypes.c_int32
    _cdll.seekcamera_store_calibration_data.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_store_flat_scene_correction
    _cdll.seekcamera_store_flat_scene_correction.restype = ctypes.c_int32
    _cdll.seekcamera_store_flat_scene_correction.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_delete_flat_scene_correction
    _cdll.seekcamera_delete_flat_scene_correction.restype = ctypes.c_int32
    _cdll.seekcamera_delete_flat_scene_correction.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_load_app_resources
    _cdll.seekcamera_load_app_resources.restype = ctypes.c_int32
    _cdll.seekcamera_load_app_resources.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_byte),
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_store_app_resources
    _cdll.seekcamera_store_app_resources.restype = ctypes.c_int32
    _cdll.seekcamera_store_app_resources.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_byte),
        ctypes.c_size_t,
        _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_capture_session_start
    _cdll.seekcamera_capture_session_start.restype = ctypes.c_int32
    _cdll.seekcamera_capture_session_start.argtypes = [ctypes.c_void_p, ctypes.c_uint32]

    # seekcamera_capture_session_stop
    _cdll.seekcamera_capture_session_stop.restype = ctypes.c_int32
    _cdll.seekcamera_capture_session_stop.argtypes = [ctypes.c_void_p]

    # seekcamera_register_frame_available_callback
    _cdll.seekcamera_register_frame_available_callback.restype = ctypes.c_int32
    _cdll.seekcamera_register_frame_available_callback.argtypes = [
        ctypes.c_void_p,
        _SEEKCAMERA_FRAME_AVAILABLE_CALLBACK_T,
        ctypes.py_object,
    ]

    # seekcamera_get_color_palette
    _cdll.seekcamera_get_color_palette.restype = ctypes.c_int32
    _cdll.seekcamera_get_color_palette.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_set_color_palette
    _cdll.seekcamera_set_color_palette.restype = ctypes.c_int32
    _cdll.seekcamera_set_color_palette.argtypes = [ctypes.c_void_p, ctypes.c_int32]

    # seekcamera_set_color_palette_data
    _cdll.seekcamera_set_color_palette_data.restype = ctypes.c_int32
    _cdll.seekcamera_set_color_palette_data.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.POINTER(CSeekCameraColorPaletteDataEntry * 256),
    ]

    # seekcamera_get_agc_mode
    _cdll.seekcamera_get_agc_mode.restype = ctypes.c_int32
    _cdll.seekcamera_get_agc_mode.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_set_agc_mode
    _cdll.seekcamera_set_agc_mode.restype = ctypes.c_int32
    _cdll.seekcamera_set_agc_mode.argtypes = [ctypes.c_void_p, ctypes.c_int32]

    # seekcamera_get_shutter_mode
    _cdll.seekcamera_get_shutter_mode.restype = ctypes.c_int32
    _cdll.seekcamera_get_shutter_mode.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_set_shutter_mode
    _cdll.seekcamera_set_shutter_mode.restype = ctypes.c_int32
    _cdll.seekcamera_set_shutter_mode.argtypes = [ctypes.c_void_p, ctypes.c_int32]

    # seekcamera_get_temperature_unit
    _cdll.seekcamera_get_temperature_unit.restype = ctypes.c_int32
    _cdll.seekcamera_get_temperature_unit.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_set_temperature_unit
    _cdll.seekcamera_set_temperature_unit.restype = ctypes.c_int32
    _cdll.seekcamera_set_temperature_unit.argtypes = [ctypes.c_void_p, ctypes.c_int32]

    # seekcamera_shutter_trigger
    _cdll.seekcamera_shutter_trigger.restype = ctypes.c_int32
    _cdll.seekcamera_shutter_trigger.argtypes = [ctypes.c_void_p]

    # seekcamera_get_scene_emissivity
    _cdll.seekcamera_get_scene_emissivity.restype = ctypes.c_int32
    _cdll.seekcamera_get_scene_emissivity.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_float),
    ]

    # seekcamera_set_scene_emissivity
    _cdll.seekcamera_set_scene_emissivity.restype = ctypes.c_int32
    _cdll.seekcamera_set_scene_emissivity.argtypes = [ctypes.c_void_p, ctypes.c_float]

    # seekcamera_get_thermography_offset
    _cdll.seekcamera_get_thermography_offset.restype = ctypes.c_int32
    _cdll.seekcamera_get_thermography_offset.argtypes = [
        ctypes.c_void_p,
        ctypes.POINTER(ctypes.c_float),
    ]

    # seekcamera_set_thermography_offset
    _cdll.seekcamera_set_thermography_offset.restype = ctypes.c_int32
    _cdll.seekcamera_set_thermography_offset.argtypes = [
        ctypes.c_void_p,
        ctypes.c_float,
    ]

    # seekcamera_set_filter_state
    _cdll.seekcamera_set_filter_state.restype = ctypes.c_int32
    _cdll.seekcamera_set_filter_state.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.c_int32,
    ]

    # seekcamera_get_filter_state
    _cdll.seekcamera_get_filter_state.restype = ctypes.c_int32
    _cdll.seekcamera_get_filter_state.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_int32),
    ]

    # seekcamera_get_frame_by_format
    _cdll.seekcamera_frame_get_frame_by_format.restype = ctypes.c_int32
    _cdll.seekcamera_frame_get_frame_by_format.argtypes = [
        ctypes.c_void_p,
        ctypes.c_int32,
        ctypes.POINTER(ctypes.c_void_p),
    ]

    # seekframe_get_width
    _cdll.seekframe_get_width.restype = ctypes.c_size_t
    _cdll.seekframe_get_width.argtypes = [ctypes.c_void_p]

    # seekframe_get_height
    _cdll.seekframe_get_height.restype = ctypes.c_size_t
    _cdll.seekframe_get_height.argtypes = [ctypes.c_void_p]

    # seekframe_get_channels
    _cdll.seekframe_get_channels.restype = ctypes.c_size_t
    _cdll.seekframe_get_channels.argtypes = [ctypes.c_void_p]

    # seekframe_get_pixel_depth
    _cdll.seekframe_get_pixel_depth.restype = ctypes.c_size_t
    _cdll.seekframe_get_pixel_depth.argtypes = [ctypes.c_void_p]

    # seekframe_get_pixel_padding
    _cdll.seekframe_get_pixel_padding.restype = ctypes.c_size_t
    _cdll.seekframe_get_pixel_padding.argtypes = [ctypes.c_void_p]

    # seekframe_get_line_stride
    _cdll.seekframe_get_line_stride.restype = ctypes.c_size_t
    _cdll.seekframe_get_line_stride.argtypes = [ctypes.c_void_p]

    # seekframe_get_line_padding
    _cdll.seekframe_get_line_padding.restype = ctypes.c_size_t
    _cdll.seekframe_get_line_padding.argtypes = [ctypes.c_void_p]

    # seekframe_get_data_size
    _cdll.seekframe_get_data_size.restype = ctypes.c_size_t
    _cdll.seekframe_get_data_size.argtypes = [ctypes.c_void_p]

    # seekframe_get_data
    _cdll.seekframe_get_data.restype = ctypes.c_void_p
    _cdll.seekframe_get_data.argtypes = [ctypes.c_void_p]

    # seekframe_get_row
    _cdll.seekframe_get_row.restype = ctypes.c_void_p
    _cdll.seekframe_get_row.argtypes = [ctypes.c_void_p, ctypes.c_size_t]

    # seekframe_get_pixel
    _cdll.seekframe_get_pixel.restype = ctypes.c_void_p
    _cdll.seekframe_get_pixel.argtypes = [
        ctypes.c_void_p,
        ctypes.c_size_t,
        ctypes.c_size_t,
    ]

    # seekframe_is_empty
    _cdll.seekframe_is_empty.restype = ctypes.c_bool
    _cdll.seekframe_is_empty.argtypes = [ctypes.c_void_p]

    # seekframe_get_header_size
    _cdll.seekframe_get_header_size.restype = ctypes.c_size_t
    _cdll.seekframe_get_header_size.argtypes = [ctypes.c_void_p]

    # seekframe_get_header
    _cdll.seekframe_get_header.restype = ctypes.POINTER(CSeekCameraFrameHeader)
    _cdll.seekframe_get_header.argtypes = [ctypes.c_void_p]


class CSeekCameraColorPaletteDataEntry(ctypes.Structure):
    _fields_ = [
        ("b", ctypes.c_uint8),
        ("g", ctypes.c_uint8),
        ("r", ctypes.c_uint8),
        ("a", ctypes.c_uint8),
    ]


class CSeekCameraFrameHeader(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("sentinel", ctypes.c_uint32),
        ("version", ctypes.c_uint8),
        ("type", ctypes.c_uint32),
        ("width", ctypes.c_uint16),
        ("height", ctypes.c_uint16),
        ("channels", ctypes.c_uint8),
        ("pixel_depth", ctypes.c_uint8),
        ("pixel_padding", ctypes.c_uint8),
        ("line_stride", ctypes.c_uint16),
        ("line_padding", ctypes.c_uint16),
        ("header_size", ctypes.c_uint16),
        ("timestamp_utc_ns", ctypes.c_uint64),
        ("chipid", ctypes.c_char * 16),
        ("serial_number", ctypes.c_char * 16),
        ("core_part_number", ctypes.c_char * 32),
        ("firmware_version", ctypes.c_uint8 * 4),
        ("io_type", ctypes.c_uint8),
        ("fpa_frame_count", ctypes.c_uint32),
        ("fpa_diode_count", ctypes.c_uint32),
        ("environment_temperature", ctypes.c_float),
        ("thermography_min_x", ctypes.c_uint16),
        ("thermography_min_y", ctypes.c_uint16),
        ("thermography_min_value", ctypes.c_float),
        ("thermography_max_x", ctypes.c_uint16),
        ("thermography_max_y", ctypes.c_uint16),
        ("thermography_max_value", ctypes.c_float),
        ("thermography_spot_x", ctypes.c_uint16),
        ("thermography_spot_y", ctypes.c_uint16),
        ("thermography_spot_value", ctypes.c_float),
        ("reserved", ctypes.c_uint8 * 1913),
    ]


class CSeekCameraUSBIOProperties(ctypes.Structure):
    _fields_ = [("bus_number", ctypes.c_uint8), ("port_numbers", ctypes.c_uint8 * 8)]


class CSeekCameraSPIIOProperties(ctypes.Structure):
    _fields_ = [("bus_number", ctypes.c_uint8), ("cs_number", ctypes.c_uint8)]


class CSeekCameraIOProperties(ctypes.Structure):
    class Properties(ctypes.Union):
        _fields_ = [
            ("usb", CSeekCameraUSBIOProperties),
            ("spi", CSeekCameraSPIIOProperties),
        ]

    _fields_ = [("type", ctypes.c_int32), ("properties", Properties)]


class CSeekCameraFirmwareVersion(ctypes.Structure):
    _fields_ = [
        ("product", ctypes.c_uint8),
        ("variant", ctypes.c_uint8),
        ("major", ctypes.c_uint8),
        ("minor", ctypes.c_uint8),
    ]


def _default_memory_access_callback(_progress, _user_data):
    pass


def _memory_access_callback(callback):
    if callback is None:
        return _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T(_default_memory_access_callback)
    return _SEEKCAMERA_MEMORY_ACCESS_CALLBACK_T(callback)


class CSeekCameraManager(object):
    def __init__(self):
        self.pointer = ctypes.c_void_p()
        self.user_data = None
        self.event_callback = None
        self.event_callback_cdll = ctypes.CFUNCTYPE(None)
        self.cameras = []


class CSeekCamera(object):
    def __init__(self, camera):
        self.pointer = ctypes.c_void_p(camera)
        self.user_data = None
        self.frame_available_callback = None
        self.frame_available_callback_cdll = ctypes.CFUNCTYPE(None)

    def __eq__(self, other):
        this_cid, _ = cseekcamera_get_chipid(self)
        other_cid, _ = cseekcamera_get_chipid(other)
        return this_cid.value.decode("utf-8") == other_cid.value.decode("utf-8")


class CSeekCameraFrame(object):
    def __init__(self, camera_frame):
        self.pointer = ctypes.c_void_p(camera_frame)


class CSeekFrame(object):
    def __init__(self, frame):
        self.pointer = frame


def cseekcamera_manager_create(discovery_mode):
    manager = CSeekCameraManager()
    status = _cdll.seekcamera_manager_create(
        ctypes.pointer(manager.pointer), ctypes.c_uint32(discovery_mode)
    )
    return manager, status


def cseekcamera_manager_destroy(manager):
    return _cdll.seekcamera_manager_destroy(ctypes.pointer(manager.pointer))


def cseekcamera_manager_register_event_callback(manager, callback, user_data):
    manager.user_data = user_data
    manager.event_callback = callback

    def _event_callback(camera, event_type, event_status, _user_data):
        camera_ = CSeekCamera(camera)

        if event_type == 0:  # Connect
            manager.cameras.append(camera_)
            manager.event_callback(camera_, event_type, event_status, manager.user_data)
        elif event_type == 1:  # Disconnect
            manager.event_callback(camera_, event_type, event_status, manager.user_data)
            manager.cameras.remove(camera_)
        elif event_type == 2:  # Error
            manager.event_callback(camera_, event_type, event_status, manager.user_data)
        elif event_type == 3:  # Ready to pair
            manager.cameras.append(camera_)
            manager.event_callback(camera_, event_type, event_status, manager.user_data)

    manager.event_callback_cdll = _SEEKCAMERA_MANAGER_EVENT_CALLBACK_T(_event_callback)

    return _cdll.seekcamera_manager_register_event_callback(
        manager.pointer,
        manager.event_callback_cdll,
        ctypes.py_object(manager.user_data),
    )


def cseekcamera_manager_get_event_str(event):
    c_str = _cdll.seekcamera_manager_get_event_str(ctypes.c_int(event))
    return c_str


def cseekcamera_error_get_str(status):
    return _cdll.seekcamera_error_get_str(status)


def cseekcamera_get_io_type(camera):
    io_type = ctypes.c_int32()
    status = _cdll.seekcamera_get_io_type(camera.pointer, ctypes.byref(io_type))
    return io_type, status


def cseekcamera_get_io_properties(camera):
    properties = CSeekCameraIOProperties()
    status = _cdll.seekcamera_get_io_properties(
        camera.pointer, ctypes.pointer(properties)
    )

    return properties, status


def cseekcamera_get_chipid(camera):
    chipid = (ctypes.c_char * 16)()
    status = _cdll.seekcamera_get_chipid(camera.pointer, ctypes.pointer(chipid))
    return chipid, status


def cseekcamera_get_serial_number(camera):
    serial_number = (ctypes.c_char * 16)()
    status = _cdll.seekcamera_get_serial_number(
        camera.pointer, ctypes.pointer(serial_number)
    )

    return serial_number, status


def cseekcamera_get_core_part_number(camera):
    core_part_number = (ctypes.c_char * 32)()
    status = _cdll.seekcamera_get_core_part_number(
        camera.pointer, ctypes.pointer(core_part_number)
    )
    return core_part_number, status


def cseekcamera_get_firmware_version(camera):
    firmware_version = CSeekCameraFirmwareVersion()
    status = _cdll.seekcamera_get_firmware_version(
        camera.pointer, ctypes.pointer(firmware_version)
    )

    return firmware_version, status


def cseekcamera_get_thermography_window(camera):
    x = ctypes.c_size_t()
    y = ctypes.c_size_t()
    w = ctypes.c_size_t()
    h = ctypes.c_size_t()
    status = _cdll.seekcamera_get_thermography_window(
        camera.pointer,
        ctypes.byref(x),
        ctypes.byref(y),
        ctypes.byref(w),
        ctypes.byref(h),
    )

    return x, y, w, h, status


def cseekcamera_set_thermography_window(camera, x, y, w, h):
    status = _cdll.seekcamera_set_thermography_window(
        camera.pointer,
        ctypes.c_size_t(x),
        ctypes.c_size_t(y),
        ctypes.c_size_t(w),
        ctypes.c_size_t(h),
    )

    return status


def cseekcamera_update_firmware(camera, upgrade_file, callback, user_data):
    path = ctypes.c_char_p(upgrade_file.encode("utf-8"))
    return _cdll.seekcamera_update_firmware(
        camera.pointer,
        path,
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )


def cseekcamera_store_calibration_data(camera, source_dir, callback, user_data):
    path = ctypes.c_char_p()
    if source_dir:
        path = ctypes.c_char_p(source_dir.encode("utf-8"))

    return _cdll.seekcamera_store_calibration_data(
        camera.pointer,
        path,
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )


def cseekcamera_store_flat_scene_correction(camera, fsc_id, callback, user_data):
    return _cdll.seekcamera_store_flat_scene_correction(
        camera.pointer,
        ctypes.c_int32(fsc_id),
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )


def cseekcamera_delete_flat_scene_correction(camera, fsc_id, callback, user_data):
    return _cdll.seekcamera_delete_flat_scene_correction(
        camera.pointer,
        ctypes.c_int32(fsc_id),
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )


def cseekcamera_load_app_resources(camera, region, data_size, callback, user_data):
    data = (ctypes.c_byte * data_size)()
    status = _cdll.seekcamera_load_app_resources(
        camera.pointer,
        ctypes.c_int32(region),
        ctypes.pointer(data),
        ctypes.c_size_t(data_size),
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )

    return data, data_size, status


def cseekcamera_store_app_resources(
    camera, region, data, data_size, callback, user_data
):
    return _cdll.seekcamera_store_app_resources(
        camera.pointer,
        ctypes.c_int32(region),
        ctypes.pointer((ctypes.c_byte * data_size).from_buffer(data)),
        ctypes.c_size_t(data_size),
        _memory_access_callback(callback),
        ctypes.py_object(user_data),
    )


def cseekcamera_capture_session_start(camera, frame_format):
    return _cdll.seekcamera_capture_session_start(
        camera.pointer, ctypes.c_uint32(frame_format)
    )


def cseekcamera_capture_session_stop(camera):
    return _cdll.seekcamera_capture_session_stop(camera.pointer)


def cseekcamera_register_frame_available_callback(camera, callback, user_data):
    camera.user_data = user_data
    camera.event_callback = callback

    def _frame_available_callback(_camera, camera_frame, _user_data):
        camera.event_callback(camera, CSeekCameraFrame(camera_frame), camera.user_data)

    camera.event_callback_cdll = _SEEKCAMERA_FRAME_AVAILABLE_CALLBACK_T(
        _frame_available_callback
    )

    return _cdll.seekcamera_register_frame_available_callback(
        camera.pointer, camera.event_callback_cdll, ctypes.py_object(camera.user_data)
    )


def cseekcamera_get_color_palette(camera):
    palette = ctypes.c_int32()
    status = _cdll.seekcamera_get_color_palette(camera.pointer, ctypes.byref(palette))
    return palette, status


def cseekcamera_set_color_palette(camera, palette):
    return _cdll.seekcamera_set_color_palette(camera.pointer, ctypes.c_int32(palette))


def cseekcamera_set_color_palette_data(camera, palette, palette_data):
    return _cdll.seekcamera_set_color_palette_data(
        camera.pointer, ctypes.c_int32(palette), ctypes.byref(palette_data)
    )


def cseekcamera_get_agc_mode(camera):
    mode = ctypes.c_int32()
    status = _cdll.seekcamera_get_agc_mode(camera.pointer, ctypes.byref(mode))
    return mode, status


def cseekcamera_set_agc_mode(camera, mode):
    return _cdll.seekcamera_set_agc_mode(camera.pointer, ctypes.c_int32(mode))


def cseekcamera_get_shutter_mode(camera):
    mode = ctypes.c_int32()
    status = _cdll.seekcamera_get_shutter_mode(camera.pointer, ctypes.byref(mode))
    return mode, status


def cseekcamera_set_shutter_mode(camera, mode):
    return _cdll.seekcamera_set_shutter_mode(camera.pointer, ctypes.c_int32(mode))


def cseekcamera_shutter_trigger(camera):
    return _cdll.seekcamera_shutter_trigger(camera.pointer)


def cseekcamera_get_temperature_unit(camera):
    unit = ctypes.c_int32()
    status = _cdll.seekcamera_get_temperature_unit(camera.pointer, ctypes.byref(unit))
    return unit, status


def cseekcamera_set_temperature_unit(camera, unit):
    return _cdll.seekcamera_set_temperature_unit(camera.pointer, ctypes.c_int32(unit))


def cseekcamera_get_scene_emissivity(camera):
    emissivity = ctypes.c_float()
    status = _cdll.seekcamera_get_scene_emissivity(
        camera.pointer, ctypes.byref(emissivity)
    )

    return emissivity, status


def cseekcamera_set_scene_emissivity(camera, emissivity):
    return _cdll.seekcamera_set_scene_emissivity(
        camera.pointer, ctypes.c_float(emissivity)
    )


def cseekcamera_get_thermography_offset(camera):
    offset = ctypes.c_float()
    status = _cdll.seekcamera_get_thermography_offset(
        camera.pointer, ctypes.byref(offset)
    )

    return offset, status


def cseekcamera_set_thermography_offset(camera, offset):
    return _cdll.seekcamera_set_thermography_offset(
        camera.pointer, ctypes.c_float(offset)
    )


def cseekcamera_get_gradient_correction_filter_enable(camera):
    enable = ctypes.c_bool()
    status = _cdll.seekcamera_get_gradient_correction_filter_enable(
        camera.pointer, ctypes.byref(enable)
    )

    return enable, status


def cseekcamera_set_gradient_correction_filter_enable(camera, enable):
    return _cdll.seekcamera_set_gradient_correction_filter_enable(
        camera.pointer, ctypes.c_bool(enable)
    )


def cseekcamera_get_flat_scene_correction_filter_enable(camera):
    enable = ctypes.c_bool()
    status = _cdll.seekcamera_get_flat_scene_correction_filter_enable(
        camera.pointer, ctypes.byref(enable)
    )

    return enable, status


def cseekcamera_set_flat_scene_correction_filter_enable(camera, enable):
    return _cdll.seekcamera_set_flat_scene_correction_filter_enable(
        camera.pointer, ctypes.c_bool(enable)
    )


def cseekcamera_set_filter_state(camera, filter_type, filter_state):
    return _cdll.seekcamera_set_filter_state(
        camera.pointer, ctypes.c_int32(filter_type), ctypes.c_int32(filter_state)
    )


def cseekcamera_get_filter_state(camera, filter_type):
    filter_state = ctypes.c_int32()
    status = _cdll.seekcamera_get_filter_state(
        camera.pointer, ctypes.c_int32(filter_type), ctypes.byref(filter_state)
    )

    return filter_state, status


def cseekcamera_frame_get_frame_by_format(camera_frame, fmt):
    frame = ctypes.c_void_p()
    status = _cdll.seekcamera_frame_get_frame_by_format(
        camera_frame.pointer, ctypes.c_int32(fmt), ctypes.pointer(frame)
    )

    return CSeekFrame(frame), status


def cseekcamera_version_get_major():
    return _cdll.seekcamera_version_get_major()


def cseekcamera_version_get_minor():
    return _cdll.seekcamera_version_get_minor()


def cseekcamera_version_get_patch():
    return _cdll.seekcamera_version_get_patch()


def cseekcamera_version_get_internal():
    return _cdll.seekcamera_version_get_internal()


def cseekcamera_version_get_qualifier():
    return _cdll.seekcamera_version_get_qualifier()


def cseekframe_get_width(frame):
    return _cdll.seekframe_get_width(frame.pointer)


def cseekframe_get_height(frame):
    return _cdll.seekframe_get_height(frame.pointer)


def cseekframe_get_channels(frame):
    return _cdll.seekframe_get_channels(frame.pointer)


def cseekframe_get_pixel_depth(frame):
    return _cdll.seekframe_get_pixel_depth(frame.pointer)


def cseekframe_get_pixel_padding(frame):
    return _cdll.seekframe_get_pixel_padding(frame.pointer)


def cseekframe_get_line_stride(frame):
    return _cdll.seekframe_get_line_stride(frame.pointer)


def cseekframe_get_line_padding(frame):
    return _cdll.seekframe_get_line_padding(frame.pointer)


def cseekframe_get_data_size(frame):
    return _cdll.seekframe_get_data_size(frame.pointer)


def cseekframe_get_data(frame):
    return _cdll.seekframe_get_data(frame.pointer)


def cseekframe_get_row(frame, y):
    return _cdll.seekframe_get_row(frame.pointer, ctypes.c_size_t(y))


def cseekframe_get_pixel(frame, x, y):
    return _cdll.seekframe_get_pixel(
        frame.pointer, ctypes.c_size_t(x), ctypes.c_size_t(y)
    )


def cseekframe_is_empty(frame):
    return _cdll.seekframe_is_empty(frame.pointer)


def cseekframe_get_header_size(frame):
    return _cdll.seekframe_get_header_size(frame.pointer)


def cseekframe_get_header(frame):
    return _cdll.seekframe_get_header(frame.pointer)
