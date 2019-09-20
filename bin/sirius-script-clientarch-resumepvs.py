#!/usr/bin/env python-sirius

import time
import getpass
import epics
from siriuspy.clientarch import ClientArchiver


DEFAULT_FUNCTION = 'NONE'


def get_authentication():
    """."""
    username = input('archiver username: ')
    password = getpass.getpass('username password: ')
    return username, password


def create_carch():
    """."""
    carch = ClientArchiver()
    username, password = get_authentication()
    # username, password = 'ximenes.resende', 'SENHA'
    ret = carch.login(username, password)
    if not ret:
        print('Could not be authenticated!')
        return
    return carch


def get_paused_and_filter_pvs(filt, carch=None):
    """."""
    if carch is None:
        carch = create_carch()

    pvnames = []
    data = carch.getPausedPVsReport()
    for datum in data:
        pvname = datum['pvName']
        if filt in pvname:
            pvnames.append(pvname)
    return pvnames, carch


def resume_pvs(pvnames, carch=None):
    """."""
    if carch is None:
        carch = create_carch()

    carch.resumePVs(pvnames)


def resume_ps_pvs():
    """."""
    pvnames, carch = get_paused_and_filter_pvs(':PS-')
    timeout = 10.0

    # check which paused PVs are online
    pvs_object = {pvname: epics.PV(pvname) for pvname in pvnames}
    pvs_disconnected = pvnames[:]
    pvs_connected = []
    time0 = time.time()
    fmtl = 'checking online and offline paused pvs... ETA: {:.0f} s     \r'
    while time.time() - time0 < timeout:
        for pvname in pvs_disconnected[:]:
            if pvs_object[pvname].connected:
                pvs_disconnected.remove(pvname)
                pvs_connected.append(pvname)
        time.sleep(0.010)
        print(fmtl.format(timeout - (time.time() - time0)), end='')
        if not pvs_disconnected:
            break
    print()
    print()

    # print offline paused PVs
    print('offline paused pvs...')
    print()
    for pvname in pvs_disconnected:
        print('{}'.format(pvname))
    print()

    # print online paused PVs
    print('online paused pvs...')
    print()
    for pvname in pvs_connected:
        print('{}'.format(pvname))
    print()

    # resuming all online pvs
    print('resuming online paused pvs...')
    resume_pvs(pvs_connected, carch)


def run():
    """."""
    resume_ps_pvs()


if __name__ == "__main__":
    run()
