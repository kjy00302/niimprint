import PIL.ImageOps as ImageOps
import struct
import niimbotpacket
import sys
import math

if sys.version_info.minor >= 10:
    def countbitsofbytes(data):
        return int.from_bytes(data, 'big').bit_count()
else:
    def countbitsofbytes(data):
        n = int.from_bytes(data, 'big')
        # https://stackoverflow.com/a/9830282
        n = (n & 0x55555555) + ((n & 0xAAAAAAAA) >> 1)
        n = (n & 0x33333333) + ((n & 0xCCCCCCCC) >> 2)
        n = (n & 0x0F0F0F0F) + ((n & 0xF0F0F0F0) >> 4)
        n = (n & 0x00FF00FF) + ((n & 0xFF00FF00) >> 8)
        n = (n & 0x0000FFFF) + ((n & 0xFFFF0000) >> 16)
        return n


def naive_encoder(img):
    img_data = ImageOps.invert(img.convert("L")).convert("1").tobytes()
    line_length = math.ceil(img.width / 8)
    count_length = line_length // 3

    for x in range(img.height):
        line_data = img_data[x*line_length:(x+1)*line_length]
        counts = (
            countbitsofbytes(line_data[i*count_length:(i+1)*count_length])
            for i in range(3))
        header = struct.pack('>H3BB', x, *counts, 1)
        pkt = niimbotpacket.NiimbotPacket(0x85, header+line_data)
        yield pkt
