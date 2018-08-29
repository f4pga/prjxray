import json

def load_speed(fin):
    speed_models = {}
    speed_types = {}
    for l in fin:
        delay = {}
        l = l.strip()
        for kvs in l.split():
            name, value = kvs.split(':')
            name = name.lower()
            if name in ('class',):
                continue
            if name in ('speed_index',):
                value = int(value)
            if name == 'type':
                speed_types.setdefault(value, {})
            delay[name] = value
        delayk = delay['name']
        if delayk in delay:
            raise Exception("Duplicate name")

        if "name" in delay and "name_logical" in delay:
            # Always true
            if delay['name'] != delay['name_logical']:
                raise Exception("nope!")
            # Found a counter example
            if 0 and delay['name'] != delay['forward']:
                # ('BSW_NONTLFW_TLRV', '_BSW_LONG_NONTLFORWARD')
                print(delay['name'], delay['forward'])
                raise Exception("nope!")
            # Found a counter example
            if 0 and delay['forward'] != delay['reverse']:
                # _BSW_LONG_NONTLFORWARD _BSW_LONG_TLREVERSE
                print(delay['forward'], delay['reverse'])
                raise Exception("nope!")

        speed_models[delayk] = delay
    return speed_models, speed_types

def load_cost_code(fin):
    # COST_CODE:4 COST_CODE_NAME:SLOWSINGLE
    cost_codes = {}
    for l in fin:
        lj = {}
        l = l.strip()
        for kvs in l.split():
            name, value = kvs.split(':')
            name = name.lower()
            lj[name] = value
        cost_code = {
            'name': lj['cost_code_name'],
            'code': int(lj['cost_code']),
            # Hmm is this unique per type?
            #'speed_class': int(lj['speed_class']),
            }
        
        cost_codes[cost_code['name']] = cost_code
    return cost_codes

def run(speed_fin, node_fin, fout, verbose=0):
    print('Loading data')
    speed_models, speed_types = load_speed(speed_fin)
    cost_codes = load_cost_code(node_fin)

    j = {
        'speed_model': speed_models,
        'speed_type': speed_types,
        'cost_code': cost_codes,
        }
    json.dump(j, fout, sort_keys=True, indent=4, separators=(',', ': '))

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description=
        'Timing fuzzer'
    )

    parser.add_argument('--verbose', type=int, help='')
    parser.add_argument(
        'speed_fn_in',
        default='/dev/stdin',
        nargs='?',
        help='Input file')
    parser.add_argument(
        'node_fn_in',
        default='/dev/stdin',
        nargs='?',
        help='Input file')
    parser.add_argument(
        'fn_out',
        default='/dev/stdout',
        nargs='?',
        help='Output file')
    args = parser.parse_args()
    run(open(args.speed_fn_in, 'r'), open(args.node_fn_in, 'r'), open(args.fn_out, 'w'), verbose=args.verbose)
