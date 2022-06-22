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
from enum import IntEnum

import numpy as np

from seekcamera import _clib
from seekcamera.error import (
    is_error,
    error_from_status,
    SeekCameraInvalidParameterError,
)


class SeekCameraManagerEvent(IntEnum):
    """Types of events used by the camera manager.

    Attributes
    ----------
    CONNECT: int
        Event case when a new camera connects in a paired state.
    DISONNECT: int
        Event case when an existing camera disconnects.
    ERROR:
        Event case when an existing camera has an error.
    READY_TO_PAIR: int
        Event case when a new camera connects in an unpaired state.
    """

    CONNECT = 0
    DISCONNECT = 1
    ERROR = 2
    READY_TO_PAIR = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraManagerEvent({})".format(self.value)


class SeekCameraIOType(IntEnum):
    """Types of IO protocols used by the cameras.

    Attributes
    ----------
    USB: int
        IO type case for USB cameras.
    SPI: int
        IO type case for SPI cameras.
    """

    USB = 0x01
    SPI = 0x02

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraIOType({})".format(self.value)


class SeekCameraFirmwareVersion(object):
    """Firmware version of a Seek camera.

    Attributes
    ----------
    product: int
        Product firmware version.
    variant: int
        Variant firmware version.
    major: int
        Major firmware version.
    minor: int
        Minor firmware version.
    """

    def __init__(self, product=0, variant=0, major=0, minor=0):
        self.product = product
        self.variant = variant
        self.major = major
        self.minor = minor

    def __str__(self):
        return "{}.{}.{}.{}".format(self.product, self.variant, self.major, self.minor)

    def __repr__(self):
        return "SeekCameraFirmwareVersion({}, {}, {}, {})".format(
            self.product, self.variant, self.major, self.minor
        )


class SeekCameraAppResourcesRegion(IntEnum):
    """Types of app resource regions.

    App resource regions are memory regions on the device that are reserved for
    customer use.

    Attributes
    ----------
    REGION_0: int
        Application resource region 0.
    REGION_1: int
        Application resource region 1.
    REGION_2: int
        Application resource region 2.
    """

    REGION_0 = 11
    REGION_1 = 12
    REGION_2 = 13

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraAppResourcesRegion({})".format(self.value)


class SeekCameraColorPalette(IntEnum):
    """Types of display color palettes.

    Attributes
    ----------
    WHITE_HOT: int
        Color palette type case for White Hot.
    BLACK_HOT: int
        Color palette type case for Black Hot.
    SPECTRA: int
        Color palette type case for Spectra.
    PRISM: int
        Color palette type case for Prism.
    TYRIAN: int
        Color palette type case for Tyrian.
    IRON: int
        Color palette type case for Iron.
    AMBER: int
        Color palette type case for Amber.
    HI: int
        Color palette type case for Hi.
    GREEN: int
        Color palette type case for Green.
    """

    WHITE_HOT = 0
    BLACK_HOT = 1
    SPECTRA = 2
    PRISM = 3
    TYRIAN = 4
    IRON = 5
    AMBER = 6
    HI = 7
    GREEN = 8
    USER_0 = 9
    USER_1 = 10
    USER_2 = 11
    USER_3 = 12
    USER_4 = 13

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraColorPalette({})".format(self.value)


class SeekCameraColorPaletteData(object):
    """Collection of color values used to colorize a thermal image.

    Each entry represents a component of a pixel. The values should be in ascending
    order going from coldest to hottest temperature. It has 256 distinct entries.
    Each entry is a tuple of color channels ordered as (b, g, r, a).

    Examples
    --------
    Creating a new color palette data object with default data (all zeros).
    >>> palette_data = SeekCameraColorPaletteData()

    Iterating the values of a color palette data object.
    >>> for index, value in enumerate(palette_data): print(value)

    Slicing a color palette object.
    >>> palette_data[1:4] = [(255, 0, 0, 0), (0, 255, 0, 0), (0, 0, 255, 0)]
    >>> print(palette_data[1:4])
    """

    def __init__(self, data=None):
        """Creates a color palette data object.

        Parameters
        ----------
        data: Optional[Iterable[Tuple[int, int, int, int]]]
            Collection of tuples that specify the color values for the color palette.
            It should have length 256; the tuples should be specified in (b, g, r, a)
            order.
        """
        if data is None:
            data = [(0, 0, 0, 0)] * 256

        self._data = data
        self._data_iter = 0

    def __repr__(self):
        return "SeekCameraColorPaletteData({})".format(self._data)

    def __iter__(self):
        """Iterates through the color values in the color palette data.

        Returns
        -------
        SeekCameraColorPaletteData
            Reference to the color palette data object to iterate.
        """
        self._data_iter = 0
        return self

    def __next__(self):
        """Gets the next color value in the current iteration.

        Returns
        -------
        Tuple[int, int, int, int]
            The next color palette value in (b, g, r, a) order.

        Raises
        ------
        StopIteration
            If at the end of the collection.
        """
        if self._data_iter >= len(self):
            raise StopIteration

        result = self._data[self._data_iter]
        self._data_iter += 1
        return result

    def __getitem__(self, key):
        """Gets an color value or slice of color values.

        Parameters
        ----------
        key: Union[slice, int]
            Either a slice or a single index used to get the color values.

        Returns
        -------
        Union[List[Tuple[int, int, int, int]], Tuple[int, int, int, int]]
            Either a slice of color values or a single color value.
        """
        if isinstance(key, slice):
            return self._data[key.start : key.stop : key.step]
        else:
            return self._data[key]

    def __setitem__(self, key, data):
        """Sets an color value or slice of color values.

        Parameters
        ----------
        key: Union[slice, int]
            Either a slice or a single index used to set the color values.
        data: Union[List[Tuple[int, int, int, int]], Tuple[int, int, int, int]]
            Either a slice of color values or a single color value.
        """
        if isinstance(key, slice):
            self._data[key.start : key.stop : key.step] = data
        else:
            self._data[key] = data

    def __len__(self):
        """Gets the number of color values in the color palette data.

        Returns
        -------
        int
            Number of color values in the color palette data.
        """
        return len(self._data)


class SeekCameraAGCMode(IntEnum):
    """Types of automated gain correction (AGC) modes.

    Attributes
    ----------
    LINEAR: int
        AGC mode type case for linear min/max.
    HISTEQ:
        AGC mode type case for histogram equalization.
    """

    LINEAR = 0
    HISTEQ = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraAGCMode({})".format(self.value)


class SeekCameraLinearAGCLockMode(IntEnum):
    """Enumerated type representing types of lock modes used by Linear AGC.

    The input modes allow for the automatic, semi-automatic, or manually setting of
    the output AGC range bounds. Regardless of which method is used to set the bounds,
    the output range (i.e. the closed interval [0, 255]) will be evenly stretched
    between the bounding values.

    Attributes
    ----------
    AUTO: int
        Lock mode type case for automatic Linear AGC.
        The minimum and maximum will be determined from the lowest/highest scene values.
    MANUAL: int
        Lock mode type case for manual Linear AGC.
        Both minimum and maximum will be set by the user, as opposed to from the scene.
    MANUAL_MIN: int
        Lock mode type case for "manual min" Linear AGC.
        The minimum bound value will be set by the user; the maximum bound value will
        be determined from the highest scene value.
    MANUAL_MAX: int
        Lock mode type case for "manual max" Linear AGC.
        The minimum bound value will be determined from the lowest scene value;
        the maximum bound value will be set by the user.
    """

    AUTO = 0
    MANUAL = 1
    MANUAL_MIN = 2
    MANUAL_MAX = 3

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraLinearAGCLockMode({})".format(self.value)


class SeekCameraShutterMode(IntEnum):
    """Types of shutter modes.

    WARNING: Shutter mode is only applicable to Mosaic Cores.

    Attributes
    ----------
    AUTO: int
        Shutter mode type case for automatic shuttering. When automatic shuttering is
        enabled, the user does not need to manually trigger the shutter. This is the
        default shuttering mode.
    MANUAL: int
        Shutter mode type case for manual shuttering. When manual shuttering is
        enabled, the user is responsible for triggering the shutter.
    """

    AUTO = 0
    MANUAL = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraShutterMode({})".format(self.value)


class SeekCameraTemperatureUnit(IntEnum):
    """Types of temperature units.

    Attributes
    ----------
    CELSIUS: int
        Temperature unit type case for degrees Celsius. This is the default temperature
        unit.
    FAHRENHEIT: int
        Temperature unit type case for degrees Fahrenheit.
    KELVIN: int
        Temperature unit type case for degrees Kelvin.
    """

    CELSIUS = 0
    FAHRENHEIT = 1
    KELVIN = 2

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraTemperatureUnit({})".format(self.value)


