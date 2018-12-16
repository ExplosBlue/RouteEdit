from libyaz0 import compress
from libyaz0 import decompress


def getCompressionMethod():
    return compressLIBYAZ0, decompressLIBYAZ0


def compressLIBYAZ0(inb, outf, level=1):
    """
    Compress the file using libyaz0
    """
    try:
        data = compress(inb, 0, level)

        with open(outf, "wb+") as out:
            out.write(data)

    except:
        return False

    else:
        return True


def decompressLIBYAZ0(inb):
    """
    Decompress the file using libyaz0
    """
    try:
        data = decompress(inb)

    except:
        return False

    else:
        return data
