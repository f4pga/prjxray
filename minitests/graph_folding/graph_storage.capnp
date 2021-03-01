@0xa4b49111bb3d0fc5;

struct CompactArray {
    storage :union {
        u1  @0 : List(Bool);
        u8  @1 : List(UInt8);
        u16 @2 : List(UInt16);
        u32 @3 : List(UInt32);
        i8  @4 : List(Int8);
        i16 @5 : List(Int16);
        i32 @6 : List(Int32);
    }
}

struct WireToNodeStorage {
    wireInTilePkeys       @0 : CompactArray;

    # Storage of wire -> node patterns
    nodePatternDx         @1 : CompactArray;
    nodePatternDy         @2 : CompactArray;
    nodePatternToNodeWire @3 : CompactArray;

    # Storage of subgraph to wire
    subgraphs             @4 : List(CompactArray);

    # Tile patterns
    tilePatterns          @5 : List(CompactArray);

    tilePkeys             @6 : CompactArray;
    tileToTilePatterns    @7 : CompactArray;
}

struct NodeToWiresStorage {
    # Id of node wire in tile pkey
    nodeWireInTilePkeys @0 : CompactArray; # This is a list of all of the starting_wire_in_tile_pkeys (order matters)
                                           # Values are stored as a CompactArray 
    # Storage of node -> wire patterns
    wirePatternDx       @1 : CompactArray; # all of the dxs (index lines up with index of nodeWireInTilePkeys maybe)
    wirePatternDy       @2 : CompactArray; # all of the dys
    wirePatternToWire   @3 : CompactArray; # all of the wirePattern Ending Wire pkeys

    # up to this point, the data is represented in the smallest possible representation

    # Storage of node to wire pattern lists.
    nodePatterns        @4 : List(CompactArray);

    # Storage of subgraph to node
    subgraphs           @5 : List(CompactArray);

    # Tile patterns
    tilePatterns        @6 : List(CompactArray);

    tilePkeys           @7 : CompactArray;
    tileToTilePatterns  @8 : CompactArray;
}
