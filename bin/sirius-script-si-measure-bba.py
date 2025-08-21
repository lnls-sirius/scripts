#!/usr/bin/env python-sirius
"""Script for running BBA measurements."""

import os
import re
import signal
import sys
import time

from mathphys.functions import load
from apsuite.commisslib.measure_bba import BBAParams, DoBBA
from siriuspy.clientconfigdb import ConfigDBClient

STOP_EVENT = False


def _stop_now(signum, frame):
    _ = frame
    sname = signal.Signals(signum).name
    tstamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"{sname} received at {tstamp}")
    sys.stdout.flush()
    sys.stderr.flush()
    global STOP_EVENT
    STOP_EVENT = True


def bba_run(dobba, fname):
    """Runs the BBA measurement and saves the data.

    Args:
        dobba (DoBBA): The configured DoBBA object.
        fname (str): Filename to save the measurement data.
    """
    print(80 * "#")
    print("Starting BBA measurement.")

    dobba.start()
    while not STOP_EVENT and not dobba.wait_measurement(2 * 60):
        dobba.save_data(fname, overwrite=True)

    if STOP_EVENT:
        print("User requested stop. Sending stop command to BBA meas.")
        dobba.stop()
        if dobba.wait_measurement():
            print("Measurement safely stopped.")

    dobba.save_data(fname, overwrite=True)


def get_bpms_for_bba(args, all_bpms, fname):
    """Determines the list of BPMs to be used for the BBA measurement.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.
        all_bpms (list): List of all available BPM names.
        fname (str): Filename for BBA measurement data.

    Returns:
        tuple: the list of BPMs for BBA and the updated filename.
        Exits the script if _process_bpms2dobba returns None.
    """
    bpms2dobba = None
    if not args.ignore_previous:
        bpms2dobba = _load_previous_progress(fname)

    if args.bpms2dobba:
        bpms2dobba = _process_bpms2dobba(args.bpms2dobba, all_bpms)
        if bpms2dobba is None:  # Handle error from _process_bpms2dobba
            sys.exit(1)
    elif bpms2dobba is not None:
        print(f"Starting BBA from BPM {bpms2dobba[0]}")
        fname, _ = os.path.splitext(fname)
        fname += f"_started_from_{bpms2dobba[0].replace(':', '-')}"
    else:
        bpms2dobba = all_bpms

    return bpms2dobba, fname


def print_bpms(all_bpms):
    """Prints BPM indices & names, quits execution.

    Args:
        all_bpms (list): List of all available BPM names.
    """
    print("BPM index      BPM name")
    for i, bpm in enumerate(all_bpms):
        print(f"  {i:03d}       {bpm}")


def get_scancenter_orb(ref_orb):
    """Get scan center ref. orb. for BBA."""
    print(f"\tLoading si_orbit: {ref_orb}")
    cltorb = ConfigDBClient(config_type="si_orbit")
    return cltorb.get_config_value(ref_orb)


def _load_previous_progress(fname):
    """Loads previous BBA measurement progress from a file.

    Exits the script if the previous measurement is already completed.

    Args:
        fname (str): Filename of the previous measurement data.

    Returns:
        list w/ remaining BPMs to be measured, or None if no previous progress
        is found.
    """
    try:
        last_bba = load(fname)
    except Exception as e:
        print(
            "No previous progress found or failed to load " +
            f"previous measurement file: {e}"
        )
        return None

    print("Previous BBA measurement w/ same filename found!")
    bpms2dobba = last_bba["data"]["bpms2dobba"]
    measured_bpms = list(last_bba["data"]["measure"].keys())

    # If previous measurement is already completed, exit
    if len(measured_bpms) == len(bpms2dobba):
        print(
              "\tPrevious BBA meas. already completed for given filename. \n" +
              "If you want to repeat the measurement, launch it again" +
              "with the '-i'/'--ignore-previous' arg. or different filename."
        )
        sys.exit(0)

    return [bpm for bpm in bpms2dobba if bpm not in measured_bpms]


def _process_bpms2dobba(bpms2dobba_args, all_bpms):
    """Processes the BPMs arguments for the BBA measurement.

    Exits the script if no BPMs match the provided arguments.

    Args:
        bpms2dobba_args (list):  Either a list of BPM names and/or regex
            patterns, or a path to file containing a BPM names per line.
        all_bpms (list): List of all available BPM names.

    Returns:
        A list of BPMs to be used in the measurement, or None if no arguments
        are provided.
    """
    if len(bpms2dobba_args) == 1:
        # only one item and it's a keyword or file
        arg = bpms2dobba_args[0]

        # all
        if arg.lower() == "all":
            return all_bpms

        # file
        if os.path.isfile(arg):
            with open(arg) as f:
                bpms = [line.strip() for line in f if line.strip()]
            bpms2dobba = [bpm for bpm in bpms if bpm in all_bpms]
            if len(bpms) != len(bpms2dobba):
                print(
                    f"Warning: {len(bpms2dobba)} BPMs identified" +
                    f" out of {len(bpms)} BPMs indicated in file."
                )
            return bpms2dobba

    bpms2dobba = []
    for arg in bpms2dobba_args:
        if arg in all_bpms:  # BPM name
            bpms2dobba.append(arg)
        else:  # regexp pattern
            try:
                pattern = re.compile(arg)
                matches = [
                    bpm for bpm in all_bpms if pattern.search(bpm)
                ]
                bpms2dobba.extend(matches)
            except re.error:
                pass

    # order-preserving removal of duplicates
    bpms2dobba = list(dict.fromkeys(bpms2dobba))

    if not bpms2dobba:
        print("Error: no BPMs matched the provided arguments.")
        return None

    return bpms2dobba


