#!/usr/bin/env python-sirius
"""Script for running BBA measurements."""

import os
import re
import signal
import sys
import time
from functools import partial
from threading import Lock

from apsuite.commisslib.measure_bba import BBAParams, DoBBA
from siriuspy.clientconfigdb import ConfigDBClient

lock_stop = Lock()


def _stop_now(dobba, signum, frame):
    _ = frame
    if lock_stop.locked():
        print('There is another stop request running. Please wait a little.')
        return
    lock_stop.acquire()

    sname = signal.Signals(signum).name
    tstamp = time.strftime('%Y-%m-%d %H:%M:%S')
    print(f'{sname} received at {tstamp}')
    sys.stdout.flush()
    sys.stderr.flush()
    dobba.stop()
    print('Waiting measurement to stop smoothly')
    if dobba.wait_measurement(60):
        print('Measurement safely stopped.')
    else:
        print('Measurement did not stop within 60 seconds.')

    lock_stop.release()


def bba_run(dobba, fname):
    """Runs the BBA measurement and saves the data.

    Args:
        dobba (DoBBA): The configured DoBBA object.
        fname (str): Filename to save the measurement data.
    """
    print(80 * '#')
    print('Starting BBA measurement.')

    dobba.start()
    while not dobba.wait_measurement(2 * 60):
        dobba.save_data(fname, overwrite=True)
    dobba.save_data(fname, overwrite=True)


def print_bpms_quads(bpms_names, quads_names):
    """Prints BPM & Quads names and meas indices.

    Args:
        bpms_names (iterable): List/tuple of all BPM names.
        quads_names (iterable): List/tuple of all quads names.

    """
    stn = '     {:^20s} {:^20s}\n'.format('BPM', 'Quad')
    tmplt = '{:03d}: {:^20s} {:^20s}\n'
    for idx, (bpm, quad) in enumerate(zip(bpms_names, quads_names)):
        stn += tmplt.format(
            idx,
            bpm,
            quad,
        )
    print(stn)


def get_scancenter_orb(ref_orb):
    """Get scan center ref. orb. for BBA."""
    print(f'Loading si_orbit: {ref_orb}')
    cltorb = ConfigDBClient(config_type='si_orbit')
    return cltorb.get_config_value(ref_orb)


def load_previous_progress(dobba, fname):
    """Loads previous BBA measurement progress from a file.

    Exits the script if the previous measurement is already completed.

    Args:
        dobba (apsuite.measure_bba.DoBBA object): BBA measurement object
        fname (str): Filename of the previous measurement data.

    Exits the script if loading of previous measurement fails or if
    previous measurement is already complete.
    """
    try:
        dobba.load_and_apply(fname)
    except Exception as e:
        print(f'Failed to load previous measurement file: {e}')
        sys.exit(1)

    print('Previous BBA measurement found and loaded!')
    bpms2dobba = dobba.data['bpms2dobba']
    measured_bpms = list(dobba.data['measure'].keys())

    dobba.bpms2dobba = [bpm for bpm in bpms2dobba if bpm not in measured_bpms]
    # If previous measurement is already completed, exit
    if len(measured_bpms) == len(bpms2dobba):
        print(
            '\tPrevious BBA meas. already completed for given filename. \n'
            + 'If you want to repeat the measurement, launch it again'
            + "without the '--resume-meas' arg. or different filename."
        )
        sys.exit(0)


def process_bpms2dobba(bpms2dobba_args, all_bpms):
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
        if arg.lower() == 'all':
            return all_bpms

        # file
        if os.path.isfile(arg):
            with open(arg) as f:
                bpms = [line.strip() for line in f if line.strip()]
            bpms2dobba = [bpm for bpm in bpms if bpm in all_bpms]
            if len(bpms) != len(bpms2dobba):
                print(
                    f'Warning: {len(bpms2dobba)} BPMs identified'
                    + f' out of {len(bpms)} BPMs indicated in file.'
                )
            return bpms2dobba

    bpms2dobba = []
    for arg in bpms2dobba_args:
        if arg in all_bpms:  # BPM name
            bpms2dobba.append(arg)
        else:  # regexp pattern
            try:
                pattern = re.compile(arg)
                matches = [bpm for bpm in all_bpms if pattern.search(bpm)]
                bpms2dobba.extend(matches)
            except re.error:
                pass

    # order-preserving removal of duplicates
    bpms2dobba = list(dict.fromkeys(bpms2dobba))

    if not bpms2dobba:
        print('Error: no BPMs matched the provided arguments.')
        sys.exit(1)

    return bpms2dobba


def get_default_fname():
    """."""
    fname = 'bba_data_'
    fname += time.strftime('%Y-%m-%d-%H-%M')
    return fname