class SeekCameraUSBIOProperties(object):
    """IO properties of USB cameras.

    Attributes
    ----------
    bus_number: int
        USB bus number on which the camera is connected.
    port_numbers: Optional[list[int]]
        USB port numbers on which the camera is connected. Valid port numbers are
        indicated by a value strictly greater than zero.
    """

    def __init__(self, bus_number=0, port_numbers=None):
        if port_numbers is None:
            port_numbers = [0] * 8
        self.bus_number = bus_number
        self.port_numbers = port_numbers

    def __repr__(self):
        return "SeekCameraUSBIOProperties({}, {})".format(
            self.bus_number, self.port_numbers
        )


class SeekCameraSPIIOProperties(object):
    """IO properties of SPI cameras.

    Attributes
    ----------
    bus_number: int
        SPI bus number on which the camera is connected. This field corresponds to the
        bus number set in the SPI configuration file.
    cs_number: int
        SPI chip select number on which the camera is connected. This field corresponds
        to the chip select (cs) number set in the SPI configuration file.
    """

    def __init__(self, bus_number=0, cs_number=0):
        self.bus_number = bus_number
        self.cs_number = cs_number

    def __repr__(self):
        return "SeekCameraSPIIoProperties({}, {})".format(
            self.bus_number, self.cs_number
        )


class SeekCameraIOProperties(object):
    """Generic IO properties of cameras.

    Attributes
    ----------
    type:
        IO type of the camera.
    usb: Optional[SeekCameraUSBIOProperties]
        Contains properties of USB cameras.
    spi: Optional[SeekCameraSPIIOProperties]
        Contains properties of SPI cameras.
    """

    def __init__(self, type_, usb=None, spi=None):
        if usb is None:
            usb = SeekCameraUSBIOProperties()

        if spi is None:
            spi = SeekCameraSPIIOProperties()

        self.type = type_
        self.usb = usb
        self.spi = spi

    def __repr__(self):
        return "SeekCameraIOProperties({}, {}, {})".format(
            self.type, self.usb, self.spi
        )


class SeekCameraFilter(IntEnum):
    """Enumerated type representing the controllable image processing filters.

    Attributes
    ----------
    GRADIENT_CORRECTION: int
        Filter responsible for correcting image gradient on all data pipelines. It is
        triggered automatically on flat scenes.
    FLAT_SCENE_CORRECTION: int
        Filter responsible for correcting non-uniformities on all data pipelines. It is
        stored explicitly by the user apriori.
    """

    GRADIENT_CORRECTION = 0
    FLAT_SCENE_CORRECTION = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraFilter({})".format(self.value)


class SeekCameraFilterState(IntEnum):
    """Enumerated type representing the possible states of an image processing filter.

    Attributes
    ----------
    DISABLED: int
        Filter state type case for a disabled filter.
    ENABLED: int
        Filter state type case for an enabled filter.
    """

    DISABLED = 0
    ENABLED = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraFilterState({})".format(self.value)


class SeekCameraHistEQAGCGainLimitFactorMode(IntEnum):
    """Enumerated type representing types of gain limit modes used by HistEQ AGC.

    Attributes
    ----------
    AUTO: int
        Gain limit factor mode type case for automatic gain limit factor control.
        The gain limit will be set by the user; all other gain limit factor settings will
        be controlled automatically.
    MANUAL: int
        Gain limit factor mode type case for manual gain limit factor control.
        The gain limit will be set by the user; all other gain limit factor settings will
        also be controlled by the user.
    """

    AUTO = 0
    MANUAL = 1

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraHistEQAGCGainLimitFactorMode({})".format(self.value)


class SeekCameraHistEQAGCPlateauRedistributionMode(IntEnum):
    """Enumerated type representing types of plateau redistribution modes used by HistEQ AGC.

     For control of the plateau threshold, see `SeekCamera.histeq_agc_plateau`.

    Attributes
    ----------
    DISABLED: int
        The default plateau redistribution mode.
        Pixels in any histogram bin that exceed the plateau threshold are discarded.
    ALL_BINS: int
        Pixels in any histogram bin that exceed that plateau threshold are
        redistributed evenly among all bins in the histogram.
    ACTIVE_BINS_ONLY: int
        Pixels in any histogram bin that exceed that plateau threshold are
        redistributed only among the active bins in the histogram.
        An active histogram bin is one which contains at least 1 pixel.
    """

    DISABLED = 0
    ALL_BINS = 1
    ACTIVE_BINS_ONLY = 2

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraHistEQAGCPlateauRedistributionMode({})".format(self.value)


class SeekCameraFlatSceneCorrectionID(IntEnum):
    """
    Enumerated type representing a unique flat scene correction (FSC) identifier.

    Attributes
    ----------
    ID_0: int
        Default flat scene correction ID. If previously stored, the FSC will be loaded
        and applied on startup.
    """

    ID_0 = 0

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraFlatSceneCorrectionID({})".format(self.value)


class SeekCameraManager(object):
    """Manages Seek cameras.

    It is the interface through which users can set discovery modes, register event
    callbacks, and access cameras. It is created and destroyed by the user.

    Methods
    -------
    register_event_callback(callback, user_data=None)
        Registers a user event callback function with the camera manager.
    """

    def __init__(self, discovery_mode):
        """Creates the camera manager responsible for managing Seek cameras.

        Parameters
        ----------
        discovery_mode: int
            Integer indicating the type of devices to be discovered. It corresponds to
            the enumerated IO type. That is, it is a value of IO type or it is a
            bitwise OR combination of the enum values.

        Raises
        ------
        SeekCameraError
            If an error occurs while creating the camera manager.
        """
        self._discovery_mode = discovery_mode

        self._user_data = None
        self._event_callback = None
        self._event_callback_ctypes = None
        self._cameras = []

        _clib.configure_dll()

        self._manager, status = _clib.cseekcamera_manager_create(discovery_mode)
        if is_error(status):
            raise error_from_status(status)

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.destroy()

    def __repr__(self):
        return "SeekCameraManager({})".format(repr(self._discovery_mode))

    def destroy(self):
        """Destroys and invalidates an existing camera manager.

        Raises
        ------
        SeekCameraError
            If an error occurs while destroying the camera manager.
        """
        status = _clib.cseekcamera_manager_destroy(self._manager)
        if is_error(status):
            raise error_from_status(status)

    def register_event_callback(self, callback, user_data=None):
        """Registers a user event callback function with the camera manager.

        The callback is fired every time the camera manager receives an event. Only one
        event callback is allowed to be registered per camera manager.

        Parameters
        ----------
        callback: callable
            User-defined callback function. The callback function will be called every
            time a connect, disconnect, or event occurrs.
        user_data: Optional
            Optional user-defined data which is provided to the callback.

        Raises
        ------
        SeekCameraInvalidParameterError
            If the callback is not callable.
        SeekCameraError
            If an error occurs while registering the event callback.
        """
        if not callable(callback):
            raise SeekCameraInvalidParameterError

        self._user_data = user_data
        self._event_callback = callback

        def _event_callback(camera, event_type, event_status, _user_data):
            camera_ = SeekCamera(camera)
            event_type_ = SeekCameraManagerEvent(event_type)

            if event_type_ == SeekCameraManagerEvent.CONNECT:
                self._cameras.append(camera)
                self._event_callback(camera_, event_type_, None, self._user_data)
            elif event_type_ == SeekCameraManagerEvent.DISCONNECT:
                self._event_callback(camera_, event_type_, None, self._user_data)
                self._cameras.remove(camera)
            elif event_type_ == SeekCameraManagerEvent.ERROR:
                error = error_from_status(event_status)
                self._event_callback(camera_, event_type_, error, self._user_data)
            elif event_type_ == SeekCameraManagerEvent.READY_TO_PAIR:
                self._cameras.append(camera)
                self._event_callback(camera_, event_type_, None, self._user_data)

        self._event_callback_ctypes = _event_callback
        status = _clib.cseekcamera_manager_register_event_callback(
            self._manager, self._event_callback_ctypes, self._user_data
        )

        if is_error(status):
            raise error_from_status(status)


