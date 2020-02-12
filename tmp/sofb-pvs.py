#!/usr/bin/env python-sirius

from siriuspy.csdevice.orbitcorr import SOFBFactory

PREFIX = {
    'SI': 'SI-Glob:AP-SOFB',
    'TS': 'TS-Glob:AP-SOFB',
    'BO': 'BO-Glob:AP-SOFB',
    'TB': 'TB-Glob:AP-SOFB',
}


def get_sofb_pvs(acc='SI'):
    """."""
    fact = SOFBFactory.create(acc)
    dbase = fact.get_ioc_database()
    for item in dbase:
        print(PREFIX[acc] + ':' + item)


get_sofb_pvs('TB')
