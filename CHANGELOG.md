# CHANGELOG

## v1.2.0

Third stable release of the Python language bindings for the Seek Thermal SDK 4.X.

Highlights
* New APIs to wrap AGC APIs added to the C SDK (HistEQ, Linear)
* New APIs to wrap frame locking APIs added to the C SDK
* Bug fix for `cseekcamera_store_app_resources` which did not match the C API signature
* Bug fix for `cseekcamera_load_app_resources` which did not match the C API signature
* Bug fix for `SeekFrame.is_empty` API which accessed invalid `.value` attribute for bool type

## v1.1.1

Stable patch release for v1.1.X.

Released on 06/24/2021.

Highlights
* Bug fix for invalid argtypes assignment in seekcamera_set_temperature_unit CDLL stub.
* Bug fix for missing conversions of enumerated integers to higher-level SeekCamera objects.

## v1.1.0

Second stable release of the Python language bindings for the Seek Thermal SDK 4.X.

Released on 06/01/2021.

Highlights
* New feature for creating user-defined color palettes
* Bug fixes and improvements released in 4.1; see SDK release notes for more

## v1.0.0

First stable release of the Python language bindings for the Seek Thermal SDK 4.X.

Released on 05/20/2021.

Highlights
* Asynchronous event driven API that is fast and responsive
* Ability to use multiple cameras in one SDK instance
* Common set of APIs for both Mosaic and Micro Core cameras
* Robust error handling and logging interface
* Numerous frame output formats
* Example applications to learn and get started
