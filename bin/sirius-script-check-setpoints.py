#!/usr/bin/env python-sirius

import time
import numpy as np

from siriuspy.clientarch import ClientArchiver, PVDataSet, Time


suffix_sp_pvs = ('-SP', '_SP', '-Sel', '-Cmd', '-sp', '-sel', '-cmd', 'SEL', '_CMD')
suffix_rb_pvs = (
    '-Mon', '-RB', '-Sts', '-Cte',
    '-mon', '-rb', '-sts', '-cte',
    '-Mon-s', 'Unit', '-raw', 'Dose', '-rate', 'temp', 'level', '_MON', '_STATUS',
    'VMAX', 'RTRY', 'SREV', 'UEIP', 'UREV', 'VELO', 'DESC', 'Type-A', 'Type-B',
    'Type-C', 'Number', 'Alpha', 'CTLV',
    '-CH1', '-CH2', '-CH3', '-CH4', '-CH5',
    'RVAL', '_RBV', 'ACCL', 'ATHM', 'BACC', 'BDST', 'BVEL',
    'DIR', 'EGU', 'ERES', 'HLM', 'HOMF', 'HOMR', 'LLM', 'MISS',
    'MRES', 'NTM', 'RDBD', 'RMOD', '_CRC', '_ERROR', '_POLL', '_TIMEOUT',
    '_WARN', 'ROI1MinX', 'ROI1MinY', 'ROI1SizeX', 'ROI1SizeY', 'ROI2SizeX',
    'ROI2SizeY', 'ROI2MinX', 'ROI2MinY', 'CursorX', 'CursorY', 'Use', ':S',
    'TXREADY', 'VACINVERT', 'VACUUM', 'ILK:0',
    'TS1', 'TS2', 'TS3', 'TS4', 'TS5', 'TS6', 'TS7',
    'Raw-U:C0', 'Raw-U:C1', 'Raw-U:C2', 'Raw-U:C3', 'Raw-U:C4',
    'TEMP', '-W', 'Teste:Redis:value', 'testpvRedisIoc',)


def create_connector(timeout=1):
    """."""
    conn = ClientArchiver()
    t0 = time.time()
    while time.time() - t0 < timeout:
        if conn.connected:
            return conn
        time.sleep(0.1)
    print('could not connect to configdb!')
    return None


def get_all_pvnames(conn):
    """."""
    if conn:
        return conn.getAllPVs('*')
    else:
        return None

def categorize_pvnames(all_pvnames):
    """."""
    pvnames_sp = []
    pvnames_rb = []
    pvnames_others = []
    for pvname in all_pvnames:
        if pvname.endswith(suffix_sp_pvs):
            pvnames_sp.append(pvname)
        elif pvname.endswith(suffix_rb_pvs):
            pvnames_rb.append(pvname)
        else:
            pvnames_others.append(pvname)
    return pvnames_sp, pvnames_rb, pvnames_others


def check_pvs_set(conn, pvnames, time_start, time_stop, nrpvs, offset, only_pvnames):
    """."""
    # get dataset 1
    pvds1 = PVDataSet(pvnames, connector=conn)
    pvds1.timeout = 30
    pvds1.time_start = time_start
    pvds1.time_stop = time_start + 60
    pvds1.update()

    # get dataset 2
    pvds2 = PVDataSet(pvnames, connector=conn)
    pvds2.timeout = 30
    pvds2.time_start = time_stop - 60
    pvds2.time_stop = time_stop
    pvds2.update()

    # check
    for pvname in pvnames:
        # get pv data from the two time intervals and concatenate data
        pvd1, pvd2 = pvds1[pvname], pvds2[pvname]
        stamp = np.array(list(pvd1.timestamp) + list(pvd2.timestamp))
        value = np.array(list(pvd1.value) + list(pvd2.value))

        # sort concatenated data by timestamp
        indices = np.argsort(stamp)
        stamp = stamp[indices]
        value = value[indices]

        # remove duplicate data (same timestamp)
        stamp, indices = np.unique(stamp, return_index=True)
        value = value[indices]

        offset += 1
        # if only one data point, no change, continue loop...
        if len(stamp) < 2:
            # print('no change!')
            continue
        else:
            if only_pvnames:
                print(pvname)
            else:
                print(f'{offset:06d}/{nrpvs:06d} - {pvname} - ', end='', flush=True)
                print(f'changed {len(stamp)-1:04d}')

    return offset


# parameters
filter = 'BO*PS*'
time_start = Time(2024,2,5,8,0,0)
time_stop = Time(2024,2,6,8,1,0)
nrchk = 50
only_pvnames = False

# list PV in categories
conn = create_connector()
all_pvnames = conn.getAllPVs(filter)
pvnames_sp, pvnames_rb, pvnames_others = categorize_pvnames(all_pvnames)
if not only_pvnames:
    print(f'filter        : {filter}')
    print(f'number of pvs : {len(all_pvnames)}')
    print(f'nr sp pvs     : {len(pvnames_sp)}')
    print(f'nr rb pvs     : {len(pvnames_rb)}')
    print(f'nr other pvs  : {len(pvnames_others)}')

# run analysis
offset = 0
nrpvs = len(pvnames_sp)
for i in range(1 + nrpvs // nrchk):
    i1, i2 = min(nrchk*i, nrpvs), min(nrchk*(i+1), nrpvs)
    pvnames = pvnames_sp[i1:i2]
    offset = check_pvs_set(conn, pvnames, time_start, time_stop, nrpvs, offset, only_pvnames)
