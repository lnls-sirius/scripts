#!/usr/bin/env python-sirius
"""."""


import argparse

from siriuspy.clientconfigdb import ConfigDBClient


def read_config_pair(name1, name2, config_type):
    """."""
    print("--- loading configurations ---")
    clt = ConfigDBClient(config_type=config_type)

    pvs1 = clt.get_config_value(name1)
    print(f"{name1:<50s}: {len(pvs1['pvs'])} pvs")
    pvs2 = clt.get_config_value(name2)
    print(f"{name2:<50s}: {len(pvs2['pvs'])} pvs")
    print()
    return pvs1, pvs2


def get_args():
    """Return command line arguments."""
    parser = argparse.ArgumentParser(
        description="""
            Compare two configs from ConfigDB server.

            Example:

            sirius-script-clientconfig-compare.py \
                ref_config_topup tmp --neg_pattern=".*-(CH|CV).*"

            Tip: If the regex string you pass to pos_pattern or neg_pattern
                starts with '-', use the following syntax:
                    --pos_pattern="-restofthestring"
            """
    )
    parser.add_argument(
        "name1", type=str, help="Name of the first config."
    )
    parser.add_argument(
        "name2", type=str, help="Name of the second config."
    )
    parser.add_argument(
        "--config_type",
        dest="config_type",
        type=str,
        required=False,
        default="global_config",
        help="Name of the configuration type.",
    )
    parser.add_argument(
        "--pos_pattern",
        dest="pos_pattern",
        type=str,
        required=False,
        default="",
        help="PVs that match this regex will be included in comparison.",
    )
    parser.add_argument(
        "--neg_pattern",
        dest="neg_pattern",
        type=str,
        required=False,
        default="",
        help="PVs that match this regex will be excluded in comparison."
        + " Empty string means no PV will be excluded.",
    )

    args = parser.parse_args()
    return args


def run():
    """."""
    args = get_args()

    config_type = args.config_type
    name1 = args.name1
    name2 = args.name2
    pos_pattern = args.pos_pattern
    neg_pattern = args.neg_pattern or None

    pvs1, pvs2 = read_config_pair(name1, name2, config_type)
    print("--- Differences between them ---\n")
    ConfigDBClient.compare_configs(pvs1, pvs2, pos_pattern, neg_pattern)


if __name__ == "__main__":
    run()
