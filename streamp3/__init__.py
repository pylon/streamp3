""" streaming MP3 decoder

This module defines the MP3Decoder class, which is used to convert an
MP3 stream to 16-bit PCM. The decoder reads/skips the ID3 container
in the stream and then each MP3 frame. For more information, see
http://mpgedit.org/mpgedit/mpeg_format/mpeghdr.htm.

"""

from io import BytesIO

from lame import hip

MP3_BUFFER_SIZE = 8192
PCM_BUFFER_SIZE = 65536


class MP3Decoder(object):
    """ streaming MP3 decoder class

    This class attaches a binary MP3 stream and decodes it into a sequence
    of 16-bit PCM frames (interleaved if stereo) encoded as bytes. The
    results may be consumed by repeatedly calling read() until it returns
    falsey, or by using the decoder as an iterator. For example,

    with open('my.mp3', 'rb') as mp3_file:
        decoder = MP3Decoder(mp3_file)
        for chunk in decoder:
            speaker.write(chunk)

    The decoder exposes the bit_rate, sample_rate, and num_channels
    properties as decoded from the first frame.

    Args:
        stream (stream): the IO stream to attach
        pcm_buffer_size (int): the size of the decoder pcm buffers to attach

    """

    def __init__(self, stream, pcm_buffer_size=PCM_BUFFER_SIZE):
        if isinstance(stream, bytes):
            stream = BytesIO(stream)

        self._stream = stream
        self._decoder = hip.Hip()
        self._bit_rate = 0
        self._sample_rate = 0
        self._num_channels = 0
        self._mp3_buffer = b''
        self._pcm_lbuffer = bytearray(pcm_buffer_size)
        self._pcm_rbuffer = bytearray(pcm_buffer_size)
        self._pcm_offset = 0
        self._pcm_length = 0

        self._read_id3()
        if not self._read_frame():
            raise Exception("invalid mp3 stream")

    @property
    def bit_rate(self):
        """ the compression rate (bits/sec) of the source audio """
        return self._bit_rate

    @property
    def sample_rate(self):
        """ the sample rate (Hz) of the output audio """
        return self._sample_rate

    @property
    def num_channels(self):
        """ the number of channels in the audio (1=mono, 2=stereo) """
        return self._num_channels

    def __iter__(self):
        """ return an iterator over the decoded stream """
        while True:
            chunk = self.read()
            if chunk:
                yield chunk
            else:
                break

    def read(self, max_bytes=None):
        """ read the next block from the decoded stream

        Args:
            max_bytes (int): the maximum number of bytes to return

        Returns:
            data (bytes): the decoded 16-bit pcm bytes if successful,
                or None if the end of the stream was reached

        """
        # decode the next mp3 frame, skipping any priming (empty) frames
        while self._pcm_length - self._pcm_offset == 0:
            if not self._read_frame():
                return None

        # default to decoding a whole frame at a time
        if not max_bytes:
            max_bytes = self._pcm_length - self._pcm_offset

        # ensure the result contains an even number of 16-bit samples
        size = min(self._pcm_length - self._pcm_offset, max_bytes)
        size -= size % 2

        if self._num_channels == 1:
            # mono was decoded into the left channel
            data = self._pcm_lbuffer[self._pcm_offset:size]
        else:
            # ensure the result contains the same number of left/right samples
            size -= size % 4

            # interleave the left/right samples
            data = bytearray([0] * size * 2)
            data[0::4] = self._pcm_lbuffer[self._pcm_offset + 0:size:2]
            data[1::4] = self._pcm_lbuffer[self._pcm_offset + 1:size:2]
            data[2::4] = self._pcm_rbuffer[self._pcm_offset + 0:size:2]
            data[3::4] = self._pcm_rbuffer[self._pcm_offset + 1:size:2]

        # advance the pcm buffer past the returned samples
        self._pcm_offset += size

        return bytes(data)

    def _read_id3(self):
        if not self._read_buffer():
            return False

        # decode the container id
        if self._mp3_buffer[:3] != 'ID3'.encode('ascii'):
            return False

        # decode the container flags
        flags = self._mp3_buffer[5]

        # decode the container size
        size = ((int(self._mp3_buffer[9]) << 0)
                | (int(self._mp3_buffer[8]) << 7)
                | (int(self._mp3_buffer[7]) << 14)
                | (int(self._mp3_buffer[6]) << 21))

        # add the header bytes
        size += 10

        # tack on another 10 if there is a footer
        if flags & 0x10:
            size += 10

        # load the container body
        while len(self._mp3_buffer) < size:
            if not self._read_buffer():
                return False

        # advance the buffer past the container
        self._mp3_buffer = self._mp3_buffer[size:]

        return True

    def _read_frame(self):
        # read the next MP3 frame header
        header = None
        while not header:
            if len(self._mp3_buffer) < 4 and not self._read_buffer():
                return False

            # the header starts with 11 1-bits
            # ignore corrupted frame headers and try the next byte
            header = self._mp3_buffer[:4]
            if header[0] != 0b11111111 or header[1] >> 5 != 0b111:
                header = None
                self._mp3_buffer = self._mp3_buffer[1:]

        # decode the mp3 header
        version_code = (header[1] & 0b00011000) >> 3
        layer_code = (header[1] & 0b00000110) >> 1
        bit_rate_code = (header[2] & 0b11110000) >> 4
        sample_rate_code = (header[2] & 0b00001100) >> 2
        padding_code = (header[2] & 0b00000010) >> 1
        channel_code = (header[3] & 0b11000000) >> 6

        # validate the MP3 layer
        if layer_code != 1:
            raise Exception("invalid mp3 layer: {0:08b}".format(layer_code))

        # extract header properties
        version = version_code & 1 if version_code >> 1 else 2
        bit_rate = hip.get_bit_rate(version, bit_rate_code) * 1000
        sample_rate = hip.get_sample_rate(version, sample_rate_code)
        is_padded = bool(padding_code)
        channels = 1 if channel_code == 0b11 else 2

        self._bit_rate = bit_rate
        self._sample_rate = sample_rate
        self._num_channels = channels

        # calculate the size of the whole frame
        frame_size = int(144 * bit_rate / sample_rate / (3 - channels))
        if is_padded:
            frame_size += 1

        # read the remainder of the frame
        while len(self._mp3_buffer) < frame_size:
            if not self._read_buffer():
                return False

        # decode the current frame into the pcm buffers
        self._pcm_offset = 0
        self._pcm_length = self._decoder.decode(self._mp3_buffer,
                                                frame_size,
                                                self._pcm_lbuffer,
                                                self._pcm_rbuffer)

        # advance the frame buffer past the current frame
        self._mp3_buffer = self._mp3_buffer[frame_size:]

        return True

    def _read_buffer(self):
        chunk = self._stream.read(MP3_BUFFER_SIZE)

        if not chunk:
            return False

        self._mp3_buffer += chunk
        return True
