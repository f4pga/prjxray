#!/usr/bin/env python3

import argparse
import json


def check_sequential(speed_model):
    # combinational path models do not contain
    # the following keywords
    timing_keywords = {
        'setup': 'setup',
        'remov': 'removal',
        'hold': 'hold',
        'recov': 'recovery',
        'removal': 'removal',
        'recovery': 'recovery'
    }
    tmp = speed_model.split('_')
    for keyword in timing_keywords:
        if keyword in tmp:
            # return found keyword and it's map in SDF
            return [keyword, timing_keywords[keyword]]

    return None


# FF's can be configured to work as FF or latch
def check_ff_latch(speed_model):

    tmp = speed_model.split('_')
    if 'ff' in tmp:
        return 'ff'
    elif 'lat' in tmp:
        return 'lat'
    else:
        return None


# some bels have duplicate names e.g bufmrce_bufmrce
# this function cleans them
def clean_bname(bname):
    tmp = bname.split('_')
    if len(tmp) > 1 and tmp[0] == tmp[1]:
        return '_'.join(tmp[1:])
    return bname


def pin_in_model(pin, model, direction=None):

    # strip site location
    model = model.split(':')[0]
    extended_pin_name = pin

    # some timings reports pins with their directions
    # this happens for e.g. CLB reg_init D pin, which
    # timing is reported as DIN
    if direction is not None:
        extended_pin_name = pin + direction

    if len(pin.split('_')) == 1:
        # pin name is one word, search it in the model
        if pin in model.split('_'):
            return True, pin
        elif extended_pin_name in model.split('_'):
            return True, extended_pin_name
        else:
            return False, None
    else:
        # pin name is multi word, search for a string
        return (pin in model), pin


def remove_pin_from_model(pin, model):

    if len(pin.split('_')) == 1:
        # pin name is one word, search it in the model
        tmp = model.split('_')
        tmp.remove(pin)
        return "_".join(tmp)
    else:
        # pin name is multi word, search for a string
        return "_".join(list(filter(None, model.replace(pin, '').split('_'))))