class SeekCamera(object):
    """Represents a single Seek camera.

    It is the interface through which users can query device characteristics, receive
    frame data, receive thermography data, etc.

    Properties
    ----------
    io_type: SeekCameraIOType
        Gets the IO type of camera.
    io_properties: SeekCameraIOProperties
        Gets the IO properties of the camera.
    chipid: str
        Gets the chip identifier (CID) of the camera.
    serial_number: str
        Gets the serial number (SN) of the camera.
    core_part_number: str
        Gets the core part number (CPN) of the camera.
    firmware_version: str
        Gets the firmware version of the camera.
    thermography_window: tuple[int, int, int, int]
        Gets/sets the thermography window of the camera.
    color_palette: SeekCameraColorPalette
        Gets/sets the color palette.
    agc_mode: SeekCameraAGCMode
        Gets/sets the AGC mode.
    histeq_agc_plateau: float
        Gets/sets the plateau value used for HistEQ AGC.
    histeq_agc_plateau_redistribution_mode : SeekCameraHistEQAGCPlateauRedistributionMode
        Gets/sets the plateau redistribution mode used for HistEQ AGC.
    histeq_agc_gain_limit: float
        Gets/sets the gain limit value used for HistEQ AGC.
    histeq_agc_gain_limit_factor_mode: SeekCameraHistEQAGCGainLimitMode
        Gets/sets the state of the gain limit factor used for HistEQ AGC.
    histeq_agc_gain_limit_factor_xmax: int
        Gets/sets the xmax value (for gain limit factor) used for HistEQ AGC.
    histeq_agc_gain_limit_factor_ymin: float
        Gets/sets the ymin value (for gain limit factor) used for HistEQ AGC.
    histeq_agc_alpha_time: float
        Gets/sets the alpha time value HistEQ AGC.
    histeq_agc_trim_left: float
        Gets/sets the histogram left trim percentage used for HistEQ AGC.
    histeq_agc_trim_right: float
        Gets/sets the histogram right trim percentage used for HistEQ AGC.
    linear_agc_lock_mode: SeekCameraLinearAGCLock Mode
        Gets/sets the lock mode used for Linear AGC.
    linear_agc_lock_min: int
        Gets/sets the minimum lock value used for Linear AGC.
    linear_agc_lock_max: int
        Gets/sets the maximum lock value used for Linear AGC.
    shutter_mode: SeekCameraShutterMode
        Gets/sets the shutter mode.
    temperature_unit: SeekCameraTemperatureUnit
        Gets/sets the temperature unit.
    scene_emissivity: float
        Gets/sets the global scene emissivity.
    thermography_offset: float
        Gets the thermography offset.

    Methods
    -------
    update_firmware(upgrade_file, callback=None, user_data=None)
        Updates the camera firmware using an input firmware file on the host OS.
    store_calibration_data(source_dir, callback=None, user_data=None)
        Stores calibration data and pairs the camera.
    store_flat_scene_correction(fsc_id, callback=None, user_data=None)
        Stores a flat scene correction (FSC).
    delete_flat_scene_correction(fsc_id, callback=None, user_data=None)
        Deletes a flat scene correction (FSC).
    load_app_resources(region, data_size, callback=None, user_data=None)
        Loads application resources into host memory.
    store_app_resources(region, data, data_size, callback=None, user_data=None)
        Stores application resources to either the host or the device.
    capture_session_start(frame_format)
        Begins streaming frames of the specified output formats from the camera.
    capture_session_stop()
        Stops streaming frames from the camera.
    register_frame_available_callback(callback, user_data=None)
        Registers a user frame available callback function with the camera.
    shutter_trigger()
        Triggers the camera to shutter as soon as possible.
    set_color_palette_data(palette, palette_data)
        Sets the color palette data for a particular color palette.
    set_filter_state(filter_type, filter_state)
        Sets the state of an image processing filter.
    get_filter_state(filter_type)
        Gets the state of an image processing filter.
    """

    def __init__(self, camera=None):
        """Creates a new SeekCamera.

        Parameters
        ----------
        camera: Optional[CSeekCamera]
            Optional reference to the camera object type used by the C bindings.

        Raises
        ------
        SeekCameraInvalidParameterError
            If camera is specified and is not an instance of CSeekCamera.
        """
        if camera is None:
            camera = _clib.CSeekCamera(None)
        elif not isinstance(camera, _clib.CSeekCamera):
            raise SeekCameraInvalidParameterError

        self._camera = camera
        self._user_data = None
        self._frame_available_callback = None
        self._frame_available_callback_ctypes = None

    def __eq__(self, other):
        return self._camera == other._camera

    def __repr__(self):
        return "SeekCamera({})".format(self._camera)

    @property
    def io_type(self):
        """Gets the IO type of the camera.

        Returns
        -------
        SeekCameraIOType
            IO type of the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        io_type, status = _clib.cseekcamera_get_io_type(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraIOType(io_type.value)

    @property
    def io_properties(self):
        """Gets the IO properties of the camera.

        Returns
        -------
        SeekCameraIOProperties
            IO properties of the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        properties, status = _clib.cseekcamera_get_io_properties(self._camera)
        if is_error(status):
            raise error_from_status(status)

        if properties.type == SeekCameraIOType.SPI:
            spi = SeekCameraSPIIOProperties(
                properties.properties.spi.bus_number,
                properties.properties.spi.cs_number,
            )

            return SeekCameraIOProperties(SeekCameraIOType.SPI, spi=spi)

        elif properties.type == SeekCameraIOType.USB:
            usb = SeekCameraUSBIOProperties(
                properties.properties.usb.bus_number,
                properties.properties.usb.port_numbers[:],
            )

            return SeekCameraIOProperties(SeekCameraIOType.USB, usb=usb)

    @property
    def chipid(self):
        """Gets the chip identifier (CID) of the camera.

        Returns
        -------
        str
            CID of the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        cid, status = _clib.cseekcamera_get_chipid(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return cid.value.decode("utf-8")

    @property
    def serial_number(self):
        """Gets the serial number (SN) of the camera.

        Returns
        -------
        str
            SN of the camera.

        Raises
        ------
        SeekCameraError
            If an error ocurrs.
        """
        sn, status = _clib.cseekcamera_get_serial_number(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return sn.value.decode("utf-8")

    @property
    def core_part_number(self):
        """Gets the core part number (CPN) of the camera.

        Returns
        -------
        str
            CPN of the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        cpn, status = _clib.cseekcamera_get_core_part_number(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return cpn.value.decode("utf-8")

    @property
    def firmware_version(self):
        """Gets the firmware version of the camera.

        Returns
        -------
        SeekCameraFirmwareVersion
            Firmware version of the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        fw, status = _clib.cseekcamera_get_firmware_version(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraFirmwareVersion(fw.product, fw.variant, fw.major, fw.minor)

    @property
    def thermography_window(self):
        """Gets/sets the thermography window of the camera.

        The thermography window is expressed in image coordinates. The global origin is
        the upper-left corner of the frame. Data outside the window is invalid.

        Returns
        -------
        (int, int, int, int)
            Tuple of integers specifying the thermography window origin, height, and
            width. The tuple is arranged as (x, y, w, h).

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        x, y, w, h, status = _clib.cseekcamera_get_thermography_window(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return x.value, y.value, w.value, h.value

    @thermography_window.setter
    def thermography_window(self, window):
        if not isinstance(window, tuple):
            raise SeekCameraInvalidParameterError

        (x, y, w, h) = window
        status = _clib.cseekcamera_set_thermography_window(self._camera, x, y, w, h)
        if is_error(status):
            raise error_from_status(status)

    def update_firmware(self, upgrade_file, callback=None, user_data=None):
        """Updates the camera firmware using a firmware file on the host OS.

        An optional callback can be used to provide progress updates.

        WARNING: Function should not be called when a capture session is live.

        NOTE: This function is not supported, and is not neccessary, for
        Micro Core SPI cores.

        Parameters
        ----------
        upgrade_file: str
            Path to the firmware update file. It may be absolute or relative to the
            executing directory. It must exist on the host filesystem.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containing user defined data.

        Raises
        ------
        SeekCameraErrorInvalidParameter
            1) If upgrade_file is not a str or None.
            2) If callback is specified but is not callable.
        SeekCameraError
            If an error ocurrs.
        """
        if upgrade_file is not None and not isinstance(upgrade_file, str):
            raise SeekCameraInvalidParameterError

        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_update_firmware(
            self._camera, upgrade_file, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

    def store_calibration_data(self, source_dir, callback=None, user_data=None):
        """Stores calibration data and pairs the camera.

        An optional callback can be used to provide progress updates.
        Pairing refers to the process by which the sensor is associated with the host
        and the embedded processor. The pairing process and requirements are highly
        dependent on the characteristics of the camera and system.

        WARNING: Function should not be called when a capture session is live. Pairing
        commands are only applicable to Micro Cores.

        Parameters
        ----------
        source_dir: str
            If a false type, the calibration data is read from sensor flash. If non
            false type, the calibration data is read from the filesystem.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containing user defined data.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If source_dir is not a str or None.
            2) If the callback is specified but is not callable.
        SeekCameraError
            If an error occurs.
        """
        if source_dir is not None and not isinstance(source_dir, str):
            raise SeekCameraInvalidParameterError

        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_store_calibration_data(
            self._camera, source_dir, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

    def store_flat_scene_correction(self, fsc_id, callback=None, user_data=None):
        """Stores a flat scene correction (FSC).

        The FSC is always stored to the host filesystem; it is also stored to the
        device if supported. An optional callback can be used to provide progress
        updates. FSC refers to the procedure used to correct non-uniformity in the
        thermal image introduced by the OEMs manufacturing process.

        NOTE: The camera must start imaging to compute and store a FSC. The camera must
        stop imaging to persistently save a FSC.

        Parameters
        ----------
        fsc_id: SeekCameraFlatSceneCorrectionID
            Enumerated unique ID of the flat scene correction to store.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containg user defined data.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the callback is specified but is not callable.
            2) If the ID is not a valid ID.
        SeekCameraError
            If an error occurs.
        """
        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        if not isinstance(fsc_id, SeekCameraFlatSceneCorrectionID):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_store_flat_scene_correction(
            self._camera, fsc_id, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

    def delete_flat_scene_correction(self, fsc_id, callback=None, user_data=None):
        """Deletes a flat scene correction (FSC).

        The FSC will be deleted from any location it was stored. An optional callback
        can be used to provide progress updates.

        NOTE: The camera must not be imaging to delete a FSC.

        Parameters
        ----------
        fsc_id: SeekCameraFlatSceneCorrectionID
            Unique enumerated ID of the FSC.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containing user defined data.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the callback is specified but is not callable.
            2) If the ID is not a valid ID.
        SeekCameraError
            If an error ocurrs.
        """
        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        if not isinstance(fsc_id, SeekCameraFlatSceneCorrectionID):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_delete_flat_scene_correction(
            self._camera, fsc_id, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

    def load_app_resources(self, region, data_size, callback=None, user_data=None):
        """Loads application resources into host memory.

        The source region may either be the camera internal memory or the SDK internal
        cache. Resources in each region must be <= 64KB. An optional callback can be
        used to provide progress updates.

        WARNING: Function should not be called when a capture session is live.

        Parameters
        ----------
        region: SeekCameraAppResourcesRegion
            Enum indicating which region should be used to load the data.
        data_size: int
            Total size of the data. It must be <= 64KB.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containing user defined data.

        Returns
        -------
        bytearray
            Object containing data read from the app resources region. It is <= 64KB.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the callback is specified but is not callable.
        SeekCameraError
            If an error occurs.
        """
        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        data, _, status = _clib.cseekcamera_load_app_resources(
            self._camera, region, data_size, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

        return bytearray(data)

    def store_app_resources(
        self, region, data, data_size, callback=None, user_data=None
    ):
        """Stores application resources to either the host or the device.

        The source region is host memory. The destination region may either be the
        camera internal memory or the SDK internal cache. Resources in each region must
        be <= 64KB. An optional callback can be used to provoide progress updates.

        WARNING: Function should not be called when a capture session is live.

        Parameters
        ----------
        region: SeekCameraAppResourcesRegion
            Enum indicating which region should be used to store the data.
        data: bytearray
            Host memory object. It contains the user defined data to store.
        data_size: int
            Total size of data. It must be <= 64KB.
        callback: callable
            Optional memory access callback that provides progress updates.
        user_data: any
            Optional parameter containing user defined data.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the input data is not a bytearray.
            2) If the callback is specified but is not callable.
        SeekCameraError
            If an error occurs.
        """
        if not isinstance(data, bytearray):
            raise SeekCameraInvalidParameterError

        if callback is not None and not callable(callback):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_store_app_resources(
            self._camera, region, data, data_size, callback, user_data
        )

        if is_error(status):
            raise error_from_status(status)

    def capture_session_start(self, frame_format):
        """Begins streaming frames of the specified formats from the camera.

        Generally a frame available callback should be pre-registered in order to
        receive frames, but doing so is not required.

        WARNING: Camera functions that interact with flash storage should not be called
        when a capture session is live.

        Unsafe functions:
            update_firmware
            store_calibration_data
            delete_flat_scene_correction
            load_app_resources
            store_app_resources

        Parameters
        ----------
        frame_format: int
            Bitwise OR combination of the frame formats to output. The frame format
            types are specified by SeekCameraFrameFormat.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        status = _clib.cseekcamera_capture_session_start(self._camera, frame_format)
        if is_error(status):
            raise error_from_status(status)

    def capture_session_stop(self):
        """Stops streaming frames from the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """

        status = _clib.cseekcamera_capture_session_stop(self._camera)
        if is_error(status):
            raise error_from_status(status)

    def register_frame_available_callback(self, callback, user_data=None):
        """Registers a user frame available callback function with the camera.

        The callback is fired every time a new frame is available. There can only be
        one registered frame available callback at a time.

        Parameters
        ----------
        callback: callable
            Callback function to register with the camera.
        user_data: Optional
            Optional parameter containing user defined data.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the callback is not callable.
        SeekCameraError
            If an error occurs.
        """
        if not callable(callback):
            raise SeekCameraInvalidParameterError

        self._user_data = user_data
        self._frame_available_callback = callback

        def _frame_available_callback(_camera, camera_frame, _user_data):
            self._frame_available_callback(
                self, SeekCameraFrame(camera_frame), self._user_data
            )

        self._frame_available_callback_ctypes = _frame_available_callback
        status = _clib.cseekcamera_register_frame_available_callback(
            self._camera, self._frame_available_callback_ctypes, self._user_data
        )

        if is_error(status):
            raise error_from_status(status)

    @property
    def color_palette(self):
        """Gets/sets the active color palette.

        Color palettes are used to colorize the image. Settings are refreshed between
        frames. This method can only be performed after a capture session has started.

        Returns
        -------
        SeekCameraColorPalette
            Active color palette used by the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        palette, status = _clib.cseekcamera_get_color_palette(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraColorPalette(palette.value)

    @color_palette.setter
    def color_palette(self, palette):
        if not isinstance(palette, SeekCameraColorPalette):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_color_palette(self._camera, palette)
        if is_error(status):
            raise error_from_status(status)

    @property
    def agc_mode(self):
        """Gets/sets the active AGC mode.

        Settings are refreshed between frames. This method can only be performed after
        a capture session has started.

        Returns
        -------
        SeekCameraAGCMode
            Active AGC mode used by the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        mode, status = _clib.cseekcamera_get_agc_mode(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraAGCMode(mode.value)

    @agc_mode.setter
    def agc_mode(self, mode):
        if not isinstance(mode, SeekCameraAGCMode):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_agc_mode(self._camera, mode)
        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_plateau(self):
        """Gets/sets the plateau value used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            Plateau value used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        plateau, status = _clib.cseekcamera_get_histeq_agc_plateau(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return plateau.value

    @histeq_agc_plateau.setter
    def histeq_agc_plateau(self, plateau):
        status = _clib.cseekcamera_set_histeq_agc_plateau(self._camera, plateau)
        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_plateau_redistribution_mode(self):
        """Gets/sets the plateau redistribution mode used for HistEQ AGC.

        The plateau value limits the percentage of pixels that can be in a single histogram bin.
        The plateau redistribution mode controls how many pixels in a histogram bin that exceed
        the plateau value are redistributed to other bins in the histogram.
        Settings are refreshed between frames.

        Returns
        -------
        SeekCameraHistEQAGCPlateauRedistributionMode
            Plateau redistrubtion mode used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        mode, status = _clib.cseekcamera_get_histeq_agc_plateau_redistribution_mode(
            self._camera
        )
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraHistEQAGCPlateauRedistributionMode(mode.value)

    @histeq_agc_plateau_redistribution_mode.setter
    def histeq_agc_plateau_redistribution_mode(self, mode):
        status = _clib.cseekcamera_set_histeq_agc_plateau_redistribution_mode(
            self._camera, mode
        )
        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_gain_limit(self):
        """Gets/sets the gain limit value used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            Gain limit value used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        limit, status = _clib.cseekcamera_get_histeq_agc_gain_limit(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return limit.value

    @histeq_agc_gain_limit.setter
    def histeq_agc_gain_limit(self, limit):
        status = _clib.cseekcamera_set_histeq_agc_gain_limit(self._camera, limit)
        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_gain_limit_factor_mode(self):
        """Gets/sets the state of the gain limit factor used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        SeekCameraHistEQAGCGainLimitFactorMode
            Mode used for controlling the gain limit factor for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        mode, status = _clib.cseekcamera_get_histeq_agc_gain_limit_factor_mode(
            self._camera
        )

        if is_error(status):
            raise error_from_status(status)

        return SeekCameraHistEQAGCGainLimitFactorMode(mode.value)

    @histeq_agc_gain_limit_factor_mode.setter
    def histeq_agc_gain_limit_factor_mode(self, mode):
        if not isinstance(mode, SeekCameraHistEQAGCGainLimitFactorMode):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_histeq_agc_gain_limit_factor_mode(
            self._camera, mode
        )

        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_gain_limit_factor_xmax(self):
        """Gets/sets the xmax value (for gain limit factor) used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        int
            xmax value (for gain limit factor) used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        xmax, status = _clib.cseekcamera_get_histeq_agc_gain_limit_factor_xmax(
            self._camera
        )

        if is_error(status):
            raise error_from_status(status)

        return xmax.value

    @histeq_agc_gain_limit_factor_xmax.setter
    def histeq_agc_gain_limit_factor_xmax(self, xmax):
        status = _clib.cseekcamera_set_histeq_agc_gain_limit_factor_xmax(
            self._camera, xmax
        )

        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_gain_limit_factor_ymin(self):
        """Gets/sets the ymin value (for gain limit factor) used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            ymin value (for gain limit factor) used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        ymin, status = _clib.cseekcamera_get_histeq_agc_gain_limit_factor_ymin(
            self._camera
        )

        if is_error(status):
            raise error_from_status(status)

        return ymin.value

    @histeq_agc_gain_limit_factor_ymin.setter
    def histeq_agc_gain_limit_factor_ymin(self, ymin):
        status = _clib.cseekcamera_set_histeq_agc_gain_limit_factor_ymin(
            self._camera, ymin
        )

        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_alpha_time(self):
        """Gets/sets the alpha time value HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            Alpha time value (in seconds) used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        alpha_time, status = _clib.cseekcamera_get_histeq_agc_alpha_time_seconds(
            self._camera
        )

        if is_error(status):
            raise error_from_status(status)

        return alpha_time.value

    @histeq_agc_alpha_time.setter
    def histeq_agc_alpha_time(self, alpha_time):
        status = _clib.cseekcamera_set_histeq_agc_alpha_time_seconds(
            self._camera, alpha_time
        )

        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_trim_left(self):
        """Gets/sets the histogram left trim percentage used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            Histogram left trim percentage used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        trim_left, status = _clib.cseekcamera_get_histeq_agc_trim_left(self._camera)

        if is_error(status):
            raise error_from_status(status)

        return trim_left.value

    @histeq_agc_trim_left.setter
    def histeq_agc_trim_left(self, trim_left):
        status = _clib.cseekcamera_set_histeq_agc_trim_left(self._camera, trim_left)

        if is_error(status):
            raise error_from_status(status)

    @property
    def histeq_agc_trim_right(self):
        """Gets/sets the histogram right trim percentage used for HistEQ AGC.

        Settings are refreshed between frames.

        Returns
        -------
        float
            Histogram right trim percentage used for HistEQ AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        trim_right, status = _clib.cseekcamera_get_histeq_agc_trim_right(self._camera)

        if is_error(status):
            raise error_from_status(status)

        return trim_right.value

    @histeq_agc_trim_right.setter
    def histeq_agc_trim_right(self, trim_left):
        status = _clib.cseekcamera_set_histeq_agc_trim_right(self._camera, trim_left)

        if is_error(status):
            raise error_from_status(status)

    @property
    def linear_agc_lock_mode(self):
        """Gets/sets the lock mode used for Linear AGC.

        Settings are refreshed between frames.

        Returns
        -------
        SeekCameraLinearAGCMode
            Lock mode used for Linear AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        mode, status = _clib.cseekcamera_get_linear_agc_lock_mode(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraLinearAGCLockMode(mode.value)

    @linear_agc_lock_mode.setter
    def linear_agc_lock_mode(self, mode):
        if not isinstance(mode, SeekCameraLinearAGCLockMode):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_linear_agc_lock_mode(self._camera, mode)
        if is_error(status):
            raise error_from_status(status)

    @property
    def linear_agc_lock_min(self):
        """Gets/sets the minimum lock value used for Linear AGC.

        Settings are refreshed between frames.

        Returns
        -------
        int:
            Minimum lock value used for Linear AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        lock_min, status = _clib.cseekcamera_get_linear_agc_lock_min(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return lock_min.value

    @linear_agc_lock_min.setter
    def linear_agc_lock_min(self, lock_min):
        status = _clib.cseekcamera_set_linear_agc_lock_min(self._camera, lock_min)
        if is_error(status):
            raise error_from_status(status)

    @property
    def linear_agc_lock_max(self):
        """Gets/sets the maximum lock value used for Linear AGC.

        Settings are refreshed between frames.

        Returns
        -------
        int:
            Minimum lock value used for Linear AGC.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        lock_max, status = _clib.cseekcamera_get_linear_agc_lock_max(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return lock_max.value

    @linear_agc_lock_max.setter
    def linear_agc_lock_max(self, lock_max):
        status = _clib.cseekcamera_set_linear_agc_lock_max(self._camera, lock_max)
        if is_error(status):
            raise error_from_status(status)

    @property
    def shutter_mode(self):
        """Gets/sets the active shutter mode.

        Settings are refreshed between frames.

        WARNING: Shutter commands are only applicable to Mosaic Cores.

        Returns
        -------
        SeekCameraShutterMode
            Active shutter mode used by the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        mode, status = _clib.cseekcamera_get_shutter_mode(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraShutterMode(mode.value)

    @shutter_mode.setter
    def shutter_mode(self, mode):
        if not isinstance(mode, SeekCameraShutterMode):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_shutter_mode(self._camera, mode)
        if is_error(status):
            raise error_from_status(status)

    @property
    def temperature_unit(self):
        """Gets/sets the active temperature unit.

        Settings are refreshed between frames.

        Returns
        -------
        SeekCameraTemperatureUnit
            Active temperature unit used by the camera.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        unit, status = _clib.cseekcamera_get_temperature_unit(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraTemperatureUnit(unit.value)

    @temperature_unit.setter
    def temperature_unit(self, unit):
        if not isinstance(unit, SeekCameraTemperatureUnit):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_temperature_unit(self._camera, unit)
        if is_error(status):
            raise error_from_status(status)

    def shutter_trigger(self):
        """Triggers the camera to shutter as soon as possible.

        WARNING: Shutter commands are only applicable to Mosaic Cores.

        Raises
        ------
        SeekCameraError:
            If an error occurs.
        """
        status = _clib.cseekcamera_shutter_trigger(self._camera)
        if is_error(status):
            raise error_from_status(status)

    @property
    def scene_emissivity(self):
        """Gets/sets the global scene emissivity.

        Emissivity is the measure of an object's ability to emit thermal radiation.
        It may take on values in the closed interval [0,1] with floating point
        precision.  Settings are refreshed between frames. This method can only be
        performed after a capture session has started.

        Returns
        -------
        float
            Active scene emissivity that was set by the user.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        emissivity, status = _clib.cseekcamera_get_scene_emissivity(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return emissivity.value

    @scene_emissivity.setter
    def scene_emissivity(self, emissivity):
        if not isinstance(emissivity, (float, int)):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_scene_emissivity(self._camera, emissivity)
        if is_error(status):
            raise error_from_status(status)

    @property
    def thermography_offset(self):
        """Gets/sets the thermography offset.

        The thermography offset is a constant that is applied to every pixel in the
        thermography frame.

        Returns
        -------
        int
            Active thermography offset applied to every pixel in the thermography frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        offset, status = _clib.cseekcamera_get_thermography_offset(self._camera)
        if is_error(status):
            raise error_from_status(status)

        return offset.value

    @thermography_offset.setter
    def thermography_offset(self, offset):
        if not isinstance(offset, (float, int)):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_thermography_offset(self._camera, offset)
        if is_error(status):
            raise error_from_status(status)

    def set_color_palette_data(self, palette, palette_data):
        """Sets the color palette data for a particular color palette.

        Parameters
        ----------
        palette: SeekCameraColorPalette
            Enumerated type corresponding to the color palette for which to set
            the data.
        palette_data: SeekCameraColorPalettteData
            Color values used to colorize the thermal image.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the palette is not of type SeekCameraColorPalette.
            2) If the plaette data is not of type SeekCameraColorPaletteData.
        SeekCameraError
            If an error occurs.
        """
        if not isinstance(palette, SeekCameraColorPalette):
            raise SeekCameraInvalidParameterError

        if not isinstance(palette_data, SeekCameraColorPaletteData):
            raise SeekCameraInvalidParameterError

        data = (_clib.CSeekCameraColorPaletteDataEntry * len(palette_data))()

        for index, value in enumerate(palette_data):
            (b, g, r, a) = value

            data[index] = (
                ctypes.c_uint8(b),
                ctypes.c_uint8(g),
                ctypes.c_uint8(r),
                ctypes.c_uint8(a),
            )

        status = _clib.cseekcamera_set_color_palette_data(self._camera, palette, data)

        if is_error(status):
            raise error_from_status(status)

    def set_filter_state(self, filter_type, filter_state):
        """Sets the state of an image processing filter.

        Settings are refreshed between frames.

        Parameters
        ----------
        filter_type: SeekCameraFilter
            Enumerated type indicating the filter for which to set the state.
        filter_state: SeekCameraFilterState
            Enumerated type indicating the state of the filter.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If the filter type is not of type SeekCameraFilter.
            2) If the filter state is not of type SeekCameraFilterState.
        SeekCameraError
            If an error occurs.
        """
        if not isinstance(filter_type, SeekCameraFilter):
            raise SeekCameraInvalidParameterError

        if not isinstance(filter_state, SeekCameraFilterState):
            raise SeekCameraInvalidParameterError

        status = _clib.cseekcamera_set_filter_state(
            self._camera, filter_type, filter_state
        )

        if is_error(status):
            raise error_from_status(status)

    def get_filter_state(self, filter_type):
        """Gets the state of an image processing filter.

        Settings are refreshed between frames. This method can only be performed after
        a capture session has started.

        Parameters
        ----------
        filter_type: SeekCameraFilter
            Enumerated type indicating the filter for which to get the state.

        Returns
        -------
        SeekCameraFilterState
            Enumerated type indicating if the state of the filter.

        Raises
        ------
        SeekCameraErrorInvalidParameter
            If the filter type is not of type SeekCameraFilter.
        SeekCameraError
            If an error occurs.
        """
        if not isinstance(filter_type, SeekCameraFilter):
            raise SeekCameraInvalidParameterError

        state, status = _clib.cseekcamera_get_filter_state(self._camera, filter_type)
        if is_error(status):
            raise error_from_status(status)

        return SeekCameraFilterState(state.value)


class SeekCameraFrameFormat(IntEnum):
    """Represents the types of output frame formats.

    Multiple frame formats can be captured simultaneously. However only one Display
    frame format and one Thermography frame format can exist in a capture session. The
    exception is that grayscale can be captured along with another color Display format.

    NOTE: All format types are little endian byte order.

    Attributes
    ----------
    CORRECTED: int
        Corrected frame format. It is the least processed format offered. To output
        corrected data, the SDK performs only required processing steps. These include:
        flat field subtraction (for shuttered cores), gain and offset correction, bad
        pixel replacement, and a few other proprietary processing techniques.
    PRE_AGC: int
        Pre-AGC frame format. It is the second least processed format offered. To output
        pre-AGC data, the SDK performs all processing steps required to output corrected
        data, as well as a limited number of proprietary processing filters.
    THERMOGRAPHY_FLOAT: int
        Thermography floating point format. The SDK performs all processing steps
        required to output corrected and pre-AGC data, as well as proprietary
        thermography processing. Temperature units are in degrees Celsius.
    THERMOGRAPHY_FIXED_10_6: int
        Thermography fixed point format. The SDK performs all processing steps required
        to output corrected and pre-AGC data, as well as proprietary thermography
        processing. Temperature units are in degrees Celsius.
    GRAYSCALE: int
        Grayscale frame format. The SDK performs all processing steps required to output
        corrected and pre-AGC data, as well as proprietary automatic gain correction
        (AGC) processing.
    COLOR_ARGB8888: int
        Color ARGB8888 format. The SDK performs all processing steps required to output
        corrected and pre-AGC data, as well as proprietary image processing (including
        automatic gain correction (AGC)).
    COLOR_RGB565: int
        Color RGB565 format. To output RGB565 data, the SDK performs conversion from
        ARGB8888.
    COLOR_AYUV: int
        Color AYUV format. To output AYUV data, the SDK performs conversion from
        ARGB8888.
    COLOR_YUY2: int
        Color YUY2 format. To output YUY2 data, the SDK performs conversion from
        ARGB8888.
    """

    CORRECTED = 0x04
    PRE_AGC = 0x08
    THERMOGRAPHY_FLOAT = 0x10
    THERMOGRAPHY_FIXED_10_6 = 0x20
    GRAYSCALE = 0x40
    COLOR_ARGB8888 = 0x80
    COLOR_RGB565 = 0x100
    COLOR_AYUV = 0x200
    COLOR_YUY2 = 0x400

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SeekCameraFrameFormat({})".format(self.value)


class SeekCameraFrame(object):
    """Encapsulates single or multiple generic SeekFrame instances.

    Properties
    ----------
    corrected: SeekFrame
        Gets the corrected frame.
    pre_agc: SeekFrame
        Gets the pre AGC frame.
    grayscale: SeekFrame
        Gets the grayscale frame.
    thermography_float: SeekFrame
        Gets the thermography floating point frame.
    thermography_fixed_10_6: SeekFrame
        Gets the thermography fixed point U10.6 frame.
    color_argb8888: SeekFrame
        Gets the color ARGB8888 frame.
    color_rgb565: SeekFrame
        Gets the color RGB565 frame.
    color_ayuv: SeekFrame
        Gets the color AYUV frame.
    color_yuy2: SeekFrame
        Gets the color YUY2 frame.
    """

    def __init__(self, camera_frame=None):
        """Creates a SeekCameraFrame.

        Parameters
        ----------
        camera_frame: Optional[CSeekCameraFrame]
            Optional reference to the camera frame object type used by the C bindings.

        Raises
        ------
        SeekCameraInvalidParameterError
            If camera_frame is specified and is not an instance of CSeekCameraFrame.
        """
        if camera_frame is None:
            camera_frame = _clib.CSeekCameraFrame(None)
        elif not isinstance(camera_frame, _clib.CSeekCameraFrame):
            raise SeekCameraInvalidParameterError

        self._camera_frame = camera_frame

    def __repr__(self):
        return "SeekCameraFrame({})".format(self._camera_frame)

    @property
    def corrected(self):
        """Gets the corrected frame.

        NOTE: The corrected format must have been specified in the capture session
        flags.

        Returns
        -------
        SeekFrame
            The corrected frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.CORRECTED)

    @property
    def pre_agc(self):
        """Gets the pre AGC frame.

        NOTE: The pre AGC format must have been specified in the capture session flags.

        Returns
        -------
        SeekFrame
            The pre AGC frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.PRE_AGC)

    @property
    def grayscale(self):
        """Gets the grayscale frame.

        NOTE: The post AGC format must have been specified in the capture session flags.

        Returns
        -------
        SeekFrame
            The post AGC frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.GRAYSCALE)

    @property
    def thermography_float(self):
        """Gets the thermography floating point frame.

        NOTE: The thermography float format must have been specified in the capture
        session flags.

        Returns
        -------
        SeekFrame
            The thermography floating point frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.THERMOGRAPHY_FLOAT)

    @property
    def thermography_fixed_10_6(self):
        """Gets the thermography U10.6 fixed point frame.

        NOTE: The thermography U10.6 fixed point format must have been specified in the
        capture session flags.

        Returns
        -------
        SeekFrame
            The thermography U10.6 fixed point frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.THERMOGRAPHY_FIXED_10_6)

    @property
    def color_argb8888(self):
        """Gets the color ARGB8888 frame.

        NOTE: The color ARGB8888 format must have been specified in the capture session
        flags.

        Returns
        -------
        SeekFrame
            The color ARGB8888 frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.COLOR_ARGB8888)

    @property
    def color_rgb565(self):
        """Gets the color RGB565 frame.

        NOTE: The color RGB565 format must have been specified in the capture session
        flags.

        Returns
        -------
        SeekFrame
            The color RGB565 frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.COLOR_RGB565)

    @property
    def color_ayuv(self):
        """Gets the AYUV frame.

        NOTE: The color AYUV format must have been specified in the capture session
        flags.

        Returns
        -------
        SeekFrame
            The color YUY2 frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.COLOR_AYUV)

    @property
    def color_yuy2(self):
        """Gets the color YUY2 frame.

        NOTE: The color YUY2 format must have been specified in the capture session
        flags.

        Returns
        -------
        SeekFrame
            The color YUY2 frame.

        Raises
        ------
        SeekCameraError
            If an error occurs.
        """
        return self._get_frame_by_format(SeekCameraFrameFormat.COLOR_YUY2)

    def _get_frame_by_format(self, fmt):
        if not isinstance(fmt, SeekCameraFrameFormat):
            raise SeekCameraInvalidParameterError

        frame, status = _clib.cseekcamera_frame_get_frame_by_format(
            self._camera_frame, fmt
        )

        if is_error(status):
            raise error_from_status(status)

        return SeekFrame(frame, fmt)

    def lock(self):
        """Locks a camera frame for exclusive access to the underlying frame data.

        Notes
        -----
        This allows the application to safely access the frame outside the context of the frame callback.
        1. There is no need to use this API (or the corresponding unlock) if all processing of the
           frame and frame data is done in the context of the frame callback.
        2. If the camera frame is already locked, calling this API multiple times has no effect.
        3. The user is responsible for unlocking a camera frame when exclusive access to the
           frame data is no longer needed.
        4. If the capture session is stopped while the camera frame is locked, exclusive access to
           the frame data is no longer guaranteed.
        """
        status = _clib.cseekcamera_frame_lock(self._camera_frame)

        if is_error(status):
            raise error_from_status(status)

    def unlock(self):
        """Unblocks a camera frame that was previously locked.

        Notes
        -----
        1. This API should only be used outside the context of the frame callback.
           There is no need for this API (or the corresponding lock API) if all
           processing of the frame (and frame data) is done in the context of the frame callback.
        2. If the camera frame is already unlocked, calling this API multiple times has no effect.
        """
        status = _clib.cseekcamera_frame_unlock(self._camera_frame)

        if is_error(status):
            raise error_from_status(status)


class SeekCameraFrameHeader(object):
    """Represents a common header for the camera frame.

    It is fixed size (2048 bytes) and byte aligned. It can be accessed in each
    individual SeekFrame.

    Properties
    ----------
    sentinel: int
        Gets the header sentinel.
    version: int
        Gets the version of the frame header.
    type: SeekCameraFrameFormat
        Gets the enumerated frame type.
    width: int
        Gets the number of pixels in the horizontal dimension.
    height: int
        Gets the number of pixels in the vertical dimension.
    channels: int
        Gets the number of image channels (e.g. 3 for RGB).
    pixel_depth: int
        Gets the number of bits per pixel.
    pixel_padding: int
        Gets the number of padding bits per pixel.
    line_stride: int
        Gets the number of bytes per line (i.e. row).
    line_padding: int
        Gets the number of padding bytes per line (i.e. row).
    header_size: int
        Gets the number of bytes in the header including line padding.
    timestamp_utc_ns: int
        Gets the UTC timestamp in nanosecond resolution.
    chipid: str
        Gets the CID of the camera.
    serial_number: str
        Gets the SN of the camera.
    core_part_number: str
        Gets the CPN of the camera.
    firmware_version: SeekCameraFirmwareVersion
        Gets the firmware version.
    io_type: SeekCameraIOType
        Gets the IO type of the camera.
    fpa_frame_count: int
        Gets the index of the frame as seen by the FPA.
    fpa_diode_count: int
        Gets the uncalibrated sampling of the FPA temperature diode voltage.
    environment_temperature: float
        Gets the estimated temperature based on the FPA in degrees Celsius.
    thermography_min: tuple[int, int, float]
        Gets the coordinates and value of the min thermography pixel.
    thermography_max: tuple[int, int, float]
        Gets the coordinates and value of the max thermography pixel.
    thermography_spot: tuple[int, int, float]
        Gets the coordinates and value of the spot thermography pixel.
    agc_mode: SeekCameraAGCMode
        AGC mode used to process the image.
    histeq_agc_num_bins: int
        Number of bins in the HistEQ AGC histogram.
    histeq_agc_bin_width: int
        Number of counts per bin in the HistEQ AGC histogram.
    histeq_agc_gain_limit_factor: float
        Multiplier of the HistEQ gain limit.
    linear_agc_min: int
        Minimum count value in the frame when using Linear AGC.
    linear_agc_max: int
        Maximum count value in the frame when using Linear AGC.
    gradient_correction_filter_state : SeekCameraFilterState
        State of the gradient correction filter.
    flat_scene_correction_filter_state : SeekCameraFilterState
        State of the flat scene correction filter.
    """

    def __init__(self, header=None):
        """Creates a new SeekCameraFrameHeader.

        Parameters
        ----------
        header: Optional[CSeekCameraFrameHeader]
            Optional reference to the camera frame header object type used by the C
            bindings.

        Raises
        ------
        SeekCameraInvalidParameterError
            If header is specified and is not an instance of CSeekCameraFrameHeader.
        """
        if header is None:
            header = _clib.CSeekCameraFrameHeader()
        elif not isinstance(header, _clib.CSeekCameraFrameHeader):
            raise SeekCameraInvalidParameterError

        self._header = header

    def __repr__(self):
        return "SeekCameraFrameHeader({})".format(self._header)

    @property
    def sentinel(self):
        """Gets the header sentinel.

        Returns
        -------
        int
            Header senintel.
        """
        return self._header.sentinel

    @property
    def version(self):
        """Gets the version of the frame header.

        Returns
        -------
        int
            Version of the frame header.
        """
        return self._header.version

    @property
    def frame_type(self):
        """Gets the enumerated frame type.

        Returns
        -------
        SeekCameraFrameFormat
            Enumerated frame type.
        """
        return SeekCameraFrameFormat(self._header.type)

    @property
    def width(self):
        """Gets the number of pixels in the horizontal dimension..

        Returns
        -------
        width: int
            Numer of pixels in the horizontal dimension.
        """
        return self._header.width

    @property
    def height(self):
        """Gets the number of pixels in the vertical dimension.

        Returns
        -------
        int
            Numer of pixels in the vertical dimension.
        """
        return self._header.height

    @property
    def channels(self):
        """Gets the number of image channels (e.g. 3 for RGB).

        Returns
        -------
        int
            Number of image channels.
        """
        return self._header.channels

    @property
    def pixel_depth(self):
        """Gets the number of bits per pixel.

        Returns
        -------
        int
            Number of bits per pixel.
        """
        return self._header.pixel_depth

    @property
    def pixel_padding(self):
        """Gets the number of padding bits per pixel.

        Returns
        -------
        int
            Number of padding bits per pixel.
        """
        return self._header.pixel_padding

    @property
    def line_stride(self):
        """Gets the number of bytes per line (i.e. row).

        Returns
        -------
        int
            Number of bytes per line (i.e. row).
        """
        return self._header.line_stride

    @property
    def line_padding(self):
        """Gets the number of padding bytes per line (i.e. row).

        Returns
        -------
        int
            Number of padding bytes per line (i.e. row).
        """
        return self._header.line_padding

    @property
    def header_size(self):
        """Gets the number of bytes in the header including line padding.

        Returns
        -------
        int
            Number of bytes in the header including line padding.
        """
        return self._header.header_size

    @property
    def timestamp_utc_ns(self):
        """Gets the UTC timestamp in nanosecond resolution.

        Returns
        -------
        int
            UTC timestamp in nanosecond resolution.
        """
        return self._header.timestamp_utc_ns

    @property
    def chipid(self):
        """Gets the CID of the camera.

        Returns
        -------
        str
            CID of the camera.
        """
        return self._header.chipid.decode("utf-8")

    @property
    def serial_number(self):
        """Gets the SN of the camera.

        Returns
        -------
        str
            SN of the camera.
        """
        return self._header.serial_number.decode("utf-8")

    @property
    def core_part_number(self):
        """Gets the CPN of the camera.

        Returns
        -------
        str
            CPN of the camera.
        """
        return self._header.core_part_number.decode("utf-8")

    @property
    def firmware_version(self):
        """Gets the firmware version of the camera.

        Returns
        -------
        SeekCameraFirmwareVersion
            Firmware version of the camera.
        """
        return SeekCameraFirmwareVersion(
            product=self._header.firmware_version[0],
            variant=self._header.firmware_version[1],
            major=self._header.firmware_version[2],
            minor=self._header.firmware_version[3],
        )

    @property
    def io_type(self):
        """Gets the IO type of the camera.

        Returns
        -------
        SeekCameraIOType
            IO type of the camera.

        """
        return SeekCameraIOType(self._header.io_type)

    @property
    def fpa_frame_count(self):
        """Gets the index of the frame as seen by the FPA.

        Returns
        -------
        int
            Index of the frame as seen by the FPA.
        """
        return self._header.fpa_frame_count

    @property
    def fpa_diode_count(self):
        """Gets the uncalibrated sampling of the FPA temperature diode voltage.

        Returns
        -------
        int
            Uncalibrated sampling of the FPA temperature diode voltage.
        """
        return self._header.fpa_diode_count

    @property
    def environment_temperature(self):
        """Gets the estimated temperature based on the FPA in degrees Celsius.

        Returns
        -------
        float
            Estimated temperature based on the FPA in degrees Celsius.
        """
        return self._header.environment_temperature

    @property
    def thermography_min(self):
        """Gets the coordinates and value of the min thermography pixel.

        Returns
        -------
        tuple[int, int, float]
            Coordinates and value of the min thermography pixel. It is in the format
            (x, y, value).
        """
        x = self._header.thermography_min_x
        y = self._header.thermography_min_y
        value = self._header.thermography_min_value
        return x, y, value

    @property
    def thermography_max(self):
        """Gets the coordinates and value of the max thermography pixel.

        Returns
        -------
        tuple[int, int, float]
            Coordinates and value of the max thermography pixel. It is in the format
            (x, y, value).
        """
        x = self._header.thermography_max_x
        y = self._header.thermography_max_y
        value = self._header.thermography_max_value
        return x, y, value

    @property
    def thermography_spot(self):
        """Gets the coordinates and value of the spot thermography pixel.

        Returns
        -------
        tuple[int, int, float]
            Coordinates and value of the spot thermography pixel. It is in the format
            (x, y, value).
        """
        x = self._header.thermography_spot_x
        y = self._header.thermography_spot_y
        value = self._header.thermography_spot_value
        return x, y, value

    @property
    def agc_mode(self):
        """Gets the AGC mode used to process the image.

        Returns
        -------
        SeekCameraAGCMode
            AGC mode used to process the image.
        """
        return SeekCameraAGCMode(self._header.agc_mode)

    @property
    def histeq_agc_num_bins(self):
        """Gets the number of bins in the HistEQ AGC histogram.

        Returns
        -------
        int
            Number of bins in the HistEQ AGC histogram.
        """
        return self._header.histeq_agc_num_bins

    @property
    def histeq_agc_bin_width(self):
        """Gets the number of counts per bin in the HistEQ AGC histogram.

        Returns
        -------
        int
            Number of counts per bin in the HistEQ AGC histogram.
        """
        return self._header.histeq_agc_bin_width

    @property
    def histeq_agc_gain_limit_factor(self):
        """Gets the multiplier of the HistEQ gain limit.

        Returns
        -------
        float
            Multiplier of the HistEQ gain limit.
        """
        return self._header.histeq_agc_gain_limit_factor

    @property
    def linear_agc_min(self):
        """Gets the minimum count value in the frame when using Linear AGC.

        Returns
        -------
        int
            Minimum count value in the frame when using Linear AGC.
        """
        return self._header.linear_agc_min

    @property
    def linear_agc_max(self):
        """Gets the maximum count value in the frame when using Linear AGC.

        Returns
        -------
        int
            Minimum count value in the frame when using Linear AGC.
        """
        return self._header.linear_agc_max

    @property
    def gradient_correction_filter_state(self):
        """Gets the state of the gradient correction filter.

        Returns
        -------
        SeekCameraFilterState
            State of the gradient correction filter.
        """
        return SeekCameraFilterState(self._header.gradient_correction_filter_state)

    @property
    def flat_scene_correction_filter_state(self):
        """Gets the state of the flat scene correction filter.

        Returns
        -------
        SeekCameraFilterState
            State of the flat scene correction filter.
        """
        return SeekCameraFilterState(self._header.flat_scene_correction_filter_state)


class SeekFrame:
    """Represents an arbitrary frame.

    Properties
    ----------
    width: int
        Gets the width of the frame in image coordinates.
    height: int
        Gets the height of the frame in image coordinates.
    channels: int
        Gets the number of image channels of the frame.
    pixel_depth: int
        Gets the pixel depth of the frame in bits.
    pixel_padding: int
        Gets the pixel padding of the frame in bits.
    line_stride: int
        Gets the line stride of the frame in bytes.
    line_padding: int
        Gets the line padding of the frame in bytes.
    data_size: int
        Gets the total size of the frame pixel data in bytes.
    data: numpy.array
        Gets the pixel data of the frame.
    is_empty: bool
        Checks if the frame does not contain any data.
    header_size: int
        Gets the total size of the frame header in bytes.
    header: SeekCameraFrameHeader
        Gets the frame header.
    """

    def __init__(self, frame=None, fmt=None):
        """Creates a new SeekFrame.

        Parameters
        ----------
        frame: Optional[CSeekFrame]
            Optional reference to the frame object type used by the C bindings.
        fmt: Optional[SeekCameraFrameFormat]
            Optional enumerated type indicating the frame type.

        Raises
        ------
        SeekCameraInvalidParameterError
            1) If frame is specified and is not an instance of SeekFrame.
            2) If fmt is specified and is not an instance of SeekCameraFrameFormat.
        """
        if frame is None:
            frame = _clib.CSeekFrame(None)
        elif not isinstance(frame, _clib.CSeekFrame):
            raise SeekCameraInvalidParameterError

        if fmt is not None and not isinstance(fmt, SeekCameraFrameFormat):
            raise SeekCameraInvalidParameterError

        self._frame = frame
        self.format = fmt

    def __repr__(self):
        return "SeekFrame({}, {})".format(self._frame, self.format)

    @property
    def width(self):
        """Gets the width of the frame in image coordinates.

        Returns
        -------
        int
            On success, the frame width.
            On failure, 0.
        """
        return _clib.cseekframe_get_width(self._frame)

    @property
    def height(self):
        """Gets the height of the frame in image coordinates.

        Returns
        -------
        int
            On success, the frame height.
            On failure, 0.
        """
        return _clib.cseekframe_get_height(self._frame)

    @property
    def channels(self):
        """Gets the number of image channels of the frame.

        Channels are stored contiguously.

        Returns
        -------
        int
            On success, the number of image channels.
            On failure, 0.
        """
        return _clib.cseekframe_get_channels(self._frame)

    @property
    def pixel_depth(self):
        """Gets the pixel depth of the frame in bits.

        Pixel depth refers to the non-padding bit depth of ech pixel.

        Returns
        -------
        int
            On success, the pixel depth.
            On failure, 0.
        """
        return _clib.cseekframe_get_pixel_depth(self._frame)

    @property
    def pixel_padding(self):
        """Gets the pixel padding of the frame in bits.

        Pixel padding refers to padding stored between pixels.

        Returns
        -------
        int
            On success, the pixel padding.
            On failure, 0.
        """
        return _clib.cseekframe_get_pixel_padding(self._frame)

    @property
    def line_stride(self):
        """Gets the line stride of the frame in bytes.

        Line stride refers to the total width of each image line/row. It includes line
        padding.

        Returns
        -------
        int
            On success, the line stride.
            On failure, 0.
        """
        return _clib.cseekframe_get_line_stride(self._frame)

    @property
    def line_padding(self):
        """Gets the line padding of the frame in bytes.

        Line padding refers to padding stored at the end of each line/row.

        Returns
        -------
        int
            On success, the line padding.
            On failure, 0.
        """
        return _clib.cseekframe_get_line_padding(self._frame)

    @property
    def data_size(self):
        """Gets the total size of the frame pixel data in bytes.

        Returns
        -------
        int
            On success, the data size as an unsigned integer type.
            On failure, 0.
        """
        return _clib.cseekframe_get_data_size(self._frame)

    @property
    def data(self):
        """Gets the pixel data of the frame.

        Returns
        -------
        numpy.array
            On success, the frame data as a numpy.array.
            On failure, None.
        """

        def as_nparray(dtype, shape):
            vptr = _clib.cseekframe_get_data(self._frame)
            data = ctypes.cast(vptr, ctypes.POINTER(dtype))
            return np.ctypeslib.as_array(data, shape=shape)

        if self.format is None:
            raise SeekCameraInvalidParameterError
        elif self.format == SeekCameraFrameFormat.CORRECTED:
            return as_nparray(ctypes.c_uint16, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.PRE_AGC:
            return as_nparray(ctypes.c_uint16, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.GRAYSCALE:
            return as_nparray(ctypes.c_uint8, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.THERMOGRAPHY_FLOAT:
            return as_nparray(ctypes.c_float, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.THERMOGRAPHY_FIXED_10_6:
            return as_nparray(ctypes.c_uint16, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.COLOR_ARGB8888:
            return as_nparray(ctypes.c_uint8, shape=(self.height, self.width, 4))
        elif self.format == SeekCameraFrameFormat.COLOR_RGB565:
            return as_nparray(ctypes.c_uint16, shape=(self.height, self.width))
        elif self.format == SeekCameraFrameFormat.COLOR_AYUV:
            return as_nparray(ctypes.c_uint8, shape=(self.height, self.width, 4))
        elif self.format == SeekCameraFrameFormat.COLOR_YUY2:
            return as_nparray(ctypes.c_uint8, shape=(self.height, self.width, 2))

        return None

    @property
    def is_empty(self):
        """Checks if the frame does not contain any data.

        Returns
        -------
        bool
            If the frame is empty, true.
            If the frame is not empty, false.
        """
        return _clib.cseekframe_is_empty(self._frame)

    @property
    def header_size(self):
        """Gets the total size of the frame header in bytes.

        Returns
        -------
        int
            On success, the header size as an unsigned integer type.
            On failure, 0.
        """
        return _clib.cseekframe_get_header_size(self._frame)

    @property
    def header(self):
        """Gets the frame header.

        Returns
        -------
        SeekCameraFrameHeader
            On success, the common frame header.
            On failure, None.
        """
        header = _clib.cseekframe_get_header(self._frame)
        if not header:
            return None

        return SeekCameraFrameHeader(header.contents)
