#!/usr/bin/env python-sirius
"""."""

import sys
import epics
import numpy as np
import matplotlib.pyplot as plt
import time
from multiprocessing import Process


# obs:
# it is preferable that nrpts_period = 4*(n+1), with n=1,2,...

_dt = 0.5  # [s]
parms = {
    # dt, ampl, nrpts_period, nr_periods, tau_period, sin_squared?
    'TB-Fam:PS-B': [_dt, 250.0, 4*(18+1), 6, 1.5, True],  # 42.6 [A/s]

    'TB-01:PS-QD1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-01:PS-QF1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-QD2A': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-QF2A': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-QD2B': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-QF2B': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-03:PS-QD3': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-03:PS-QF3': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-04:PS-QD4': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-04:PS-QF4': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-01:PS-CH-1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-01:PS-CV-1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-01:PS-CH-2': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-01:PS-CV-2': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-CH-1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-CV-1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-CH-2': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-02:PS-CV-2': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-04:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-04:PS-CV-1': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'TB-04:PS-CV-2': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]

    'BO-Fam:PS-B-1': [_dt, 60.0, 4*(22+1), 6, 1.5, False],  # 9.6 [A/s]
    'BO-Fam:PS-B-2': [_dt, 60.0, 4*(22+1), 6, 1.5, False],  # 9.6 [A/s]
    'BO-Fam:PS-QF': [_dt, 20.0, 4*(11+1), 10, 2, False],  # 5.8 [A/s]
    'BO-Fam:PS-QD': [_dt, 30.0, 4*(11+1), 10, 2, False],  # 8.8 [A/s]
    'BO-Fam:PS-SF': [_dt, 149.0, 4*(11+1), 10, 2, False],  # 43.5 [A/s]
    'BO-Fam:PS-SD': [_dt, 149.0, 4*(11+1), 10, 2, False],  # 43.5 [A/s]
    'BO-02D:PS-QS': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]

    'BO-01U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-01U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-03U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-03U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-05U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-05U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-07U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-07U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-09U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-09U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-11U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-11U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-13U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-13U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-15U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-15U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-17U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-17U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-19U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-19U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-21U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-21U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-23U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-23U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-25U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-25U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-27U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-27U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-29U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-29U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-31U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-31U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-33U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-33U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-35U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-35U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-37U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-37U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-39U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-39U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-41U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-41U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-43U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-43U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-45U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-45U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-47U:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-47U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-49D:PS-CH': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
    'BO-49U:PS-CV': [_dt, 10.0, 4*(11+1), 10, 2, False],  # 2.9 [A/s]
}


def gen_waveform(dt, ampl, nrpts_period, nr_periods, tau_period, square):
    """."""
    period = dt * nrpts_period
    w = 2*np.pi/period
    tau = tau_period*period
    nrpts = nrpts_period * nr_periods
    v = list(range(0, nrpts))
    t = dt * np.array(v)
    n = 2 if square else 1
    t0 = np.arctan(2*np.pi*tau_period*n)/w
    sin = np.sin(2*np.pi*t/period)
    exp = np.exp(-(t-t0)/tau)
    amp = ampl/(np.sin(w*t0))**n
    f = amp * exp * sin**n
    t = np.append(t, t[-1] + dt)
    f = np.append(f, 0.0)
    f *= ampl/max(f)  # makes sure max point is 'ampl'
    return t, f


def ps_set_sp(pv, value):
    """."""
    pv.value = value
    pass


def ps_ramp_down(psname, pv):
    """."""
    time_step = 0.5  # [s]
    max_speed = 10.0  # [A/s]

    value = pv.value
    if value is None:
        print('{:<16s} disconnected.'.format(pv.pvname))
        sys.exit(-1)
    total_time = value/max_speed
    nrpts = int(total_time/time_step)
    fv = np.linspace(1.0, 0, nrpts)
    print('{:<16s} ramping down with {} points...'.format(psname, nrpts))
    for i in range(len(fv)):
        new_value = value * fv[i]
        print('{:<16s} RD {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
              new_value, i+1, nrpts))
        ps_set_sp(pv, new_value)
        time.sleep(time_step)
    print('{:<16s} ramp down finished.'.format(psname))


def ps_cycle(psname, plot=True):
    """."""
    t, w = gen_waveform(*parms[psname])
    if plot:
        dt = np.diff(t)
        dw = np.diff(w)
        print('{}: {:.02f} minutes, max {:.1f} A/s'.format(
            psname, max(t)/60.0, max(dw/dt)))
        plt.plot(t, w, 'o')
        plt.xlabel('time [s]')
        plt.ylabel('Current [A]')
        plt.title(psname)
        plt.show()
    else:
        pv_sp = epics.PV(psname + ':Current-SP')
        ps_ramp_down(psname, pv_sp)
        print('{:<16s} cycling with {} points...'.format(psname, len(t)))
        for i in range(0, len(t)-1):
            print('{:<16s} CY {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
                  w[i], i+1, len(w)))
            ps_set_sp(pv_sp, w[i])
            time.sleep(t[i+1]-t[i])
        print('{:<16s} CY {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
              w[i], i+1, len(w)))
        pv_sp.value = w[-1]
        print('{:<16s} cycling finished.'.format(psname))


