#!/usr/bin/env python-sirius
"""Run and analyze AC ORM measurements for LOCO."""

import argparse
import signal
import os
import sys
import time
from functools import partial
from threading import Lock

import numpy as np
from apsuite.commisslib.meas_ac_orm import ACORMParams, MeasACORM, ORMReport
from mathphys.functions import load

MEAS_TIMEOUT_DEFAULT = 6 * 60  # [s]
CONN_TIMEOUT_DEFAULT = 15  # [s]

lock_stop = Lock()


def _stop_now(meas_orm, signum, frame):
    """."""
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
    meas_orm.stop()
    print('Waiting measurement to stop smoothly')
    if meas_orm.wait_measurement(60):
        print('Measurement safely stopped.')
    else:
        print('Measurement did not stop within 60 seconds.')
    lock_stop.release()


def parse_args():
    """."""
    params = ACORMParams()

    parser = argparse.ArgumentParser(
        description='Measure AC ORM for LOCO fitting'
    )

    parser.add_argument(
        'orm_name',
        type=str,
        help='ORM nickname or keyword (without extension). Used for saving '
        'the measurement acquisitions data, the LOCO input data and saving '
        'the ORM to the configDB. '
    )

    parser.add_argument(
        '-f',
        '--folder',
        type=str,
        default=os.getcwd(),
        help='Path to the folder for output files (acquisition, LOCO input, '
        'figures of the analysis and the measurement report). '
        'Default is the current directory.',
    )

    parser.add_argument(
        '--print-setup',
        action='store_true',
        help='Print measurement setup (parameters) and try to connect to PVs. '
        'Default is False.',
    )

    parser.add_argument(
        '--run-meas',
        action='store_true',
        help='Run the measurement. If not set, the script will do a dry-run: '
        'will only connect to PVs and print the measurement setup (if '
        '--print-setup is set).',
    )

    parser.add_argument(
        '--conn-timeout',
        type=int,
        default=CONN_TIMEOUT_DEFAULT,
        help='Time (in seconds) to wait for PVs to connect. Defaults to '
        f'{CONN_TIMEOUT_DEFAULT} seconds.',
    )

    parser.add_argument(
        '--meas-timeout',
        type=int,
        default=MEAS_TIMEOUT_DEFAULT,
        help='Time (in seconds) to wait for measurement to finish. Defaults '
        f'to {MEAS_TIMEOUT_DEFAULT} seconds.',
    )

    parser.add_argument(
        '--save-acq-data',
        '--sa',
        action='store_true',
        help='''
        Save BPMs acquisition data (unprocessed data) to a pickle file
        named <orm_name>_acq_data.pickle. This can be useful for
        investigating issues w/ the measurement or for testing different data
        processing. These files can be quite large (~1-2 GB) and are not
        required for LOCO fitting. Defaults to False.''',
    )

    parser.add_argument(
        '--save2configdb',
        action='store_true',
        help='Save the measured AC ORM to the configDB server. '
        'Caution: this can overwrite existing ORMs with the same name! '
        'make sure to choose a unique ORM name.',
    )

    parser.add_argument(
        '--ref-respmat-name',
        type=str,
        default=params.ref_respmat_name,
        help='Name of the reference ORM to be used during the AC ORM '
        'measurement processing (determining scale factors and '
        'evaluate measurement quality). Make sure to input a valid '
        'name, existing in the machine database. Defaults to '
        f'"{params.ref_respmat_name}".',
    )

    parser.add_argument(
        '--correct_orbit_between_acqs',
        action='store_true',
        default=params.correct_orbit_between_acqs,
        help='Correct orbit between acquisitions. An ACORM measurement '
        'consists of several BPMs acquisitions for each set of corrector '
        'magnets excitations. If this flag is set, the orbit will be '
        'corrected to SOFBs current reference orbit in between acquisitions. '
        f'Defaults to {params.correct_orbit_between_acqs}.',
    )

    parser.add_argument(
        '-r',
        '--report',
        action='store_true',
        help='Create report. Default: False, set to True if flag is given.'
    )

    parser.add_argument(
        '-c',
        '--cleanup',
        action='store_true',
        help='Cleanup .png files. '
        'Default: False, set to True if flag is given.',
    )

    return parser.parse_args()


