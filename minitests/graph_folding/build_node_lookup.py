import argparse
import progressbar

from prjxray import util
from prjxray.db import Database
from node_lookup import NodeLookup
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    util.db_root_arg(parser)
    util.part_arg(parser)

    args = parser.parse_args()

    db = Database(args.db_root, args.part)

    if os.path.exists(args.database):
        os.unlink(args.database)

    lookup = NodeLookup(database=args.database)
    try:
        lookup.build_database(db, progressbar.progressbar)
    except Exception:
        os.unlink(args.database)


if __name__ == "__main__":
    main()
