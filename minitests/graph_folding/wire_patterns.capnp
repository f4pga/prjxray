@0xa4b49111bb3d0fc5;

struct WirePatterns {
    struct Pattern {
        dxdyIdxs  @0 : List(UInt16);
        tiles     @1 : List(UInt16);
        wires     @2 : List(UInt32);
        nodes     @3 : List(UInt32);
    }

    dxs             @0 : List(Int16);
    dys             @1 : List(Int16);
    wirePatterns    @2 : List(Pattern);
}