def main():
    """Parse arguments, configure, and run the BBA measurement."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Measure BBA."
    )

    parser.add_argument(
        "--print-all-bpms",
        action="store_true",
        help="Print all BPMS names/indices only, w/o establishing connections "
        "nor launching the measurement. Print and exit. ",
    )

    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        help="Filename for BBA measurement data. ",
    )

    parser.add_argument(
        "-o",
        "--ref-orb",
        type=str,
        default="ref_orb",
        help="Name of reference orbit for BBA measurement. "
        "If you want to carry out the measurement around the current machine "
        "orbit, use the SOFB Window to correct orbit and save it in servconf "
        "with a desired orbit name. Use the same orbit name here. ",
    )

    parser.add_argument(
        "-b",
        "--bpms2dobba",
        nargs="+",
        help="BPMs to include in the BBA measurement. Accepted inputs: "
        "(1) Space-separated list of BPMs names: SI-17C3:DI-BPM-2"
        " SI-17C4:DI-BPM. "
        "(2) Space-separated list of regexp patterns: 17 C3 M1|C1."
        "(3) Path to text file with one BPM name per line. "
        "(4) 'all' to include all BPMs. "
        "If provided, overrides automatic BPM selection from any previous"
        " measurement progress. ",
    )

    parser.add_argument(
        "-r",
        "--run-meas",
        action="store_true",
        help="Run the BBA measurement. If not set, the script only "
        "connects to devices/ref-orb and sets-up the measurement, w/o running "
        "it. Set this flag once you are conviced the measurement has been "
        "correclty set up. "
    )

    parser.add_argument(
        "-p",
        "--print-setup",
        action="store_true",
        help="Print measurement setup. Ideal for checking if meas. params. "
        "have been correclty set and PVs connections have been succesfully "
        "established, as well as if the desired BPMs have been correclty "
        "selected. ",
    )

    parser.add_argument(
        "-i",
        "--ignore-previous",
        action="store_true",
        help="Ignore data from previous BBA measurements with same filename "
        "in the working directory. ",
    )

    parser.add_argument(
        "-t",
        "--timeout",
        type=int,
        default=15,
        help="Connection timeout for quads and SOFB PVs, in seconds. "
        "Defaults to 15 s. "
    )

    parser.add_argument(
        "--deltaorbx",
        type=float,
        default=100,
        help="Range for horizontal orbit offset scan, in micrometers. "
        "Defaults to 100 um. ",
    )

    parser.add_argument(
        "--deltaorby",
        type=float,
        default=100,
        help="Range for vertical orbit offset scan, in micrometers. "
        "Defaults to 100 um. ",
    )

    parser.add_argument(
        "--quad_deltakl",
        type=float,
        default=0.02,
        help="Integrated duadrupole strength variation during measurements, "
        "in 1/m. Defaults to 0.02 1/m. ",
    )

    parser.add_argument(
        "--sofb_nrpoints",
        type=int,
        default=20,
        help="Number of points for offset scan. Defaults to 20. ",
    )

    parser.add_argument(
        "--sofb_maxorberr",
        type=float,
        default=5,
        help="Tolerated orbit error when placing a BPM at a given "
        "offset, in micrometers. Defaults to 5 um. ",
    )

    parser.add_argument(
        "--sofb_maxcorriter",
        type=int,
        default=5,
        help="Maximum number of failed attempts at placing a BPM at a given "
        "offset. Defaults to 5. ",
    )

    args = parser.parse_args()

    all_bpms = BBAParams.BPMNAMES

    if args.print_all_bpms:
        print_bpms(all_bpms)
        sys.exit(0)

    fname = args.filename
    orb = get_scancenter_orb(args.ref_orb)
    bpms2dobba, fname = get_bpms_for_bba(args, all_bpms, fname)

    dobba = DoBBA(isonline=True)
    print("Configuring BBA measurement.")

    dobba.params.deltaorbx = args.deltaorbx
    dobba.params.deltaorby = args.deltaorby
    dobba.params.quad_deltakl = args.quad_deltakl
    dobba.params.sofb_nrpoints = args.sofb_nrpoints
    dobba.params.sofb_maxcorriter = args.sofb_maxcorriter
    dobba.params.sofb_maxorberr = args.sofb_maxorberr

    dobba.data["scancenterx"] = orb["x"]
    dobba.data["scancentery"] = orb["y"]

    if bpms2dobba:
        dobba.bpms2dobba = bpms2dobba

    print("\tWaiting PVs to connect...")
    if not dobba.wait_for_connection(timeout=15):
        print("\t\tSome PVs did not connect! Disconnected PVs:")
        for pvname in dobba.disconnected_pvnames:
            print(f"\t\t{pvname}")
        print("\tExiting.")
        sys.exit(1)
    print("\tDone!")

    print("Measurement configured.")

    if args.print_setup:
        print(dobba)

    if args.run_meas:
        bba_run(dobba, fname)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, _stop_now)
    signal.signal(signal.SIGTERM, _stop_now)
    main()
