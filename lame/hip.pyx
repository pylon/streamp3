""" lame hip decoding wrapper for python """

cimport lame


cdef class Hip:
    """ hip decoder class

    This class maintains the data structures needed for decoding MP3
    frames and encapsulates the hip encoder api.

    """

    cdef lame.hip_t hip

    def __cinit__(self):
        self.hip = lame.hip_decode_init()
        if not self.hip:
            raise MemoryError()

    def __dealloc__(self):
        if self.hip:
            lame.hip_decode_exit(self.hip)

    def decode(self,
               mp3_buffer,
               mp3_length,
               pcm_lbuffer,
               pcm_rbuffer):
        """ decode an mp3 frame into left/right 16-bit pcm buffers

        Args:
            mp3_buffer (bytes): buffer containing a whole mp3 frame
            mp3_length (int): the number of bytes in the frame
            pcm_lbuffer (bytearray): return left channel pcm samples via here
            pcm_rbuffer (bytearray): return right channel pcm samples via here

        Returns:
            decoded (int): the number of pcm bytes decoded into each channel
                buffer

        """
        return self.do_decode(mp3_buffer,
                              mp3_length,
                              pcm_lbuffer,
                              pcm_rbuffer) * 2

    cdef int do_decode(self,
                       unsigned char* mp3_buffer,
                       size_t mp3_length,
                       unsigned char* pcm_lbuffer,
                       unsigned char* pcm_rbuffer):
        return lame.hip_decode1(self.hip,
                                mp3_buffer,
                                mp3_length,
                                <short*>pcm_lbuffer,
                                <short*>pcm_rbuffer)


def get_bit_rate(version, index):
    """ map an mp3 version/bitrate code to a kbps value

    Args:
        version (int): mp3g version (0=mpeg-2, 1=mpeg-1, 2=mpeg-2.5)
        index (int): bitrate code (0-15)

    Returns:
        bitrate (int): the kbps rate of the mp3 frame

    """
    return lame.lame_get_bitrate(version, index)


def get_sample_rate(version, index):
    """ map an mp3 version/bitrate code to a sample rate value

    Args:
        version (int): mp3g version (0=mpeg-2, 1=mpeg-1, 2=mpeg-2.5)
        index (int): bitrate code (0-15)

    Returns:
        sample_rate (int): audio sample rate (Hz)

    """
    return lame.lame_get_samplerate(version, index)
