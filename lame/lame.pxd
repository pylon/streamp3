cdef extern from "<lame/lame.h>":
    # lame api
    int lame_get_bitrate(int mpeg_version, int table_index)
    int lame_get_samplerate(int mpeg_version, int table_index)

    # hip api
    ctypedef struct hip_global_flags:
        pass

    ctypedef hip_global_flags* hip_t

    hip_t hip_decode_init()

    int hip_decode_exit(hip_t hip)

    int hip_decode1(
        hip_t hip,
        unsigned char* mp3_buffer,
        size_t len,
        short* pcm_l,
        short* pcm_r) nogil
