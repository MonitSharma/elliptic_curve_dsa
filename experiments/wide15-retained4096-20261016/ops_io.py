"""Canonical immutable Op stream codec used only by this research adapter."""
import ctypes,ctypes.util,struct
z=ctypes.CDLL(ctypes.util.find_library('zstd'))
z.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t];z.ZSTD_decompress.restype=ctypes.c_size_t
z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int];z.ZSTD_compress.restype=ctypes.c_size_t
z.ZSTD_compressBound.argtypes=[ctypes.c_size_t];z.ZSTD_compressBound.restype=ctypes.c_size_t
z.ZSTD_isError.argtypes=[ctypes.c_size_t];z.ZSTD_isError.restype=ctypes.c_uint
def load(path):
    data=path.read_bytes();assert data[:8]==b'QECCOPSZ'
    n=struct.unpack_from('<Q',data,8)[0];assert 0<n<30_000_000
    buf=ctypes.create_string_buffer(n*56)
    size=z.ZSTD_decompress(buf,len(buf),data[16:],len(data)-16)
    assert not z.ZSTD_isError(size) and size==n*56
    return buf.raw
def save(path,raw):
    assert len(raw)%56==0
    buf=ctypes.create_string_buffer(z.ZSTD_compressBound(len(raw)))
    size=z.ZSTD_compress(buf,len(buf),raw,len(raw),3)
    assert not z.ZSTD_isError(size)
    path.write_bytes(b'QECCOPSZ'+struct.pack('<Q',len(raw)//56)+buf.raw[:size])
