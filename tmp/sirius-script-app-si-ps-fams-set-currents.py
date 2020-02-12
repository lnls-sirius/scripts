#!/usr/bin/env python


import time
import epics


setpoints = {
    'SI-Fam:PS-B1B2-1': 380.00,
    'SI-Fam:PS-B1B2-2': 380.00,
    'SI-Fam:PS-QFA': 122.45,
    'SI-Fam:PS-QFB': 139.81,
    'SI-Fam:PS-QFP': 139.81,
    'SI-Fam:PS-QDA': 64.12,
    'SI-Fam:PS-QDB1': 79.34,
    'SI-Fam:PS-QDB2': 135.09,
    'SI-Fam:PS-QDP1': 79.34,
    'SI-Fam:PS-QDP2': 135.09,
    'SI-Fam:PS-Q1': 96.49,
    'SI-Fam:PS-Q2': 148.81,
    'SI-Fam:PS-Q3': 110.88,
    'SI-Fam:PS-Q4': 134.81,
    'SI-Fam:PS-SDA0': 53.38,
    'SI-Fam:PS-SDB0': 42.88,
    'SI-Fam:PS-SDP0': 42.88,
    'SI-Fam:PS-SFA0': 34.71,
    'SI-Fam:PS-SFB0': 48.69,
    'SI-Fam:PS-SFP0': 48.69,
    'SI-Fam:PS-SDA1': 107.62,
    'SI-Fam:PS-SDA2': 58.67,
    'SI-Fam:PS-SDA3': 92.41,
    'SI-Fam:PS-SFA1': 126.67,
    'SI-Fam:PS-SFA2': 99.56,
    'SI-Fam:PS-SDB1': 93.52,
    'SI-Fam:PS-SDB2': 80.71,
    'SI-Fam:PS-SDB3': 114.77,
    'SI-Fam:PS-SFB1': 150.47,
    'SI-Fam:PS-SFB2': 130.62,
    'SI-Fam:PS-SDP1': 93.97,
    'SI-Fam:PS-SDP2': 80.74,
    'SI-Fam:PS-SDP3': 115.00,
    'SI-Fam:PS-SFP1': 151.38,
    'SI-Fam:PS-SFP2': 131.08}


def create_pvs(field, timeout=5.0):
    """."""
    psnames = list(setpoints.keys())

    # create PV objects
    pvs = dict()
    for psname in psnames:
        pvs[psname] = epics.PV(psname + ':' + field)

    # check connection
    psnames_nok = psnames[:]
    time0 = time.time()
    while psnames_nok and time.time() - time0 < timeout:
        for psname in psnames:
            if pvs[psname].connected and psname in psnames_nok:
                psnames_nok.remove(psname)
        time.sleep(0.1)
    if psnames_nok:
        print('timed out!')
        print(psnames_nok)
        return {}

    return pvs


def print_currents():
    """."""
    print('Printing current values')
    pvs_sp = create_pvs(field='Current-SP', timeout=5.0)
    pvs_mon = create_pvs(field='Current-Mon', timeout=5.0)
    for psname in pvs_sp:
        pv_sp = pvs_sp[psname]
        pv_mon = pvs_mon[psname]
        msg = '!!! ' if abs(pv_mon.value - pv_sp.value) > 0.1 else ''
        print('{}{:<20s} [A],  SP:{}, Mon:{}'.format(
            msg, pv_sp.pvname, pv_sp.value, pv_mon.value))


def set_pwrsupplies():
    """."""
    print('Setting default values for SI power supplies')
    pvs_sp = create_pvs(field='Current-SP', timeout=5.0)
    for psname in pvs_sp:
        pv_sp = pvs_sp[psname]
        pv_sp.value = setpoints[psname]


set_pwrsupplies()
print_currents()