def main():
    """Parse arguments, configure, and run the BBA measurement."""
    import argparse as _argparse

    par = BBAParams()

    parser = _argparse.ArgumentParser(description='Measure BBA.')

    parser.add_argument(
        '--print-bpms-quads',
        action='store_true',
        help='Print all BPMs & quads names/indices only, '
        'w/o establishing connections nor launching the measurement. '
        'Print and exit. ',
    )

    parser.add_argument(
        '-f',
        '--filename',
        type=str,
        help='Filename for BBA measurement data. '
        "Default name of 'bba_data_yyy-dd-mm-hh-ss´ used if not given"
        'Mandatory if --resume-meas is given',
    )

    parser.add_argument(
        '--resume-meas',
        action='store_true',
        help='Resume from a previous measurement. If given, all other '
        'args are ignored and params from previous measurement are used.',
    )

    parser.add_argument(
        '-o',
        '--ref-orb',
        type=str,
        default='ref_orb',
        help='Name of reference orbit for BBA measurement. '
        'If you want to carry out the measurement around the current machine '
        'orbit, use the SOFB Window to correct orbit and save it in servconf '
        'with a desired orbit name. Use the same orbit name here. '
        'Not needed if resuming a previous measurement. ',
    )

    parser.add_argument(
        '-b',
        '--bpms2dobba',
        nargs='+',
        help='BPMs to include in the BBA measurement. Accepted inputs: '
        '(1) Space-separated list of BPMs names: SI-17C3:DI-BPM-2'
        ' SI-17C4:DI-BPM. '
        '(2) Space-separated list of regexp patterns: 17 C3 M1|C1.'
        '(3) Path to text file with one BPM name per line. '
        "(4) 'all' to include all BPMs. "
        "If not given, 'all' is assumed. "
        'Not needed if resuming from a previous measurement. ',
    )

    parser.add_argument(
        '-r',
        '--run-meas',
        action='store_true',
        help='Run the BBA measurement. If not given, the script only '
        'connects to devices/ref-orb and sets-up the measurement, w/o running '
        'it. Set this flag once you are convinced the measurement has been '
        'correctly set up and is ready to be launched. ',
    )

    parser.add_argument(
        '-p',
        '--print-setup',
        action='store_true',
        help='Print measurement setup. Ideal for checking if meas. params. '
        'have been correctly set and PVs connections have been successfully '
        'established, as well as if the desired BPMs have been correctly '
        'selected. ',
    )

    parser.add_argument(
        '-t',
        '--timeout',
        type=int,
        default=15,
        help='Connection timeout for quads and SOFB PVs, in seconds. '
        'Defaults to 15 s. ',
    )

    parser.add_argument(
        '--deltaorbx',
        type=float,
        default=par.deltaorbx,
        help='Range for horizontal orbit offset scan, in micrometers. '
        f'Defaults to {par.deltaorbx:.0f} um. '
        'Not needed if resuming a previous measurement. ',
    )

    parser.add_argument(
        '--deltaorby',
        type=float,
        default=par.deltaorby,
        help='Range for vertical orbit offset scan, in micrometers. '
        f'Defaults to {par.deltaorby:.0f} um. '
        'Not needed if resuming a previous measurement. ',
    )

    parser.add_argument(
        '--quad_deltakl',
        type=float,
        default=par.quad_deltakl,
        help='Integrated quadrupole strength variation during measurements, '
        f'in 1/m. Defaults to {par.quad_deltakl:.3f} 1/m. '
        'Not needed if resuming a previous measurement.',
    )

    parser.add_argument(
        '--sofb_nrpoints',
        type=int,
        default=par.sofb_nrpoints,
        help='Number of points for offset scan. '
        f'Defaults to {par.sofb_nrpoints:d}. '
        'Not needed if resuming a previous measurement.',
    )

    parser.add_argument(
        '--sofb_maxorberr',
        type=float,
        default=par.sofb_maxorberr,
        help='Tolerated orbit error when placing a BPM at a given '
        'offset, in micrometers. '
        f'Defaults to {par.sofb_maxorberr:.1f} um. '
        'Not needed if resuming a previous measurement. ',
    )

    parser.add_argument(
        '--sofb_maxcorriter',
        type=int,
        default=par.sofb_maxcorriter,
        help='Maximum number of failed attempts at placing a BPM at a given '
        f'offset. Defaults to {par.sofb_maxcorriter:d}. '
        'Not needed if resuming a previous measurement. ',
    )

    args = parser.parse_args()

    all_bpms = BBAParams.BPMNAMES
    all_quads = BBAParams.QUADNAMES

    if args.print_bpms_quads:
        print_bpms_quads(all_bpms, all_quads)
        sys.exit(0)

    fname = args.filename
    orb = get_scancenter_orb(args.ref_orb)

    if args.bpms2dobba:
        bpms2dobba = process_bpms2dobba(args.bpms2dobba, all_bpms)
    else:
        bpms2dobba = all_bpms

    dobba = DoBBA(isonline=True)
    print('Configuring BBA measurement.')

    signal.signal(signal.SIGINT, partial(_stop_now, dobba))
    signal.signal(signal.SIGTERM, partial(_stop_now, dobba))

    if args.resume_meas:
        if fname is None:
            print(
                'ERROR: '
                + "Can't resume from a previous meas! "
                + 'No filename was given. \n'
            )
            sys.exit(1)

        load_previous_progress(dobba, fname)
        print(
            'Warning! '
            + 'Measurement configured according to last '
            + 'measurement params. Ignoring any other args. passed.'
            + '\n'
        )
    else:
        dobba.params.deltaorbx = args.deltaorbx
        dobba.params.deltaorby = args.deltaorby
        dobba.params.quad_deltakl = args.quad_deltakl
        dobba.params.sofb_nrpoints = args.sofb_nrpoints
        dobba.params.sofb_maxcorriter = args.sofb_maxcorriter
        dobba.params.sofb_maxorberr = args.sofb_maxorberr
        dobba.data['scancenterx'] = orb['x']
        dobba.data['scancentery'] = orb['y']
        dobba.bpms2dobba = bpms2dobba

    if fname is None:
        fname = get_default_fname()

    print('Waiting PVs to connect...')
    if not dobba.wait_for_connection(timeout=args.timeout):
        print('\tSome PVs did not connect! Disconnected PVs:\n')
        for pvname in dobba.disconnected_pvnames:
            print(f'\t{pvname}')
        print('\tExiting.')
        sys.exit(1)
    print('\tDone!')

    print('Measurement configured.')

    if args.print_setup:
        print(dobba)

    if args.run_meas:
        bba_run(dobba, fname)


if __name__ == '__main__':
    main()
