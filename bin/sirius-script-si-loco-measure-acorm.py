#!/usr/bin/env python-sirius
"""Script for running & analyzing AC ORM measurements for LOCO fittings."""

import signal
import sys
import time
from functools import partial
from threading import Lock

import numpy as _np
from apsuite.commisslib.meas_ac_orm import ACORMParams, MeasACORM
from mathphys.functions import load

MEAS_TIMEOUT = 6 * 60  # [s]
CONN_TIMEOUT = 15  # [s]

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


def configure(meas_orm, args):
    """."""
    # only configuring parameters which differ from
    # MeasACORM.params defaults or are changed by the flags of the script.
    # TODO: review the class defaults. compare it to the last measrements.
    meas_orm.params.ref_respmat_name = args.ref_respmat_name
    meas_orm.params.correct_orbit_between_acqs = (
        args.correct_orbit_between_acqs
    )

    meas_orm.params.corrs_norm_kicks = True
    meas_orm.params.corrs_ch_kick = 5.000
    meas_orm.params.corrs_cv_kick = 5.000
    meas_orm.params.corrs_dorb1ch = 40.000
    meas_orm.params.corrs_dorb1cv = 40.000

    nrsecs = 1
    primes = meas_orm.params.find_primes(2 * 8 * nrsecs + 2, 3)
    # TODO: do we still need to exclude frequencies close to 60 Hz even
    # now without the PetraVII Cavity?
    primes = _np.array(sorted(set(primes) - {59, 61}))
    cv_freqs = primes[: 8 * nrsecs]
    primes = _np.array(sorted(set(primes) - set(cv_freqs)))
    ch_freqs = primes[: 6 * nrsecs]

    meas_orm.params.corrs_ch_freqs = ch_freqs
    meas_orm.params.corrs_cv_freqs = cv_freqs

    meas_orm.params.rf_mode = 'Standard'
    meas_orm.params.rf_step_kick = 75 / 2
    meas_orm.params.rf_step_delay = 0.2


def check_configdb_entry(name, meas_orm, print_info=False):
    """True if name is not a si_orbcorr_respm entry, False otherwise."""
    try:
        info = meas_orm.configdb.get_config_info(name)
    except Exception as e:
        return True
    if print_info:
        print(f'An ORM with name "{name}" already exists in configDB ')
        print('Info:')
        for key, val in info.items():
            val = convert_timestamps(val)
            print(f'\t{key}: {val}')
    return False


def convert_timestamps(val):
    """."""
    if isinstance(val, float):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(val))

    elif isinstance(val, list):
        return [convert_timestamps(v) for v in val]
    return val


def check_previous_loco_input_data(name):
    """."""
    try:
        ln = name + '_loco_input_data.pickle'
        _ = load(ln)
        print(
            f'There already is a LOCO input data file named {ln}. '
            ' Please, choose a different ORM name or delete/rename the '
            'existing file. Exiting.'
        )
        return True
    except FileNotFoundError:
        return False


