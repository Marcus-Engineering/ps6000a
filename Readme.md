# PicoScope 6000E Driver

This library provides a mid-level object-oriented Python wrapper for the PicoScope 6000A API,
which is used with the PicoScope 6000E series oscilloscopes. This library keeps track of the
necessary handles and buffers (and buffer allocation), but otherwise tries to present all of the
native functions of the API in an unchanged form.

Not all API functions have been fully Pythonized - only features that we've needed to use from
Python, which is basically streaming and block capture modes. Probably the biggest gap in the
Python API at this time is the AWG, which has not been worked on at all.

## Installation

First, the Pico SDK needs to be installed. It can be found at:
https://www.picotech.com/downloads/_lightbox/pico-software-development-kit-64bit

To install this Python library, you can use pip directly by running:

`pip install .` or `python setup.py install`.

This library is tested on CPython 3.10, on Windows 10.

It has also been tested on CPython 3.12 on Windows 10 but not fully. Other platforms *should*
work fine.

## Examples

Some API usage examples can be found in the `scripts` folder.

Other than that, the examples provided by Pico Technology for their C API should be pretty easy
to implement using this Python API.

## Compatibility Note

Note that where the driver code refers to "6000A", or "A API", this is because the API for the
PicoScope 6000E series is called the "A API" by the vendor. These drivers are not compatible with
the PicoScope 6000A series.

## License (MIT/ISC)

Copyright 2024 Marcus Engineering, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
associated documentation files (the “Software”), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Portions Copyright 2018-2019 Pico Technology Ltd. (ISC licensed):

"Permission to use, copy, modify, and/or distribute this software for any purpose with or without
fee is hereby granted, provided that the above copyright notice and this permission notice appear
in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS
SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITYAND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE."

Documentation Excerpts Copyright 2018-2019 Pico Technology Ltd.

## Changelog

- v0.1.2 (2024-11-05)
  - Initial public release.

