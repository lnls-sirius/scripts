#!/usr/bin/env python-sirius
"""Script for running BBA measurements."""

import os
import sys
import time

import numpy as np

from mathphys.functions import load
from apsuite.commisslib.measure_bba import DoBBA
from siriuspy.clientconfigdb import ConfigDBClient


def bba_configure(
    dobba, ref_orb, bpms2dobba, deltaorbx, deltaorby,
    quad_deltakl, sofb_nrpoints, sofb_maxorberr
):
    """."""
    print("Configuring BBA measurement.")
    print(f"\tLoading si_orbit: {ref_orb}")
    cltorb = ConfigDBClient(config_type="si_orbit")
    orb = cltorb.get_config_value(ref_orb)

    dobba.params.deltaorbx = deltaorbx
    dobba.params.deltaorby = deltaorby
    dobba.params.quad_deltakl = quad_deltakl
    dobba.params.sofb_nrpoints = sofb_nrpoints
    dobba.params.sofb_maxorberr = sofb_maxorberr
    dobba.data["scancenterx"] = orb["x"]
    dobba.data["scancentery"] = orb["y"]

    if bpms2dobba:
        dobba.bpms2dobba = bpms2dobba

    print("\tWaiting PVs to connect...")
    if not dobba.wait_for_connection(timeout=15):
        print("\t\tSome PVs did not connect!")
    print("\tDone!")

    print("Measurement configured.")
    print(dobba)
    return dobba


def bba_run(dobba, fname):
    """."""
    print(80 * "#")
    print("Starting BBA measurement.")

    dobba.start()
    while not dobba.wait_measurement(2 * 60):
        dobba.save_data(fname, overwrite=True)
    dobba.save_data(fname, overwrite=True)


def process_bpms2dobba(bpms2dobba, dobba=None):
    """Process BPMs input.

    Accepts:
    - String: direct BPM name.
    - Regexp string: matches against dobba.params.BPMNAMES.
    - Path to .txt file: reads BPM names from file.
    - None: selects all BPMs.
    """
    if not isinstance(bpms2dobba, str):
        return bpms2dobba

    # if all BPMS
    if bpms2dobba.lower() == "all":
        return None

    # if comma-separated list
    if "," in bpms2dobba:
        return [bpm.strip() for bpm in bpms2dobba.split(",")]

    # if path+file
    if os.path.isfile(bpms2dobba):
        with open(bpms2dobba) as f:
            bpms2dobba = [line.strip() for line in f if line.strip()]
        return bpms2dobba

    # if regexp or single BPM name (exact regexp match)
    import re
    pattern = re.compile(bpms2dobba)
    bpms2dobba = [
        bpm for bpm in dobba.params.BPMNAMES
        if pattern.search(bpm)
    ]
    if bpms2dobba:
        return bpms2dobba
    else:
        print(f"No BPMs matched regexp pattern '{pattern.pattern}'.")

    print("bpms2dobba input could not be interpreted. Exiting")
    sys.exit(1)


def load_previous_progress(fname):
    """."""
    if not os.path.isfile(fname + ".pickle"):
        return None

    print("Previous BBA measurement w/ same filename found!")
    last_bba = load(fname)
    bpms2dobba = last_bba["data"]["bpms2dobba"]
    measured_bpms = list(last_bba["data"]["measure"].keys())
    # TODO: verify if previous measurements finished ok using
    # logic to verify if nrpoints match saved orbits dimensions
    if len(measured_bpms) == len(bpms2dobba):
        print(
              "\tPrevious BBA meas. already completed for given filename. \n" +
              "If you want to repeat the measurement, launch it again" +
              "with the '-i'/'--ignore-previous' arg. or different filename."
        )
        sys.exit(0)

    idx = bpms2dobba.index(measured_bpms[-1])
    bpms2dobba = bpms2dobba[idx:]
    return bpms2dobba


def main():
    """."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Measure BBA."
    )

    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        required=True,
        help="Filename for BBA measurement data.",
    )

    parser.add_argument(
        "-r",
        "--ref_orb",
        type=str,
        required=True,
        help="Name of reference orbit for BBA measurement ."
        "Use SOFB Window to correct orbit and save it in servconf."
        "Use the same orbit name.",
    )

    # TODO: argparse native list parsing
    # TODO: list + regexp + names inputs
    parser.add_argument(
        "-b",
        "--bpms2dobba",
        help=(
            "BPMs to include in the BBA measurement. Accepted input formats:\n"
            "  (1) Comma-separated list of BPM names, e.g.:\n"
            "      SI-17C3:DI-BPM-2,SI-17C4:DI-BPM\n"
            "  (2) Regular expression pattern to match BPM names, e.g.:\n"
            "      'M1' or 'M1|C1'\n"
            "  (3) Path to a .txt file listing BPM names (one per line)\n"
            "  (4) 'all' to include all BPMs (default behavior)\n\n"
            "Priority:\n"
            "- If this argument is given, it overrides previous progress.\n"
            "- If not provided:\n"
            "     • Previous progress (if found) resumes measurement.\n"
            "     • Otherwise, all BPMs are measured."
        )
    )

    parser.add_argument(
        "-p",
        "--print",
        action="store_true",
        help="Print measurement setup only, w/o launching the measurement. "
        "Default is False, set to True if flag is given.",
    )

    parser.add_argument(
        "-i",
        "--ignore-previous",
        action="store_true",
        help="Ignore data from previous BBA measurements with same filename"
        "in the working directory. Default: False, set to True if flag"
        "is given.",
    )

    parser.add_argument(
        "--deltaorbx",
        type=float,
        default=100,
        help="Range for horizontal orbit offset scan, in micrometers. "
        "Defaults to 100 um.",
    )

    parser.add_argument(
        "--deltaorby",
        type=float,
        default=100,
        help="Range for vertical orbit offset scan, in micrometers ."
        "Defaults to 100 um.",
    )

    parser.add_argument(
        "--quad_deltakl",
        type=float,
        default=0.02,
        help="Integrated duadrupole strength variation during measurements, "
        "in 1/m. Defaults to 0.02 1/m.",
    )

    parser.add_argument(
        "--sofb_nrpoints",
        type=int,
        default=20,
        help="Number of points for offset scan. Defaults to 20.",
    )

    parser.add_argument(
        "--sofb_maxorberr",
        type=int,
        default=5,
        help="Maximum number of failed attempts at placing a BPM at a given"
        "offset. Defaults to 5.",
    )

    args = parser.parse_args()

    fname = args.filename
    ref_orb = args.ref_orb

    previous_bpms2dobba = None
    if not args.ignore_previous:
        previous_bpms2dobba = load_previous_progress(fname)

    dobba = DoBBA()
    # If user provides BPMs explicitly, they override selection
    # from previous progress.
    if args.bpms2dobba:
        bpms2dobba = process_bpms2dobba(args.bpms2dobba, dobba)
    elif previous_bpms2dobba is not None:
        bpms2dobba = previous_bpms2dobba
        print(f"Starting BBA from BPM {bpms2dobba[0]}")
        fname += f"_started_from_{bpms2dobba[0].replace(':', '-')}"
    else:
        bpms2dobba = None

    dobba = bba_configure(
        dobba=dobba,
        ref_orb=ref_orb,
        bpms2dobba=bpms2dobba,
        deltaorbx=args.deltaorbx,
        deltaorby=args.deltaorby,
        quad_deltakl=args.quad_deltakl,
        sofb_nrpoints=args.sofb_nrpoints,
        sofb_maxorberr=args.sofb_maxorberr,
    )

    if not args.print:
        bba_run(dobba, fname)


if __name__ == "__main__":
    main()
