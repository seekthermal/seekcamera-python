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

import setuptools

long_description = ""
with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="seekcamera-python",
    version="1.2.0",
    author="Seek Thermal Incorporated",
    author_email="open-source@thermal.com",
    description="Seek Thermal SDK Python Language Bindings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seekthermal/seekcamera-python",
    license="Apache License 2.0",
    license_files=["LICENSE"],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.0",
    install_requires=[
        "numpy>=1",
    ],
    data_files=[
        ("examples", ["examples/seekcamera-opencv.py", "examples/seekcamera-simple.py"])
    ],
)