def read_raw_timings(fin, properties, pins, site_pins):

    timings = dict()
    with open(fin, "r") as f:
        for line in f:

            raw_data = line.split()
            slice = raw_data[0]

            #XXX: debug
            if slice.startswith('DSP'):
                continue

            sites_count = int(raw_data[1])
            loc = 2
            for site in range(0, sites_count):

                site_name = raw_data[loc]
                bels_count = int(raw_data[loc + 1])
                print(slice, site_name)

                # read all BELs data within
                loc += 2
                for bel in range(0, bels_count):
                    tmp_data = raw_data[loc:]
                    btype = (tmp_data[0]).lower()
                    delay_count = int(tmp_data[1])

                    # get all the delays
                    delay_loc = 2
                    for delay in range(0, delay_count):
                        speed_model = tmp_data[delay_loc]
                        delay_btype = clean_bname(btype)
                        delay_btype_orig = delay_btype
                        # all the bel names seem to start with "bel_d_"
                        # let's get rid of it
                        if speed_model.startswith('bel_d_'):
                            speed_model = speed_model[6:]

                        # keep original speed model string to use as unique dict entry
                        speed_model_orig = speed_model

                        # if more than one BEL type exists in the slice
                        # location is added at the end of the name
                        tmp = speed_model.split(':')
                        speed_model = tmp[0]

                        bel_location = site_name
                        if len(tmp) > 2:
                            bel_location += "/" + "/".join(tmp[2:])

                        bel_location = bel_location.upper()

                        sequential = check_sequential(speed_model)
                        if sequential is not None:
                            tmp = speed_model.split('_')
                            tmp.remove(sequential[0])
                            speed_model = '_'.join(tmp)

                        bel_input = None
                        bel_output = None
                        bel_clock = None

                        # strip btype from speed model so we can search for pins
                        speed_model_clean = speed_model
                        if speed_model.startswith(delay_btype):
                            speed_model_clean = speed_model[len(delay_btype):]

                        # locate pins
                        for pin in pins[slice][site_name][delay_btype_orig]:
                            orig_pin = pin
                            pim, pin = pin_in_model(
                                pin.lower(), speed_model_clean, 'in')
                            if pim:
                                if pins[slice][site_name][delay_btype_orig][
                                        orig_pin]['is_clock']:
                                    bel_clock = pin
                                elif pins[slice][site_name][delay_btype_orig][
                                        orig_pin]['direction'] == 'IN':
                                    bel_input = pin
                                elif pins[slice][site_name][delay_btype_orig][
                                        orig_pin]['direction'] == 'OUT':
                                    bel_output = pin
                                speed_model_clean = remove_pin_from_model(
                                    pin.lower(), speed_model_clean)

                        if bel_clock is None:
                            for pin in site_pins[slice][site_name.lower()]:
                                orig_pin = pin
                                pim, pin = pin_in_model(
                                    pin.lower(), speed_model_clean)
                                if pim:
                                    if site_pins[slice][site_name.lower(
                                    )][orig_pin]['is_clock']:
                                        bel_clock = pin
                                        bel_clock_orig_pin = orig_pin
                                        speed_model_clean = remove_pin_from_model(
                                            pin.lower(), speed_model_clean)

                        # Some speed models describe delays from/to site pins instead of BEL pins
                        if bel_input is None:
                            # search site inputs
                            for pin in site_pins[slice][site_name.lower()]:
                                orig_pin = pin
                                pim, pin = pin_in_model(
                                    pin.lower(), speed_model_clean, 'in')
                                if pim:
                                    if site_pins[slice][site_name.lower(
                                    )][orig_pin]['direction'] == 'IN':
                                        bel_input = pin
                                        speed_model_clean = remove_pin_from_model(
                                            pin.lower(), speed_model_clean)

                        if bel_output is None:
                            for pin in site_pins[slice][site_name.lower()]:
                                orig_pin = pin
                                pim, pin = pin_in_model(
                                    pin.lower(), speed_model_clean)
                                if pim:
                                    if site_pins[slice][site_name.lower(
                                    )][orig_pin]['direction'] == 'OUT':
                                        bel_output = pin
                                        speed_model_clean = remove_pin_from_model(
                                            pin.lower(), speed_model_clean)

                        # check if the input is not a BEL property
                        if bel_input is None:
                            # if there is anything not yet decoded
                            if len(speed_model_clean.split("_")) > 1:
                                for prop in properties[slice][site_name][
                                        delay_btype_orig]:
                                    if prop.lower() in speed_model_clean:
                                        bel_input = prop
                                        speed_model_clean = remove_pin_from_model(
                                            prop.lower(), speed_model_clean)
                                        break
                        # if we couldn't find input, check if the clock is the
                        # only input
                        if bel_input is None and (bel_clock is not None):
                            if bel_clock_orig_pin in site_pins[slice][site_name.lower()] and \
                            site_pins[slice][site_name.lower(
                            )][bel_clock_orig_pin]['direction'] == 'IN':
                                bel_input = bel_clock

                        # if we still don't have the input check if the input
                        # is wider than 1 bit and timing defined for the whole
                        # port
                        import re
                        if bel_input is None:
                            for pin in pins[slice][site_name][
                                    delay_btype_orig]:
                                number = re.search(r'\d+$', pin)
                                if number is not None:
                                    orig_pin = pin[:-(
                                        len(str(number.group())))]
                                    pim, pin = pin_in_model(
                                        orig_pin.lower(), speed_model_clean)
                                    if not pim:
                                        # some inputs pins are named with unsignificant zeros
                                        # remove ti and try again
                                        orig_pin = orig_pin + str(
                                            int(number.group()))
                                        pim, pin = pin_in_model(
                                            orig_pin.lower(),
                                            speed_model_clean)

                                    if pim:
                                        bel_input = pin
                                        speed_model_clean = remove_pin_from_model(
                                            orig_pin.lower(),
                                            speed_model_clean)

                        # if we still don't have input, give up
                        if bel_input is None:
                            delay_loc += 6
                            continue

                        # restore speed model name
                        speed_model = delay_btype + speed_model_clean

                        if sequential is not None:
                            if bel_output is None and bel_clock is None:
                                delay_loc += 6
                                continue
                        else:
                            if bel_input is None or bel_output is None:
                                delay_loc += 6
                                continue

                        delay_btype = speed_model
                        extra_ports = None

                        if slice not in timings:
                            timings[slice] = dict()

                        if bel_location not in timings[slice]:
                            timings[slice][bel_location] = dict()

                        if delay_btype not in timings[slice][bel_location]:
                            timings[slice][bel_location][delay_btype] = dict()

                        timings[slice][bel_location][delay_btype][
                            speed_model_orig] = dict()
                        timings[slice][bel_location][delay_btype][
                            speed_model_orig]['type'] = btype.upper()
                        timings[slice][bel_location][delay_btype][
                            speed_model_orig]['input'] = bel_input.upper()

                        if bel_output is not None:
                            timings[slice][bel_location][delay_btype][
                                speed_model_orig]['output'] = bel_output.upper(
                                )
                        if bel_clock is not None:
                            timings[slice][bel_location][delay_btype][
                                speed_model_orig]['clock'] = bel_clock.upper()
                        timings[slice][bel_location][delay_btype][
                            speed_model_orig]['location'] = bel_location.upper(
                            )

                        #XXX: debug
                        timings[slice][bel_location][delay_btype][
                            speed_model_orig]['model'] = speed_model_orig
                        if sequential is not None:
                            timings[slice][bel_location][delay_btype][
                                speed_model_orig]['sequential'] = sequential[1]
                        if extra_ports is not None:
                            timings[slice][bel_location][delay_btype][
                                speed_model_orig]['extra_ports'] = extra_ports

                        # each timing entry reports 5 delays
                        for d in range(0, 5):
                            (t, v) = tmp_data[d + 1 + delay_loc].split(':')
                            timings[slice][bel_location][delay_btype][
                                speed_model_orig][t] = v

                        # 5 delay values + name
                        delay_loc += 6
                    loc += delay_loc
    return timings


