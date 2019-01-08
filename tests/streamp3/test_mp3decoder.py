import pytest
from io import BytesIO

from streamp3 import MP3Decoder


def test_construction():
    # invalid stream
    with pytest.raises(Exception):
        MP3Decoder(BytesIO(b''))
    with pytest.raises(Exception):
        MP3Decoder(b'')
    with pytest.raises(Exception):
        MP3Decoder(b'invalid')
    with pytest.raises(Exception):
        MP3Decoder(open('tests/streamp3/data/id3only.mp3', 'rb'))
    with pytest.raises(Exception):
        MP3Decoder(bytes([0xFF, 0xFF, 0xFF, 0xFF]))

    # valid bytes
    MP3Decoder(open('tests/streamp3/data/noid3.mp3', 'rb').read())

    # valid stream, no ID3
    MP3Decoder(open('tests/streamp3/data/noid3.mp3', 'rb'))

    # valid stream with ID3
    MP3Decoder(open('tests/streamp3/data/withid3.mp3', 'rb'))


def test_properties():
    # constant bit rate
    decoder = MP3Decoder(open('tests/streamp3/data/cbr.mp3', 'rb'))
    assert decoder.bit_rate == 128000
    assert decoder.sample_rate == 44100
    assert decoder.num_channels == 2

    # variable bit rate
    decoder = MP3Decoder(open('tests/streamp3/data/vbr.mp3', 'rb'))
    assert decoder.bit_rate == 128000
    decoder.read()
    assert decoder.bit_rate == 32000
    assert decoder.sample_rate == 44100
    assert decoder.num_channels == 2

    # mono
    decoder = MP3Decoder(open('tests/streamp3/data/mono.mp3', 'rb'))
    assert decoder.bit_rate == 32000
    assert decoder.sample_rate == 16000
    assert decoder.num_channels == 1


def test_read():
    # stereo read
    decoder = MP3Decoder(open('tests/streamp3/data/stereo.mp3', 'rb'))
    while True:
        chunk = decoder.read()
        if chunk:
            assert isinstance(chunk, bytes)
            assert len(chunk) % 4 == 0
        else:
            break

    # mono read
    decoder = MP3Decoder(open('tests/streamp3/data/mono.mp3', 'rb'))
    while True:
        chunk = decoder.read()
        if chunk:
            assert isinstance(chunk, bytes)
            assert len(chunk) % 2 == 0
        else:
            break


def test_iterator():
    # valid file
    decoder = MP3Decoder(open('tests/streamp3/data/stereo.mp3', 'rb'))
    for chunk in decoder:
        assert isinstance(chunk, bytes)
        assert len(chunk) % 4 == 0

    # truncated file
    decoder = MP3Decoder(open('tests/streamp3/data/truncated.mp3', 'rb'))
    while True:
        chunk = decoder.read()
        if chunk:
            assert isinstance(chunk, bytes)
            assert len(chunk) % 4 == 0
        else:
            break


def test_iterator_with_copy():
    decoder = MP3Decoder(open('tests/streamp3/data/stereo.mp3', 'rb'), provide_copy=True)
    raw_data = b''
    for chunk, raw in decoder:
        raw_data += raw
        assert isinstance(chunk, bytes)
        assert len(chunk) % 4 == 0
    ref_data = open('tests/streamp3/data/stereo.mp3', 'rb').read()
    assert len(raw_data) == len(ref_data)
    assert raw_data == ref_data
