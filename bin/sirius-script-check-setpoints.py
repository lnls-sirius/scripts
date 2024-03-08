#!/usr/bin/env python-sirius

import time
import numpy as np

from siriuspy.clientarch import ClientArchiver, PVData, PVDataSet, Time


class CheckPVsChange:
    """."""

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

    def __init__(self, time_beg, time_end=None, filter=None, timeout=50):
        """."""
        time_end = time_end if time_end else Time.now()
        filter = filter if filter else '*'
        self._time_beg = time_beg
        self._time_end = time_end
        self._filter = filter
        self._timeout = timeout
        self._conn = self._create_connector()

    def _create_connector(self):
        """."""
        conn = ClientArchiver()
        t0 = time.time()
        while time.time() - t0 < self._timeout:
            if conn.connected:
                return conn
            time.sleep(0.1)
        print('could not connect to configdb!')
        return None

    def get_all_pvnames(self):
        """."""
        return self._conn.getAllPVs(self._filter)

    def categorize_pvnames(self, all_pvnames):
        """."""
        pvnames_sp = []
        pvnames_rb = []
        pvnames_others = []
        for pvname in all_pvnames:
            if pvname.endswith(self.suffix_sp_pvs):
                pvnames_sp.append(pvname)
            elif pvname.endswith(self.suffix_rb_pvs):
                pvnames_rb.append(pvname)
            else:
                pvnames_others.append(pvname)
        return pvnames_sp, pvnames_rb, pvnames_others

    def get_pv_data(self, pvname):
        """."""
        # get dataset 1
        pvd1 = PVData(pvname, connector=self._conn)
        pvd1.timeout = self._timeout
        pvd1.time_start = self._time_beg
        pvd1.time_stop = self._time_beg + 60  # 1 min interval
        pvd1.update()

        # get dataset 2
        pvd2 = PVData(pvname, connector=self._conn)
        pvd2.timeout = self._timeout
        pvd2.time_start = self._time_end - 60  # 1 min interval
        pvd2.time_stop = self._time_end
        pvd2.update()

        return pvd1.timestamp, pvd1.value, pvd2.timestamp, pvd2.value

    def check_pvs_set(self, pvnames, nrpvs, offset, only_pvnames):
        """."""
        # get dataset 1
        pvds1 = PVDataSet(pvnames, connector=self._conn)
        pvds1.timeout = self._timeout
        pvds1.time_start = self._time_beg
        pvds1.time_stop = self._time_beg + 60  # 1 min interval
        pvds1.update()

        # get dataset 2
        pvds2 = PVDataSet(pvnames, connector=self._conn)
        pvds2.timeout = self._timeout
        pvds2.time_start = self._time_end - 60  # 1 min interval
        pvds2.time_stop = self._time_end
        pvds2.update()

        # check
        for pvname in pvnames:
            # get pv data from the two time intervals and concatenate data
            pvd1, pvd2 = pvds1[pvname], pvds2[pvname]

            if pvd1.timestamp is None or pvd2.timestamp is None or pvd1.value is None or pvd2.value is None:
                print(f'{offset:06d}/{nrpvs:06d} - {pvname} - ', end='', flush=True)
                print(f'None!')
                continue
            try:
                stamp = np.array(list(pvd1.timestamp) + list(pvd2.timestamp))
                value = np.array(list(pvd1.value) + list(pvd2.value))
            except TypeError:
                print(pvname)
                print(pvd1.timestamp)
                print(pvd2.timestamp)
                print(pvd1.value)
                print(pvd2.value)
                continue

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

    def run_check(self, nrchk=50, only_pvnames=False):
        """."""
        # list PV in categories
        all_pvnames = self.get_all_pvnames()
        pvnames_sp, pvnames_rb, pvnames_others = self.categorize_pvnames(all_pvnames)
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
            offset = self.check_pvs_set(pvnames, nrpvs, offset, only_pvnames)


if __name__ == "__main__":
    # parameters
    filter = '*'
    timeout = 50  # [s]
    time_beg = Time(2024,3,6,21,0,0)
    time_end = Time(2024,3,7,21,0,0)
    nrchk = 50
    only_pvnames = False

    cpvsc = CheckPVsChange(time_beg, time_end, filter=filter, timeout=timeout)
    cpvsc.run_check(nrchk, only_pvnames)

    t1, v1, t2, v2 = cpvsc.get_pv_data('BO-RA09:VA-SIPC-01:Autostart-SP')
    print(t1, v1)
    print(t2, v2)
