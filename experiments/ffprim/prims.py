def ones(l):
    #return l + [x + '_1' for x in l]
    #return sorted(l + [x + '_1' for x in l])
    ret = []
    for x in l:
        ret.append(x)
        ret.append(x + '_1')
    return ret

ffprims_fall = ones([
        'FD',
        'FDC',
        'FDCE',
        'FDE',
        'FDP',
        'FDPE',
        'FDR',
        'FDRE',
        'FDS',
        'FDSE',
        ])
ffprims_f = [
        'FDRE',
        'FDSE',
        'FDCE',
        'FDPE',
        ]
ffprims_lall = ones([
        'LDC',
        'LDCE',
        'LDE',
        'LDPE',
        'LDP',
        ])
ffprims_l = [
        'LDCE',
        'LDPE',
        ]
ffprims = ffprims_f + ffprims_l

def isff(prim):
    return prim.startswith("FD")

def isl(prim):
    return prim.startswith("LD")

ff_bels_5 = [
        'A5FF',
        'B5FF',
        'C5FF',
        'D5FF',
        ]
ff_bels_ffl = [
        'AFF',
        'BFF',
        'CFF',
        'DFF',
        ]
ff_bels = ff_bels_ffl + ff_bels_5
#ff_bels = ff_bels_ffl

