#!/usr/bin/env python-sirius

"""Benchmark script."""

import time
import numpy as np
import epics


def create_pv(pvname, timeout=2.0):
    """."""
    pvobj = epics.PV(pvname)
    time0 = time.time()
    while not pvobj.connected:
        time.sleep(0.1)
        if time.time() - time0 > timeout:
            return None
    return pvobj


def benchmark(pvname, interval=5.0):
    """."""
    # create connection
    pvobj = create_pv(pvname, timeout=1.0)
    if pvobj is None:
        return None

    # do benchmarking
    time0 = time.time()
    timestamps = []
    while time.time() - time0 < interval:
        timestamp = pvobj.get_timevars()['timestamp']
        if not timestamps or timestamp != timestamps[-1]:
            timestamps.append(timestamp)

    # estimate update rate
    dtime = np.diff(timestamps)
    avg, std = np.average(dtime), np.std(dtime)
    dtime = timestamps[-1] - timestamps[0]
    nrupdates = len(timestamps) - 1
    rate = nrupdates / dtime
    return rate, nrupdates, dtime, avg, std


def run_benchmark(pvname, interval=10.0):
    """."""
    result = benchmark(pvname, interval)
    if result is None:
        print('Could not connect!')
        return
    rate, nrupdates, dtime, avg, std = result
    print('pvname         : {}'.format(pvname))
    print('acq dtime      : {:.6f} s'.format(dtime))
    print('number updates : {}'.format(nrupdates))
    print('update rate    : {:.2f} updates/s'.format(rate))
    print('interval (avg) : {:06.2f} ms'.format(avg*1000))
    print('interval (std) : {:06.2f} ms'.format(std*1000))


def run():
    """."""
    psnames = (
        # 'TB-Fam:PS-B:Current-Mon',
        # 'TB-01:PS-QF1:Current-Mon',
        # 'TB-02:PS-QF2A:Current-Mon',
        # 'TB-02:PS-QF2B:Current-Mon',
        # 'TB-03:PS-QF3:Current-Mon',
        # 'TB-04:PS-QF4:Current-Mon',
        # 'TB-01:PS-CH-1:Current-Mon',
        # 'TB-01:PS-CH-2:Current-Mon',
        # 'TB-02:PS-CH-1:Current-Mon',
        # 'TB-02:PS-CH-2:Current-Mon',
        # 'TB-04:PS-CH-1:Current-Mon',
        # 'TB-04:PS-CH-2:Current-Mon',
        # 'TB-01:PS-CV-1:Current-Mon',
        # 'TB-01:PS-CV-2:Current-Mon',
        # 'TB-02:PS-CV-1:Current-Mon',
        # 'TB-02:PS-CV-2:Current-Mon',
        # 'TB-04:PS-CV-1:Current-Mon',
        # 'TB-04:PS-CV-2:Current-Mon',

        # 'BO-Fam:PS-B-1:TimestampUpdate-Mon',
        # 'BO-Fam:PS-B-1:Current-Mon',
        # 'BO-Fam:PS-B-2:TimestampUpdate-Mon',
        # 'BO-Fam:PS-B-2:Current-Mon',
        # 'BO-03U:PS-CH:TimestampUpdate-Mon',
        # 'BO-03U:PS-CH:Current-Mon',

        'SI-01M2:PS-CH:TimestampUpdate-Mon',
        'SI-01M2:PS-CH:Current-Mon',
        # 'SI-03C3:PS-CV-2:TimestampUpdate-Mon',
        # 'SI-03C3:PS-CV-2:Current-Mon',
        # 'SI-Glob:AP-SOFB',
    )
    for psname in psnames:
        run_benchmark(psname, interval=10.0)
        print()


run()
