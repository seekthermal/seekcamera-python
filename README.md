# seekcamera-python

Welcome! :wave:

This is the official home of the Python language bindings for the Seek Thermal SDK. :snake:

## About :scroll:

In general, the Seek Thermal SDK allows customers to develop applications that interface with our thermal camera cores easily, flexibly, and efficiently.
In addition, examples are provided to demonstrate the use of several functional areas and can be a starting point for your own projects.

The Python language bindings supplement and extend the SDK's traditional C interface in a higher-level language.
They require the Seek Thermal SDK 4.X to be pre-installed on the system; they also require a Seek Thermal OEM core to be physically attached to the system.

Visit our [website](https://thermal.com) for more information and to get your [Starter Kit](https://www.thermal.com/oem.html).

## Features :test_tube:

The Python language bindings mirror all the major functionality in our SDK.

### Highlights :confetti_ball:

* Asynchronous event driven API that is fast and responsive
* Ability to use multiple cameras in one SDK instance
* First class support for Mosaic and Micro Core cameras through the same APIs
* Robust error handling and logging interface
* Numerous frame output formats
* Example applications to learn and get started

### Supported platforms :electric_plug:

The Python language bindinge will run on a wide variety of common processors and Linux/Windows OSs.

The requirements are
* Python 3.X
  * [numpy](https://numpy.org) >= 1
* A host architecture supported by the SDK (see the official SDK documentation for more information)

## Getting started :book:

We recommend that you jump right in by checking out one of the sample applications.
The sample applications demonstrate how to use the most common APIs and features in the SDK.

### Sample applications :bulb:

* seekcamera-opencv
  * Demonstrates how to image and display thermal frames to the screen using OpenCV's drawing functions.
* seekcamera-simple
  * Demonstrates how to export frame pixel values to disk as a CSV file.

### API documentation :brain:

API documentation is provided as standard Python docstrings.
Please refer to the more complete Seek Thermal SDK C Programming Guide which is provided with the SDK for more in-depth documentation.

## Installation :open_file_folder:

To install the Python language bindings using [pip](https://pypi.org/project/pip/).

```txt
pip3 install .
```

Or install as editable (recommended for developers)

```txt
pip3 install -e .
```

Or install with setuptools:

```txt
python3 setup.py install
```

### Dependencies :cd:

#### Python dependencies

Required Python dependencies can be installed via [pip](https://pypi.org/project/pip/).

```txt
$ cat requirements.txt
numpy>=1
```

```txt
pip3 install -r requirements.txt
```

Optional Python dependencies (required for some of the samples) can be installed via [pip](https://pypi.org/project/pip/).

```txt
pip3 install -r requirements.examples.txt
```

#### Other dependencies

The Python language bindings require the Seek Thermal SDK to be installed.
It is recommended, but not required, to use one of the SDK installers.
We provide Debian installers (`.deb`) for Linux and MSI installers (`.msi`) for Windows.

On Windows, the SDK library (`seekcamera.dll`) should be located in one of the following places in order of precedence:

```txt
%SEEKTHERMAL_LIB_DIR%/
C:/Program Files/Seek Thermal/SDK/4.X.X/x64-windows/lib
```

On Linux, the SDK library (`libseekcamera.so`) should be located in one of the following places in order of precedence:

```txt
$SEEKTHERMAL_LIB_DIR/
$LD_LIBRARY_PATH/
/lib/
/lib64/
/usr/lib/
/usr/lib64/
```

## License :balance_scale:

The project is licensed under the Apache 2.0 License (see `LICENSE`).

Copyright (c) 2021 Seek Thermal.

## Contributing :hammer:

We are excited about contributions!

Please see our contributing guide (`CONTRIBUTING.md`) for more information.