def cycle_all(psnames):
    """."""
    threads = []
    for psname in psnames:
        process = Process(target=ps_cycle, args=(psname, False))
        process.start()
        threads.append(process)
    for process in threads:
        process.join()


def select_psnames(psgroup):
    """."""
    psnames = []
    allps = list(parms.keys())
    if psgroup.lower() == 'all':
        psnames += allps
    elif psgroup in allps:
        psnames.append(psgroup)
    elif psgroup.lower() == 'tb-dipole' or psgroup.lower() == 'tb-dipoles':
        for ps in allps:
            if 'TB-Fam' in ps and 'PS-B' in ps:
                psnames.append(ps)
    elif psgroup.lower() == 'tb-correctors':
        for ps in allps:
            if 'TB' in ps and ('PS-CH' in ps or 'PS-CV' in ps):
                psnames.append(ps)
    elif psgroup.lower() == 'tb-quadrupoles':
        for ps in allps:
            if 'TB' in ps and ('PS-QF' in ps or 'PS-QD' in ps):
                psnames.append(ps)
    elif psgroup.lower() == 'tb':
        for ps in allps:
            if ps.startswith('TB-'):
                psnames.append(ps)
    elif psgroup.lower() == 'bo-dipoles':
        for ps in allps:
            if 'BO-Fam' in ps and 'PS-B' in ps:
                psnames.append(ps)
    elif psgroup.lower() == 'bo-quadrupoles':
        for ps in allps:
            if 'BO-' in ps and \
               ('PS-QF' in ps or 'PS-QD' in ps or 'PS-QS' in ps):
                psnames.append(ps)
    elif psgroup.lower() == 'bo-sextupoles':
        for ps in allps:
            if 'BO-Fam' in ps and ('PS-SF' in ps or 'PS-SD' in ps):
                psnames.append(ps)
    elif psgroup.lower() == 'bo-correctors':
        for ps in allps:
            if 'BO-' in ps and \
               ('PS-CH' in ps or 'PS-CV' in ps or 'PS-QS' in ps):
                psnames.append(ps)
    elif psgroup.lower() == 'bo':
        for ps in allps:
            if ps.startswith('BO-'):
                psnames.append(ps)
    else:
        print('Invalid ps group {}!'.format(psgroup))
    return list(set(psnames))


def print_help():
    """."""
    print("NAME")
    print("       sirius-script-app-demag.py - Demagnetize magnets")
    print("")
    print("SINOPSIS")
    print("       sirius-script-app-demag.py [--help] [--plot] [all] [OTHERS]...")
    print("")
    print("DESCRIPTION")
    print("       Script used to demagnetize magnets with power supplies in in SlowRef mode")
    print("")
    print("       --help          print this help")
    print("")
    print("       --plot          plot demag curves")
    print("")
    print("       all             demag all magnets")
    print("")
    print("       tb-dipoles      demag TB dipoles")
    print("")
    print("       tb-quadrupoles  demag TB quadrupoles")
    print("")
    print("       tb-correctors   demag TB correctors")
    print("")
    print("       tb              demag TB magnets")
    print("")
    print("       bo-dipoles      demag BO dipoles")
    print("")
    print("       bo-quadrupoles  demag BO quadrupoles")
    print("")
    print("       bo-sextupoles  demag BO sextupoles")
    print("")
    print("       bo-correctors   demag BO correctors")
    print("")
    print("       BO-Fam:PS-QF    demag BO QF quadrupoles")
    print("")
    print("       bo              demag BO magnets")
    print("")
    print("       <POWER-SUPPLY>  demag magnets excitated by <POWER-SUPPLY>")
    print("")
    print("       and so on...")
    print("")
    print("AUTHOR")
    print("       Written by X. Resende, FACS-LNLS.")


def process_argv():
    """."""
    plot = False
    argv = [v for v in sys.argv[1:]]
    if '--help' in argv:
        print_help()
        sys.exit(0)
    if '--plot' in argv:
        plot = True
        argv.remove('--plot')
    psnames = []
    for arg in argv:
        psnames += select_psnames(arg)
    psnames = sorted(list(set(psnames)))
    return psnames, plot


def run():
    """."""
    psnames, plot_flag = process_argv()
    if plot_flag:
        print('Plotting cycling waveforms for {} power supplies:'.format(
            len(psnames)))
    else:
        print('Cycling magnets with {} power supplies:'.format(len(psnames)))
    for ps in psnames:
        print(ps)
    if plot_flag:
        for ps in psnames:
            ps_cycle(ps, plot=True)
    else:
        cycle_all(psnames)
        pass


if __name__ == "__main__":
    run()
