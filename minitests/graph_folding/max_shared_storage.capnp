@0xc33b8dbf33893c3c;

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



struct NodesAndWiresStorage {
    #nodePatterns was removed from litghost's representation
    # Id of node wire in tile pkey
    nodeWireInTilePkeys @0 : CompactArray; # This is the starting node pkey (indexes to these pkeys are found in subgraphs)

    # Storage of node -> wire patterns (The index of dx, dy, and patternToWire are aligned with the subgraph index)
    wirePatternDx       @1 : List(CompactArray); 
    wirePatternDy       @2 : List(CompactArray);
    wirePatternToWire   @3 : List(CompactArray);
    hasPip              @4 : List(CompactArray); # one list for each subgraph

    # Storage of subgraph to nodeWireInTilePkey
    subgraphs           @5 : List(CompactArray);

    # All of the below data structures are the same as in graph_storage.capnp
    # Tile patterns
    tilePatterns        @6 : List(CompactArray);

    tilePkeys           @7 : CompactArray;
    tileToTilePatterns  @8 : CompactArray;
}