def main():
    """Parse params, configure and run the AC ORM measurement."""
    import argparse as _argparse

    params = ACORMParams()

    parser = _argparse.ArgumentParser(
        description='Measure AC ORM for LOCO fitting.'
    )

    parser.add_argument(
        '-n',
        '--name',
        type=str,
        default='acorm',
        help='ORM nickname (without extension). Used for saving measurement '
        'acquisitions data, LOCO input data and for saving the ORM to the '
        'configDB (if --save2configdb is set). Defaults to "acorm".',
    )

    parser.add_argument(
        '--print-setup',
        action='store_true',
        help='Print measurement setup (parameters) and try to connect to PVs.',
    )

    parser.add_argument(
        '--run-meas',
        action='store_true',
        help='Run the measurement. If not set, the script will only attempt '
        'to connect to PVs and print the measurement setup if '
        '--print-setup is set.',
    )

    parser.add_argument(
        '--conn-timeout',
        type=int,
        default=CONN_TIMEOUT,
        help='Time (in seconds) to wait for PVs to connect. Defaults to '
        f'{CONN_TIMEOUT} seconds.',
    )

    parser.add_argument(
        '--meas-timeout',
        type=int,
        default=MEAS_TIMEOUT,
        help='Time (in seconds) to wait for measurement to finish. Defaults '
        f'to {MEAS_TIMEOUT} seconds.',
    )

    parser.add_argument(
        '--save-acq-data',
        '--sa',
        action='store_true',
        default=False,
        help='Save BPMs acquisition data (unprocessed data) to a pickle file '
        'named <name>_acq_data.pickle. This can be useful for investigating '
        'issues w/ the measurement or for testing different data processing. '
        'These files can be quite large (~1-2 GB) and are not required for '
        'LOCO fitting. Defaults to False.',
    )

    parser.add_argument(
        '--save2configdb',
        action='store_true',
        default=False,
        help='Save the measured AC ORM to the configDB server. '
        'Caution: this can overwrite existing ORMs with the same name! '
        'make sure to choose a unique ORM name.',
    )

    parser.add_argument(
        '--ref-respmat-name',
        type=str,
        default=params.ref_respmat_name,
        help='Name of the reference ORM to be used during the AC ORM '
        'measurement processing (determining scale factors and compare '
        'evaluate measurement quality). Make sure to input a valid '
        'name, existing in the machine database. Defaults to '
        f'"{params.ref_respmat_name}".',
    )

    parser.add_argument(
        '--correct_orbit_between_acqs',
        action='store_true',
        default=params.correct_orbit_between_acqs,
        help='Correct orbit between acquisitions. An ACORM measurment '
        'consists of several BPMs acquisitions for each set of corrector '
        'magnets excitations. If this flag is set, the orbit will be '
        'corrected to SOFBs current reference orbit in between acquisitions'
        f'Defaults to {params.correct_orbit_between_acqs}.',
    )

    args = parser.parse_args()

    name = args.name

    meas_orm = MeasACORM(isonline=True)

    if check_configdb_entry(args.ref_respmat_name, meas_orm):
        print(
            'No reference respmat found with res name ' + args.ref_respmat_name
        )
        print('Exiting.')
        sys.exit(1)

    signal.signal(signal.SIGINT, partial(_stop_now, meas_orm))
    signal.signal(signal.SIGTERM, partial(_stop_now, meas_orm))

    if check_previous_loco_input_data(name):
        sys.exit(1)

    configure(meas_orm, args)

    print('Waiting PVs to connect...')

    if not meas_orm.wait_for_connection(CONN_TIMEOUT):
        print('\tSome PVs did not connect! Disconnected PVs:\n')
        for pvname in meas_orm.disconnected_pvnames:
            print(f'\t{pvname}')
        print('Exiting.')
        sys.exit(1)

    print('\tDone!')

    print('Measurement configured.')

    if args.print_setup:
        print(meas_orm.params)

    if not args.run_meas:
        print(
            'Exiting.'
            + 'If you want to run the measurement, use the --run-meas flag.'
        )
        sys.exit(0)

    print(80 * '#')
    print('Starting AC ORM measurement.')

    meas_orm.start()
    meas_orm.wait_measurement(MEAS_TIMEOUT)
    meas_orm.process_data()

    print('Measurement finished and processed.')

    print(f'\tFinished ok? {meas_orm.check_measurement_finished_ok()}')
    print(f'\tGood quality? {meas_orm.check_measurement_quality()}')

    if args.save_acq_data:
        print('Saving acquisitions data...')
        meas_orm.save_data(name + '_acq_data.pickle')
        print(
            'Acquisitions data (unprocessed) saved to '
            + f'{name}_acq_data.pickle'
        )

    print('Saving LOCO input data...')
    meas_orm.save_loco_input_data(name + '_loco_input_data.pickle')
    print(f'LOCO input data saved to {name}_loco_input_data.pickle')
    print(
        'Use `sirius-script-si-loco-run_fitting.py` to fit model to this data'
    )

    if args.save2configdb:
        if check_configdb_entry(name, meas_orm, True):
            print('Saving measured AC ORM to configDB...')
            meas_orm.save_respmat_to_configdb(name)
            print('Done!')
        else:
            print('Data not saved to configDB!')

    # meas_respmat = meas_orm.build_respmat()
    # ref_respmat = meas_orm.get_ref_respmat()
    # TODO: proceed with analysis and analysis report (similar to LOCO's)


if __name__ == '__main__':
    main()
