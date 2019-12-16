#!/usr/bin/env python-sirius
"""."""

import time
import epics
from siriuspy.search import PSSearch


def get_pvs():
    """."""
    psnames = PSSearch.get_psnames()
    pvs = dict()
    for psname in psnames:
        if psname[:2] in ('TB', 'TS', 'SI') and \
                'FCH' not in psname and \
                'FCV' not in psname and \
                'PU' not in psname:
            pvs[psname] = epics.PV(psname + ':WfmUpdateAuto-Sel')
    return pvs


def update_on_off(pvs, value):
    """."""
    yok, nok = [], []
    for psname, pvobj in pvs.items():
        if pvobj.connected:
            pvobj.value = value
            yok.append(psname)
        else:
            nok.append(psname)

    print('OK pwrsupply:')
    for psname in yok:
        print(psname)
    print()
    print('Not OK pwrsupply:')
    for psname in nok:
        print(psname)


def run():
    """."""
    pvs = get_pvs()
    time.sleep(2.0)
    update_on_off(pvs, 0)


run()
