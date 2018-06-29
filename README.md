# streamp3

This library implements streaming MP3 decompression using the LAME library.

## Status
[![PyPI](https://badge.fury.io/py/streamp3.svg)](https://badge.fury.io/py/streamp3)
[![CircleCI](https://circleci.com/gh/pylon/streamp3.svg?style=shield)](https://circleci.com/gh/pylon/streamp3)
[![Coveralls](https://coveralls.io/repos/github/pylon/streamp3/badge.svg?branch=master)](https://coveralls.io/github/pylon/streamp3?branch=master)

## Installation

### Pip
```bash
pip install streamp3
```

## Usage
To begin decoding an MP3, construct an MP3Decoder, passing it in a binary
stream or `bytes` object. You can then access the `bit_rate`, `sample_rate`,
and `num_channels` properties for information about the MP3.

```python
from streamp3 import MP3Decoder

with open('my.mp3', 'rb') as mp3_file:
    decoder = MP3Decoder(mp3_file)
    print(decoder.bit_rate, decoder.sample_rate, decoder.num_channels)
```

You can then read samples from the stream directly using the `read()` method
or use the decoder as an iterator. Samples are returned as `bytes` objects,
which are 16-bit PCM encoded, with samples interleaved across channels. This
example streams an MP3 file to the system speaker using
[PyAudio](https://pypi.org/project/PyAudio/).

```python
import pyaudio
from streamp3 import MP3Decoder

with open('my.mp3', 'rb') as mp3_file:
    decoder = MP3Decoder(mp3_file)

    audio = pyaudio.PyAudio()
    device = audio.get_default_output_device_info()
    speaker = audio.open(output=True,
                         input_device_index=device['index'],
                         format=pyaudio.paInt16,
                         channels=decoder.num_channels,
                         rate=decoder.sample_rate)

    for chunk in decoder:
        speaker.write(chunk)
```

## Development

### Setup
We generally use pyenv to create virtual environments. The following script
creates a virtual environment for the project and installs dependencies.

```bash
pyenv install 3.6.4
pyenv virtualenv 3.6.4 streamp3
pip install -r requirements.txt
```

LAME must also be installed. This can be done on OSX via homebrew.

```bash
brew install lame
```

### Deployment
The project uses setup.py for installation and is deployed to
[PyPI](https://pypi.org). The project can be built for installation with
the following command:

```bash
python setup.py clean --all; rm -r ./dist
python setup.py sdist bdist_wheel
```

The wheel and source distribution can then be uploaded to PyPI using twine.

```bash
twine upload --repository-url=https://upload.pypi.org/legacy/ dist/*
```

## License

Copyright 2018 Pylon, Inc.

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
