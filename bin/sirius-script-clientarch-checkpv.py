#!/usr/bin/env python-sirius


import sys
import re

# import matplotlib.pyplot as plt

from siriuspy.clientarch import ClientArchiver
from siriuspy.clientarch import PV, PVDetails
from siriuspy.search import PSSearch
from siriuspy.pwrsupply.data import PSData



def get_pvs(accelerator, pattern):
    """."""
    regexp = re.compile(pattern)
    psnames = PSSearch.get_psnames({'sec': accelerator})
    pvslist = []
    for psname in psnames:
        psdata = PSData(psname)
        dbase = psdata.propty_database
        for prop in dbase:
            pvname = psname + ':' + prop
            if regexp.match(pvname):
                pvslist.append(pvname)
    return pvslist


def check_is_archived(accelerator, pattern):
    """."""
    connector = ClientArchiver()
    pvslist = get_pvs(accelerator, pattern)
    for pvname in pvslist:
        pvarch = PVDetails(pvname, connector=connector)
        status = pvarch.is_archived
        print('{:<60s} {}'.format(pvname, status))


def check_is_connected(accelerator, pattern):
    """."""
    connector = ClientArchiver()
    pvslist = get_pvs(accelerator, pattern)
    for pvname in pvslist:
        pvarch = PVDetails(pvname, connector=connector)
        pvarch.update()
        status = pvarch.is_connected
        print('{:<60s} {}'.format(pvname, status))


def check_is_paused(accelerator, pattern):
    """."""
    connector = ClientArchiver()
    pvslist = get_pvs(accelerator, pattern)
    for pvname in pvslist:
        pvarch = PVDetails(pvname, connector=connector)
        pvarch.update()
        status = pvarch.is_paused
        print('{:<60s} {}'.format(pvname, status))


def check_estimated_storage_rate_kb_hour(accelerator, pattern):
    """."""
    connector = ClientArchiver()
    pvslist = get_pvs(accelerator, pattern)
    for pvname in pvslist:
        pvarch = PVDetails(pvname, connector=connector)
        pvarch.update()
        kb_hour = pvarch.estimated_storage_rate_kb_hour
        print('{:<60s} {}'.format(pvname, kb_hour))


def run():
    """."""
    if len(sys.argv) != 4:
        print('sirius-script-clientarch-checkpv.py OPTION ACC PATTERN')
        print('  OPTION:')
        print('    --archived')
        print('    --connected')
        print('    --paused')
        print('    --storage-kb-hour')
        return
    test_type = sys.argv[1]
    accelerator = sys.argv[2]
    pattern = sys.argv[3]
    if test_type == '--archived':
        check_is_archived(accelerator, pattern)
    elif test_type == '--connected':
        check_is_connected(accelerator, pattern)
    elif test_type == '--paused':
        check_is_paused(accelerator, pattern)
    elif test_type == '--storage-kb-hour':
        check_estimated_storage_rate_kb_hour(accelerator, pattern)


run()