def read_bel_properties(properties_file, properties_map):

    properties = dict()
    with open(properties_file, 'r') as f:
        for line in f:
            raw_props = line.split()
            tile = raw_props[0]
            sites_count = int(raw_props[1])
            prop_loc = 2
            properties[tile] = dict()
            for site in range(0, sites_count):
                site_name = raw_props[prop_loc]
                bels_count = int(raw_props[prop_loc + 1])
                prop_loc += 2
                properties[tile][site_name] = dict()
                for bel in range(0, bels_count):
                    bel_name = raw_props[prop_loc]
                    bel_name = clean_bname(bel_name)
                    bel_name = bel_name.lower()
                    bel_properties_count = int(raw_props[prop_loc + 1])
                    properties[tile][site_name][bel_name] = dict()
                    prop_loc += 2
                    for prop in range(0, bel_properties_count):
                        prop_name = raw_props[prop_loc]
                        # the name always starts with "CONFIG." and ends with ".VALUES"
                        # let's get rid of that
                        prop_name = prop_name[7:-7]
                        # append name prop name mappings
                        if bel_name in properties_map:
                            if prop_name in properties_map[bel_name]:
                                prop_name = properties_map[bel_name][prop_name]
                        prop_values_count = int(raw_props[prop_loc + 1])
                        properties[tile][site_name][bel_name][
                            prop_name] = raw_props[prop_loc + 2:prop_loc + 2 +
                                                   prop_values_count]
                        prop_loc += 2 + prop_values_count

    return properties


