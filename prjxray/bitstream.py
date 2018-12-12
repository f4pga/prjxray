# Break frames into WORD_SIZE bit words.
WORD_SIZE_BITS = 32

# How many 32-bit words for frame in a 7-series bitstream?
FRAME_WORD_COUNT = 101
'''
Sample:
bit_0002000f_079_06

Where:
-0002000f: FDRI address
-079: FDIR word number (0-100)
-06: bit index (0-31) 
'''


def load_bitdata(f):
    """ Read bit file and return bitdata map.
    Similar to segbits file

    bitdata is a map of of two sets.
    The map key is the frame address.
    The first sets are the word columns that have any bits set.
    Word columsn are WORD_SIZE_BITS wide.
    The second sets are bit index within the frame and word if it is set.
    """
    bitdata = dict()

    for line in f:
        line = line.split("_")
        frame = int(line[1], 16)
        wordidx = int(line[2], 10)
        bitidx = int(line[3], 10)

        if frame not in bitdata:
            bitdata[frame] = set(), set()

        bitdata[frame][0].add(wordidx)
        bitdata[frame][1].add(wordidx * WORD_SIZE_BITS + bitidx)

    return bitdata


# used by segprint
# TODO: merge these
def load_bitdata2(f):
    '''
    return as bitdata[frame][wordidx].add(bitidx)
    ie indexed by frame, word index, and then a set with bit indexes
    Similar to .bits file: bit_00020012_014_20
    '''

    bitdata = dict()

    for lineraw in f:
        lineraw = lineraw.strip()
        line = lineraw.split("_")
        try:
            frame = int(line[1], 16)
            wordidx = int(line[2], 10)
            bitidx = int(line[3], 10)
        except:
            print("Invalid line %s" % lineraw)
            raise

        if frame not in bitdata:
            bitdata[frame] = dict()

        if wordidx not in bitdata[frame]:
            bitdata[frame][wordidx] = set()

        bitdata[frame][wordidx].add(bitidx)
    return bitdata
