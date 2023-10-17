#!/usr/bin/env python-sirius
"""."""


# Example:
#
# ./sirius-script-clientconfig-compare.py --name1 topupend1510
# --name2 ref_config_topup --pattern "TB.*"


import re
import argparse

from siriuspy.clientconfigdb import ConfigDBDocument


def read_config_pair(name1, name2, config_type):
    """."""
    print('--- loading configurations ---')
    config = ConfigDBDocument(config_type=config_type)

    config.name = name1
    config.load()
    pvs1 = config.value['pvs']
    pvs1 = {item[0]: item[1] for item in pvs1}
    print(f'{name1:<50s}: {len(pvs1)} pvs')

    config.name = name2
    config.load()
    pvs2 = config.value['pvs']
    pvs2 = {item[0]: item[1] for item in pvs2}
    print(f'{name2:<50s}: {len(pvs2)} pvs')

    print()

    return pvs1, pvs2


def build_diff_dicts(pvs1, pvs2):
    """."""
    pvs_both_diff = dict()
    pvs_only_first = dict()
    pvs_only_second = dict()

    for pvname, value in pvs1.items():
        if pvname in pvs2:
            if pvs2[pvname] != value:
                pvs_both_diff[pvname] = (value, pvs2[pvname])
        else:
            pvs_only_first[pvname] = value

    for pvname, value in pvs2.items():
        if pvname not in pvs1:
            pvs_only_second[pvname] = value

    return pvs_both_diff, pvs_only_first, pvs_only_second


def print_exclusive_set(name, pvs_set, pattern):
    """."""
    # pvs_set = pvs_only_first
    # name = name1
    regexp = re.compile(pattern)
    pvnames = [pvname for pvname in pvs_set if regexp.match(pvname)]

    print(f'--- PVs ony in {name} [{len(pvnames)}]: ---')
    for pvname in pvnames:
        value = pvs_set[pvname]
        if isinstance(value, (list, tuple)):
            print(f'{pvname:<50s}: {value[:3]} ...')
        else:
            print(f'{pvname:<50s}: {value}')
    print()


def print_difference(pvs_set, pattern):
    """."""
    regexp = re.compile(pattern)
    pvnames = [pvname for pvname in pvs_set if regexp.match(pvname)]

    print(f'--- PVs with differences [{len(pvnames)}]: ---')
    for pvname in pvnames:
        value1, value2 = pvs_set[pvname]
        if isinstance(value1, (list, tuple)):
            print(f'{pvname:<50s}: {value1[:3]} {value2[:3]} ...')
        else:
            print(f'{pvname:<50s}: {value1} {value2}')


def getArgs():
    """Return command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--config_type', dest='config_type', type=str, required=False,
        default='global_config', help="")
    parser.add_argument(
        '--name1', dest='name1', type=str, required=True, help="")
    parser.add_argument(
        '--name2', dest='name2', type=str, required=True, help="")
    parser.add_argument(
        '--pattern', dest='pattern', type=str, required=False,
        default='.*', help="")

    args = parser.parse_args()
    return args


def run():
    """."""
    args = getArgs()

    config_type = args.config_type
    name1 = args.name1
    name2 = args.name2
    pattern = args.pattern

    pvs1, pvs2 = read_config_pair(name1, name2, config_type)
    pvs_both_diff, pvs_only_first, pvs_only_second = \
        build_diff_dicts(pvs1, pvs2)
    print_exclusive_set(name1, pvs_only_first, pattern)
    print_exclusive_set(name2, pvs_only_second, pattern)
    print_difference(pvs_both_diff, pattern)


if __name__ == "__main__":
    run()
