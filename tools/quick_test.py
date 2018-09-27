from __future__ import print_function
import prjxray.db
import argparse


def quick_test(db_root):
    db = prjxray.db.Database(db_root)
    g = db.grid()

    # Verify that we have some tile information for every tile in grid.
    tile_types_in_grid = set(
        g.gridinfo_at_loc(loc).tile_type for loc in g.tile_locations())
    tile_types_in_db = set(db.get_tile_types())
    assert len(tile_types_in_grid - tile_types_in_db) == 0

    # Verify that all tile types can be loaded.
    for tile_type in db.get_tile_types():
        tile = db.get_tile_type(tile_type)
        tile.get_wires()
        tile.get_sites()
        tile.get_pips()


def main():
    parser = argparse.ArgumentParser(
        description="Runs a sanity check on a prjxray database.")
    parser.add_argument('--db_root', required=True)

    args = parser.parse_args()

    quick_test(args.db_root)


if __name__ == '__main__':
    main()