def read_bel_pins(pins_file):

    pins = dict()
    with open(pins_file, 'r') as f:
        for line in f:
            raw_pins = line.split()
            tile = raw_pins[0]
            sites_count = int(raw_pins[1])
            pin_loc = 2
            pins[tile] = dict()
            for site in range(0, sites_count):
                site_name = raw_pins[pin_loc]
                bels_count = int(raw_pins[pin_loc + 1])
                pin_loc += 2
                pins[tile][site_name] = dict()
                for bel in range(0, bels_count):
                    bel_name = raw_pins[pin_loc]
                    bel_name = clean_bname(bel_name)
                    bel_name = bel_name.lower()
                    bel_pins_count = int(raw_pins[pin_loc + 1])
                    pins[tile][site_name][bel_name] = dict()
                    pin_loc += 2
                    for pin in range(0, bel_pins_count):
                        pin_name = raw_pins[pin_loc]
                        pin_direction = raw_pins[pin_loc + 1]
                        pin_is_clock = raw_pins[pin_loc + 2]
                        pins[tile][site_name][bel_name][pin_name] = dict()
                        pins[tile][site_name][bel_name][pin_name][
                            'direction'] = pin_direction
                        pins[tile][site_name][bel_name][pin_name][
                            'is_clock'] = int(pin_is_clock) == 1
                        pin_loc += 3
    return pins


def read_site_pins(pins_file):

    pins = dict()
    with open(pins_file, 'r') as f:
        for line in f:
            raw_pins = line.split()
            tile = raw_pins[0]
            site_count = int(raw_pins[1])
            pin_loc = 2
            pins[tile] = dict()
            for site in range(0, site_count):
                site_name = raw_pins[pin_loc]
                site_name = site_name.lower()
                site_pins_count = int(raw_pins[pin_loc + 1])
                pins[tile][site_name] = dict()
                pin_loc += 2
                for pin in range(0, site_pins_count):
                    pin_name = raw_pins[pin_loc]
                    pin_direction = raw_pins[pin_loc + 1]
                    pins[tile][site_name][pin_name] = dict()
                    pins[tile][site_name][pin_name][
                        'direction'] = pin_direction
                    # site clock pins are always named 'CLK'
                    pins[tile][site_name][pin_name][
                        'is_clock'] = pin_name.lower() == 'clk'
                    pin_loc += 2
    return pins


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--timings', type=str, help='Raw timing input file')
    parser.add_argument('--json', type=str, help='json output file')
    parser.add_argument(
        '--properties', type=str, help='Bel properties input file')
    parser.add_argument('--belpins', type=str, help='Bel pins input file')
    parser.add_argument('--sitepins', type=str, help='Site pins input file')
    parser.add_argument(
        '--debug', type=bool, default=False, help='Enable debug json dumps')
    parser.add_argument(
        '--propertiesmap', type=str, help='Properties names mappings')
    args = parser.parse_args()

    with open(args.propertiesmap, 'r') as fp:
        properties_map = json.load(fp)

    properties = read_bel_properties(args.properties, properties_map)

    if args.debug:
        with open('debug_prop.json', 'w') as fp:
            json.dump(properties, fp, indent=4, sort_keys=True)

    pins = read_bel_pins(args.belpins)
    if args.debug:
        with open('debug_pins.json', 'w') as fp:
            json.dump(pins, fp, indent=4, sort_keys=True)

    site_pins = read_site_pins(args.sitepins)
    if args.debug:
        with open('debug_site_pins.json', 'w') as fp:
            json.dump(site_pins, fp, indent=4, sort_keys=True)

    timings = read_raw_timings(args.timings, properties, pins, site_pins)
    with open(args.json, 'w') as fp:
        json.dump(timings, fp, indent=4, sort_keys=True)


if __name__ == '__main__':
    main()
