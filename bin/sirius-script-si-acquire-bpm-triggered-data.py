#!/usr/bin/env python-sirius
"""."""

from siriuspy.devices import BunchbyBunch, SOFB, HLFOFB
from apsuite.commisslib.meas_bpms_signals import AcqBPMsSignals
from siriuspy.devices import BOPSRampStandbyHandler, BORFRampStandbyHandler
import sys
from datetime import datetime


def configure_acquisition_params(orbacq):
    """."""
    params = orbacq.params
    params.signals2acq = 'XY'

    # params.orbit_acq_rate = 'FAcq'
    # params.orbit_timeout = 100

    params.acq_rate = 'TbT'
    params.timeout = 60*4  # 3 minutes between top-up injections

    params.nrpoints_before = 1_000
    params.nrpoints_after = 10_000
    params.acq_repeat = False
    params.trigbpm_delay = 0
    params.trigbpm_nrpulses = 1
    params.do_pulse_evg = False
    params.event_mode = 'Injection'
    params.timing_event = 'Linac'
    print('--- orbit acquisition configuration ---')
    print(params)


def measure(orbacq):
    """."""
    init_state_orbacq = orbacq.get_timing_state()
    orbacq.prepare_timing()
    print('Waiting for next injection pulse')
    print('Take a look at Injection Control Log to check for next injection')
    orbacq.acquire_data()
    orbacq.recover_timing_state(init_state_orbacq)
    return orbacq.data is not None

def initialize():
    """."""
    orbacq = AcqBPMsSignals(isonline=True)
    configure_acquisition_params(orbacq)
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
    orbacq = initialize()
    devs = create_devices()

    if measure(orbacq):
        read_feedback_status(devs, orbacq)
        now = datetime.now()
        snow = now.strftime('%Y-%m-%d_%Hh%Mm%Ss')
        filename = sys.argv[1]
        orbacq.save_data(snow + '_' + filename, overwrite=False)
        print(f'\nData saved at {snow:s}')
    else:
        print('\nData NOT saved!')

