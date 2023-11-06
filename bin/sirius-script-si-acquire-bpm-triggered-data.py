#!/usr/bin/env python-sirius
"""."""

from siriuspy.devices import BunchbyBunch, SOFB, HLFOFB
from apsuite.commisslib.meas_bpms_signals import AcqBPMsSignals
from siriuspy.devices import BOPSRampStandbyHandler, BORFRampStandbyHandler
from datetime import datetime

def configure_acquisition_params(orbacq, parse_args):
    """."""
    args = parse_args
    params = orbacq.params
    params.signals2acq = args.signals2acq  # Default: 'XY'
    params.acq_rate = args.acqrate  # Default: 'TbT'
    params.timeout = args.timeout  # Default: 200 [s]

    params.nrpoints_before = args.nrptsbefore  # Default: 1000
    params.nrpoints_after = args.nrptsafter  # Default: 10000
    params.acq_repeat = False
    params.trigbpm_delay = None
    params.trigbpm_nrpulses = 1

    params.timing_event = args.eventname  # Default: 'Linac'
    params.event_mode = args.eventmode   # Default: 'Injection'
    params.event_delay = None
    params.do_pulse_evg = args.pulseevg  # Default: False
    print('--- orbit acquisition configuration ---')
    print(params)


def measure(orbacq):
    """."""
    init_state = orbacq.get_timing_state()
    orbacq.prepare_timing()
    print('Waiting for next injection pulse')
    print('Take a look at Injection Control Log to check for next injection')
    try:
        orbacq.acquire_data()
    except Exception as e:
        print(f"An error occurred during acquisition: {e}")
    # Restore initial timing state, regardless acquisition status
    orbacq.recover_timing_state(init_state)
    return orbacq.data is not None


def initialize(parse_args):
    """."""
    orbacq = AcqBPMsSignals(isonline=True)
    configure_acquisition_params(orbacq, parse_args)
    print('--- orbit acquisition connection ---')
    print(orbacq.wait_for_connection(timeout=100))
    return orbacq


def create_devices():
    """."""
    sofb = SOFB(SOFB.DEVICES.SI)
    fofb = HLFOFB(HLFOFB.DEVICES.SI)
    bbbl = BunchbyBunch(BunchbyBunch.DEVICES.L)
    bbbh = BunchbyBunch(BunchbyBunch.DEVICES.H)
    bbbv = BunchbyBunch(BunchbyBunch.DEVICES.V)
    bopsrmp = BOPSRampStandbyHandler()
    borfrmp = BORFRampStandbyHandler()
    return sofb, fofb, bbbl, bbbh, bbbv, bopsrmp, borfrmp


def read_feedback_status(devs, orbacq):
    """."""
    sofb, fofb, bbbl, bbbh, bbbv, bopsrmp, borfrmp = devs
    orbacq.data['sofb_loop_state'] = sofb.autocorrsts
    orbacq.data['fofb_loop_state'] = fofb.loop_state
    orbacq.data['bbbl_loop_state'] = bbbl.feedback.loop_state
    orbacq.data['bbbh_loop_state'] = bbbh.feedback.loop_state
    orbacq.data['bbbv_loop_state'] = bbbv.feedback.loop_state
    orbacq.data['bo_ps_ramp_state'] = bopsrmp.is_on
    orbacq.data['bo_rf_ramp_state'] = borfrmp.is_on


if __name__ == "__main__":
    """."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="BPM triggered acquisition script. By default the script is configured to acquire injection perturbations during top-up.")
    parser.add_argument(
        '-f', '--filename', type=str, default='',
        help='name of the file to save (Default: acqrate_%Y-%m-%d_%Hh%Mm%Ss)')
    parser.add_argument(
        '-s', '--signals2acq', type=str, default='XY',
        help='signals to acquire (Default: XY)')
    parser.add_argument(
        '-r', '--acqrate', type=str, default='TbT',
        help='acquisition Rate (Default: TbT)')
    # 3 minutes between top-up injections, timeout > 3*60s
    parser.add_argument(
        '-t', '--timeout', type=float, default=200,
        help='acquisition timeout [s] (Default: 200 [s])')
    parser.add_argument(
        '-b', '--nrptsbefore', type=int, default=1_000,
        help='nr points before trigger (Default: 1000)')
    parser.add_argument(
        '-a', '--nrptsafter', type=int, default=10_000,
        help='nr points after trigger (Default: 10000)')
    parser.add_argument(
        '-e', '--eventname', type=str, default='Linac',
        help='timing event name (Default: Linac)')
    parser.add_argument(
        '-m', '--eventmode', type=str, default='Injection',
        help='timing event mode (Default: Injection)')
    parser.add_argument(
        '-p', '--pulseevg', default=False, action='store_true',
        help='pulse EVG? (Default: False)')

    args = parser.parse_args()
    orbacq = initialize(args)
    devs = create_devices()

    if measure(orbacq):
        read_feedback_status(devs, orbacq)
        now = datetime.now()
        str_rate = f'{args.acqrate.lower():s}rate_'
        str_now = now.strftime('%Y-%m-%d_%Hh%Mm%Ss')
        filename = args.filename or str_rate + str_now
        orbacq.save_data(filename, overwrite=False)
        print(f'\nData saved at {str_now:s}')
    else:
        print('\nData NOT saved!')
