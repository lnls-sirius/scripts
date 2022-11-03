#!/usr/bin/env python-sirius

import matplotlib.pyplot as plt
import numpy as np

from siriuspy.clientarch import Time, PVData, PVDataSet


def example_1pv():
    pvd = PVData(pvname='SI-01M1:PS-CH:Current-Mon')
    print(pvd.connected)
    print(pvd.is_archived)
    pvd.time_start = Time(2022, 11, 3, 19, 19, 0)
    pvd.time_stop = Time(2022, 11, 3, 19, 20, 0)
    print(pvd.request_url)
    pvd.update()

    tim = np.array(pvd.timestamp)
    data = np.array(pvd.value)

    plt.plot(tim - tim[0], data - data[0])
    plt.show()


def example_manypvs():
    pvnames = ['SI-01M1:PS-CH:Current-Mon', 'SI-01M2:PS-CH:Current-Mon', 'SI-Glob:AP-CurrInfo:Current-Mon']
    pvd = PVDataSet(pvnames=pvnames)
    print(pvd.connected)
    print(pvd.is_archived)
    pvd.time_start = Time(2022, 11, 2, 19, 19, 0)
    pvd.time_stop = Time(2022, 11, 3, 19, 20, 0)
    # print(pvd.request_url)
    pvd.update()

    pvd0 = pvd[pvnames[0]]
    pvd1 = pvd[pvnames[1]]
    pvd2 = pvd[pvnames[2]]
    tim0 = np.array(pvd0.timestamp)
    data0 = np.array(pvd0.value)
    tim1 = np.array(pvd1.timestamp)
    data1 = np.array(pvd1.value)
    tim2 = np.array(pvd2.timestamp)
    data2 = np.array(pvd2.value)

    plt.plot(tim0 - tim0[0], data0 - data0[0], label=pvnames[0])
    plt.plot(tim1 - tim1[0], data1 - data1[0], label=pvnames[1])
    plt.plot(tim2 - tim2[0], (data2 - data2[0])/40, label=pvnames[2])
    plt.legend()
    plt.show()


example_manypvs()