def configure_measurement(meas_orm, args):
    """."""
    # only configuring parameters which differ from
    # TODO: review the class defaults. compare it to the last measrements.
    # MeasACORM.params defaults or are changed by the flags of the script.

    p = meas_orm.params
    p.ref_respmat_name = args.ref_respmat_name
    p.correct_orbit_between_acqs = args.correct_orbit_between_acqs

    p.corrs_norm_kicks = True
    p.corrs_ch_kick = 5.0
    p.corrs_cv_kick = 5.0
    p.corrs_dorb1ch = 40.0
    p.corrs_dorb1cv = 40.0

    nrsecs = 1
    primes = p.find_primes(2 * 8 * nrsecs + 2, 3)
    primes = np.array(sorted(set(primes) - {59, 61}))
    cv_freqs = primes[: 8 * nrsecs]
    primes = np.array(sorted(set(primes) - set(cv_freqs)))
    ch_freqs = primes[: 6 * nrsecs]

    p.corrs_ch_freqs = ch_freqs
    p.corrs_cv_freqs = cv_freqs

    p.rf_mode = 'Standard'
    p.rf_step_kick = 75 / 2
    p.rf_step_delay = 0.2


def config_exists(meas_orm, name):
    """."""
    try:
        meas_orm.configdb.get_config_info(name)
    except Exception as e:
        print(f'ConfigDB error: {e}')
        return False
    return True


def loco_input_exists(name):
    """."""
    fname = f'{name}_loco_input_data.pickle'
    try:
        load(fname)
        print(
            f'A LOCO input data file named {fname} already exists. '
            + 'Please, choose a different ORM name or delete/rename the '
            'existing file.'
        )
        return True
    except FileNotFoundError:
        return False


def ensure_connection(meas_orm, timeout):
    """."""
    print('Connecting PVs...')
    if meas_orm.wait_for_connection(timeout):
        print('Connected.')
        return True

    print('Connection failed. Missing PVs:')
    for pv in meas_orm.disconnected_pvnames:
        print(f'\t{pv}')
    return False


def run_measurement(meas_orm, timeout):
    """."""
    meas_orm.start()

    if not meas_orm.wait_measurement(timeout):
        print('Measurement timeout.')
        return False

    return True


def cleanup_png_files(folder):
    """Cleans up generated PNG plot files."""
    lst = [
        'scale_factors',
        'correlation',
        'least_corr_ch',
        'least_corr_cv',
        'best_corr_ch',
        'best_corr_cv',
        'rf_column',
    ]
    for name in lst:
        try:
            os.remove(os.path.join(folder, name + '.png'))
        except FileNotFoundError:
            pass  # silently ignore missing files


def main():
    """."""
    args = parse_args()
    meas_orm = MeasACORM(isonline=True)

    if not config_exists(meas_orm, args.ref_respmat_name):
        print('Reference response matrix not found.')
        print(
            'Please, make sure the name passed to `--ref-respmat-name`'
            + ' is valid.'
        )
        sys.exit(1)

    if args.save2configdb and config_exists(meas_orm, args.orm_name):
        print(f'An ORM w/ name "{args.orm_name}" already exists in confgDB:')
        sys.exit(1)

    if loco_input_exists(args.orm_name):
        sys.exit(1)

    configure_measurement(meas_orm, args)

    signal.signal(signal.SIGINT, partial(_stop_now, meas_orm))
    signal.signal(signal.SIGTERM, partial(_stop_now, meas_orm))

    if not ensure_connection(meas_orm, args.conn_timeout):
        print('Exiting.')
        sys.exit(1)

    if args.print_setup:
        print(meas_orm.params)

    if not args.run_meas:
        print('Dry run. Use `--run-meas` to execute.')
        return

    print('#' * 80)
    print('Starting measurement...')

    if not run_measurement(meas_orm, args.meas_timeout):
        sys.exit(1)

    meas_orm.process_data()

    print('Measurement finished & processed.')
    print(f'\tFinished OK? {meas_orm.check_measurement_finished_ok()}')
    print(f'\tQuality? {meas_orm.check_measurement_quality()}')

    folder = args.folder.strip('/') + '/'

    if args.save_acq_data:
        print('Saving acquisitions data...')
        fname = f'{args.orm_name}_acq_data.pickle'
        meas_orm.save_data(folder + fname)
        print(f'Saved: {fname}')

    print('Saving LOCO input data...')
    loco_fname = f'{args.orm_name}_loco_input_data.pickle'
    meas_orm.save_loco_input_data(folder + loco_fname)
    print(f'Saved: {loco_fname}')
    print(
        'Use `sirius-script-si-loco-run-fitting.py` to fit model to this data.'
    )

    if args.save2configdb:
        print('Saving measured AC ORM to configDB...')
        meas_orm.save_respmat_to_configdb(args.orm_name)
        print('Saved.')

    if args.report:
        print('Creating report...')
        report = ORMReport()
        report.create_report(meas_orm=meas_orm, folder=folder)

    if args.cleanup:
        cleanup_png_files(folder)
        print('All .png files have been deleted.')


if __name__ == '__main__':
    main()
