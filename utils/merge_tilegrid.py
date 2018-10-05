import json
import argparse


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('--base_grid', required=True)
    parser.add_argument('--output_grid', required=True)
    parser.add_argument('--overlay_grid', required=True)
    parser.add_argument('--old_format', action='store_true')
    parser.add_argument('--mark_roi', action='store_true')

    args = parser.parse_args()

    with open(args.base_grid) as f:
        base_grid = json.load(f)

    if args.mark_roi:
        for tile in base_grid:
            base_grid[tile]['in_roi'] = True

    with open(args.overlay_grid) as f:
        overlay_grid = json.load(f)

        if args.old_format:
            overlay_grid = overlay_grid['tiles']

    for tile in overlay_grid:
        if tile in base_grid:
            for k in overlay_grid[tile]:
                if k in base_grid[tile]:
                    assert base_grid[tile][k] == overlay_grid[tile][k], (
                        k, base_grid[tile][k], overlay_grid[tile][k])
                else:
                    base_grid[tile][k] = overlay_grid[tile][k]
        else:
            base_grid[tile] = overlay_grid[tile]
            if args.mark_roi:
                base_grid[tile]['in_roi'] = False

    with open(args.output_grid, 'w') as f:
        json.dump(base_grid, f, indent=2)


if __name__ == '__main__':
    main()
