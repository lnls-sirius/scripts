#!/usr/bin/env python-sirius
"""."""

import time as _time
from datetime import datetime

from mathphys.functions import save
from siriuspy.devices import BOPSRampStandbyHandler, BORFRampStandbyHandler, \
    BunchbyBunch, FamFOFBLamp, HLFOFB, SOFB


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


def read_feedback_status(devs, data):
    """."""
    sofb, fofb, bbbl, bbbh, bbbv, bopsrmp, borfrmp = devs
    data['sofb_loop_state'] = sofb.autocorrsts
    data['fofb_loop_state'] = fofb.loop_state
    data['bbbl_loop_state'] = bbbl.feedback.loop_state
    data['bbbh_loop_state'] = bbbh.feedback.loop_state
    data['bbbv_loop_state'] = bbbv.feedback.loop_state
    data['bo_ps_ramp_state'] = bopsrmp.is_on
    data['bo_rf_ramp_state'] = borfrmp.is_on


if __name__ == "__main__":
    """."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="FOFB LAMP triggered acquisition script.")
    parser.add_argument(
        '-f', '--filename', type=str, default='',
        help='name of the file to save (Default: FOFBLAMP-_YY-MM-DD_HHhMMmSSs)')
    # 3 minutes between top-up injections, timeout > 3*60s
    parser.add_argument(
        '-b', '--nrptsbefore', type=int, default=500_000,
        help='nr points before trigger (Default: 500000)')
    parser.add_argument(
        '-a', '--nrptsafter', type=int, default=500_000,
        help='nr points after trigger (Default: 500000)')

    args = parser.parse_args()

    # prepare acquisition
    lampacq = FamFOFBLamp(event='Study')

    print('Configuring lamp...')
    for dev in lampacq.ctrldevs.values():
        dev.cmd_ctrl(1)  # stop
    for dev in lampacq.ctrldevs.values():
        dev.nrsamples_pre = args.nrptsbefore
    for dev in lampacq.ctrldevs.values():
        dev.nrsamples_post = args.nrptsafter
    for dev in lampacq.ctrldevs.values():
        dev.repeat = 0  # normal
    for dev in lampacq.ctrldevs.values():
        dev.trigger = 1  # external
    for dev in lampacq.ctrldevs.values():
        dev.cmd_ctrl(0)  # start
    print('...done...')
    _time.sleep(2)

    # trigger acquisition
    print('...sending trigger...')
    lampacq.evtdev.cmd_external_trigger()

    # sleep waiting for data
    print('...waiting for data...')
    _time.sleep(30)
    print('...done...')

    # create devices to complement data
    devs = create_devices()

    # get lamp data
    print('...getting data...')
    data = dict()
    for datatyp in ['Current', 'Voltage']:
        data[datatyp] = dict()
        for psname, psdev in lampacq.psdevs.items():
            pvo = psdev.pv_object(f'LAMP{datatyp}Data')
            data[datatyp][psname] = pvo.get(use_monitor=False, timeout=5.0)

    # get extra data
    read_feedback_status(devs, data)

    # save file
    print('...saving data to file...')
    now = datetime.now()
    str_now = now.strftime('%Y-%m-%d_%Hh%Mm%Ss')
    filename = args.filename or 'FOFBLAMP' + str_now
    save(data, filename + '.hdf5', overwrite=False, compress=True)
    print(f'\nData saved at {str_now:s}')
