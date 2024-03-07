#!/usr/bin/env python-sirius

import time

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


def check_pvs_set(conn, pvnames, time_start, time_stop):
    """."""
    # get data
    pvds = PVDataSet(pvnames, connector=conn)
    pvds.timeout = 30
    pvds.time_start = time_start
    pvds.time_stop = time_stop
    pvds.update()

    # check
    for pvname in pvnames:
        pvd = pvds[pvname]
        stamp, value = pvd.timestamp, pvd.value
        if stamp is not None and len(stamp) < 2:
            continue
        try:
            stamp0 = Time(stamp[0]).get_iso8601()
            stamp1 = Time(stamp[-1]).get_iso8601()
            print(f'{pvname} {len(stamp)} {stamp0} {stamp1} {len(set(value))}')
        except TypeError:
            print(f'{pvname} ...type error...')
        except IndexError:
            print(f'{pvname} ...index error...')


conn = create_connector()
all_pvnames = conn.getAllPVs('*PS*')
print(f'number of pvs : {len(all_pvnames)}')
pvnames_sp, pvnames_rb, pvnames_others = categorize_pvnames(all_pvnames)
print(f'nr sp pvs     : {len(pvnames_sp)}')
print(f'nr rb pvs     : {len(pvnames_rb)}')
print(f'nr other pvs  : {len(pvnames_others)}')
time_start = Time(2024,2,5,8,0,0)
time_stop = Time(2024,2,6,8,0,0)

for pvname in pvnames_sp:
    check_pvs_set(conn, [pvname], time_start, time_stop)

# for i in range(50):
#     print(i)
#     i1 = min(len(pvnames_sp), 100*i)
#     i2 = min(len(pvnames_sp), 100*(i+1))
#     check_pvs_set(conn, pvnames_sp[i1:i2], time_start, time_stop)

