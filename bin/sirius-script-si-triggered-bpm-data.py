#!/usr/bin/env python-sirius
"""."""

from siriuspy.devices import BunchbyBunch, SOFB, HLFOFB
from apsuite.commisslib.measure_orbit_stability import \
        OrbitAcquisition
from siriuspy.devices import BOPSRampStandbyHandler, BORFRampStandbyHandler
import sys


def configure_acquisition_params(orbacq):
    """."""
    params = orbacq.params

    # params.orbit_acq_rate = 'FAcq'
    # params.orbit_timeout = 100

    params.orbit_acq_rate = 'TbT'
    params.orbit_timeout = 60*4  # 3 minutes between top-up injections

    params.orbit_nrpoints_before = 1_000
    params.orbit_nrpoints_after = 10_000
    params.orbit_acq_repeat = 0
    params.trigbpm_delay = 0
    params.trigbpm_nrpulses = 1
    params.do_pulse_evg = False
    params.event_mode = 'Injection'
    params.timing_event = 'Linac'
    print('--- orbit acquisition configuration ---')
    print(params)


def measure(orbacq):
    """."""
    init_state_orbacq = orbacq.get_initial_state()
    orbacq.prepare_timing()
    print('Waiting for next injection pulse')
    print('Take a look at Injection Control Log to check for next injection')
    orbacq.acquire_data()
    orbacq.recover_initial_state(init_state_orbacq)


def initialize():
    """."""
    orbacq = OrbitAcquisition(isonline=True)
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
    if orbacq.data is not None:
        orbacq.data['sofb_loop_state'] = sofb.autocorrsts
        orbacq.data['fofb_loop_state'] = fofb.loop_state
        orbacq.data['bbbl_loop_state'] = bbbl.feedback.loop_state
        orbacq.data['bbbh_loop_state'] = bbbh.feedback.loop_state
        orbacq.data['bbbv_loop_state'] = bbbv.feedback.loop_state
        orbacq.data['bo_ps_ramp_state'] = bopsrmp.is_on
        orbacq.data['bo_rf_ramp_state'] = borfrmp.is_on
    else:
        raise Exception('data is None, problem with acquisition!')


if __name__ == "__main__":
    """."""
    orbacq = initialize()
    devs = create_devices()

    measure(orbacq)
    read_feedback_status(devs, orbacq)

    filename = sys.argv[1]
    orbacq.save_data(filename, overwrite=False)
