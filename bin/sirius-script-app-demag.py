#!/usr/bin/env python-sirius
"""."""

import sys
import time
import signal
from threading import Thread

# The original code was using multiprocessing instead of threading.
# It was buggy when an epics PV in global scope was created!
from multiprocessing import Process  # BUGGY with epics PVs!!!


import epics
import numpy as np
import matplotlib.pyplot as plt
from siriuspy import util


stop_event = False


def _stop_now(signum, frame):
    global stop_event
    print(signal.Signals(signum).name + ' received at ' +
          util.get_timestamp())
    sys.stdout.flush()
    sys.stderr.flush()
    stop_event = True

# obs:
# In order for the waveform to end at zero current, as it is desirable,
# please choose period as multiple of time step dt;


NEW_LI_NAMES = True


PSConvDict = {
    'LA-CN:H1RCPS-1': 'LI-01:PS-LensRev',
    'LA-CN:H1MLPS-1': 'LI-01:PS-Lens-1',
    'LA-CN:H1MLPS-2': 'LI-01:PS-Lens-2',
    'LA-CN:H1MLPS-3': 'LI-01:PS-Lens-3',
    'LA-CN:H1MLPS-4': 'LI-01:PS-Lens-4',
    'LA-CN:H1SLPS-1': 'LI-01:PS-Slnd-1',
    'LA-CN:H1SLPS-2': 'LI-01:PS-Slnd-2',
    'LA-CN:H1SLPS-3': 'LI-01:PS-Slnd-3',
    'LA-CN:H1SLPS-4': 'LI-01:PS-Slnd-4',
    'LA-CN:H1SLPS-5': 'LI-01:PS-Slnd-5',
    'LA-CN:H1SLPS-6': 'LI-01:PS-Slnd-6',
    'LA-CN:H1SLPS-7': 'LI-01:PS-Slnd-7',
    'LA-CN:H1SLPS-8': 'LI-01:PS-Slnd-8',
    'LA-CN:H1SLPS-9': 'LI-01:PS-Slnd-9',
    'LA-CN:H1SLPS-10': 'LI-01:PS-Slnd-10',
    'LA-CN:H1SLPS-11': 'LI-01:PS-Slnd-11',
    'LA-CN:H1SLPS-12': 'LI-01:PS-Slnd-12',
    'LA-CN:H1SLPS-13': 'LI-01:PS-Slnd-13',
    'LA-CN:H1SLPS-14': 'LI-Fam:PS-Slnd-14',
    'LA-CN:H1SLPS-15': 'LI-Fam:PS-Slnd-15',
    'LA-CN:H1SLPS-16': 'LI-Fam:PS-Slnd-16',
    'LA-CN:H1SLPS-17': 'LI-Fam:PS-Slnd-17',
    'LA-CN:H1SLPS-18': 'LI-Fam:PS-Slnd-18',
    'LA-CN:H1SLPS-19': 'LI-Fam:PS-Slnd-19',
    'LA-CN:H1SLPS-20': 'LI-Fam:PS-Slnd-20',
    'LA-CN:H1SLPS-21': 'LI-Fam:PS-Slnd-21',
    'LA-CN:H1SCPS-1': 'LI-01:PS-CV-1',
    'LA-CN:H1SCPS-2': 'LI-01:PS-CH-1',
    'LA-CN:H1SCPS-3': 'LI-01:PS-CV-2',
    'LA-CN:H1SCPS-4': 'LI-01:PS-CH-2',
    'LA-CN:H1LCPS-1': 'LI-01:PS-CV-3',
    'LA-CN:H1LCPS-2': 'LI-01:PS-CH-3',
    'LA-CN:H1LCPS-3': 'LI-01:PS-CV-4',
    'LA-CN:H1LCPS-4': 'LI-01:PS-CH-4',
    'LA-CN:H1LCPS-5': 'LI-01:PS-CV-5',
    'LA-CN:H1LCPS-6': 'LI-01:PS-CH-5',
    'LA-CN:H1LCPS-7': 'LI-01:PS-CV-6',
    'LA-CN:H1LCPS-8': 'LI-01:PS-CH-6',
    'LA-CN:H1LCPS-9': 'LI-01:PS-CV-7',
    'LA-CN:H1LCPS-10': 'LI-01:PS-CH-7',
    'LA-CN:H1FQPS-1': 'LI-Fam:PS-QF1',
    'LA-CN:H1FQPS-2': 'LI-Fam:PS-QF2',
    'LA-CN:H1FQPS-3': 'LI-01:PS-QF3',
    'LA-CN:H1DQPS-1': 'LI-01:PS-QD1',
    'LA-CN:H1DQPS-2': 'LI-01:PS-QD2',
    'LA-CN:H1DPPS-1': 'LI-01:PS-Spect'}

parms = {
    # psname           dt[s], max_amp[A], period[s], nr_cycles, tau[s], sin**2

    # --- TB ---

    'TB-Fam:PS-B':     [0.5, 300, 4, 32, 16, True],

    'TB-01:PS-QD1':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-01:PS-QF1':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-QD2A':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-QF2A':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-QD2B':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-QF2B':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-03:PS-QD3':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-03:PS-QF3':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-04:PS-QD4':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-04:PS-QF4':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-01:PS-CH-1':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-01:PS-CV-1':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-01:PS-CH-2':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-01:PS-CV-2':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-CH-1':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-CV-1':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-CH-2':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-02:PS-CV-2':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-04:PS-CH':     [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-04:PS-CV-1':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'TB-04:PS-CV-2':   [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]

    # --- LI ---

    # SPECTROMETER
    'LI-01:PS-Spect':  [0.5, 6.0, 24, 8, 48, False],

    # QUADRUPOLES
    'LI-01:PS-QD1':   [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-QD2':   [0.5, 5, 24, 8, 48, False],
    'LI-Fam:PS-QF1':  [0.5, 5, 24, 8, 48, False],
    'LI-Fam:PS-QF2':  [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-QF3':  [0.5, 5, 24, 8, 48, False],

    # LONG CORRECTORS
    'LI-01:PS-CV-3': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-3': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-4': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-4': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-5': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-5': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-6': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-6': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CV-7': [0.5, 1.5, 24, 8, 48, False],
    'LI-01:PS-CH-7': [0.5, 1.5, 24, 8, 48, False],

    # LENSES
    'LI-01:PS-Lens-1':  [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-2':  [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-3':  [0.5, 5, 24, 8, 48, False],
    'LI-01:PS-Lens-4':  [0.5, 5, 24, 8, 48, False],

    # REVERSE LENS
    'LI-01:PS-LensRev':  [0.5, 5, 24, 8, 48, False],

    # SHORT CORRECTORS
    'LI-01:PS-CV-1':  [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CH-1':  [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CV-2':  [0.5, 0.25, 24, 8, 48, False],
    'LI-01:PS-CH-2':  [0.5, 0.25, 24, 8, 48, False],

    # SOLENOIDS
    'LI-01:PS-Slnd-1':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-2':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-3':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-4':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-5':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-6':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-7':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-8':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-9':   [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-10':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-11':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-12':  [0.5, 35, 38, 5, 57, True],
    'LI-01:PS-Slnd-13':  [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-14': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-15': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-16': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-17': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-18': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-19': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-20': [0.5, 35, 38, 5, 57, True],
    'LI-Fam:PS-Slnd-21': [0.5, 35, 38, 5, 57, True],

    # --- BO ---

    'BO-Fam:PS-B-1':   [0.5, 60,  46, 6,  69, False],  # 24 [A/s]
    'BO-Fam:PS-B-2':   [0.5, 60,  46, 6,  69, False],  # 24 [A/s]
    'BO-Fam:PS-QF':    [0.5, 120, 24, 10, 48, False],  # 34.8 [A/s]
    'BO-Fam:PS-QD':    [0.5, 30,  24, 10, 48, False],  # 8.8 [A/s]
    'BO-Fam:PS-SF':    [0.5, 150, 24, 10, 48, False],  # 43.5 [A/s]
    'BO-Fam:PS-SD':    [0.5, 150, 24, 10, 48, False],  # 43.5 [A/s]

    'BO-02D:PS-QS':    [0.5, 10,  24, 10, 48, False],  # 2.9 [A/s]

    'BO-01U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-03U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-05U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-07U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-09U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-11U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-13U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-15U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-17U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-19U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-21U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-23U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-25U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-27U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-29U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-31U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-33U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-35U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-37U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-39U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-41U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-43U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-45U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-47U:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-49D:PS-CH':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]

    'BO-01U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-03U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-05U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-07U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-09U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-11U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-13U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-15U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-17U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-19U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-21U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-23U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-25U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-27U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-29U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-31U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-33U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-35U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-37U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-39U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-41U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-43U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-45U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-47U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]
    'BO-49U:PS-CV':    [0.5, 10, 24, 10, 48, False],  # 2.9 [A/s]

}


def conv_li_psnames():
    """."""
    global parms
    for oname, nname in PSConvDict.items():
        data = parms[oname]
        parms[nname] = data
        del parms[oname]


def gen_waveform(dt, ampl, period, nr_periods, tau, square):
    """."""
    w = 2*np.pi/period
    nrpts = nr_periods * int(period / dt)
    v = list(range(0, nrpts))
    t = dt * np.array(v)
    n = 2 if square else 1
    t0 = np.arctan(2*np.pi*tau*n)/w
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


def create_pv_sp(psname):
    """."""
    if psname.startswith('LI-'):
        pv_sp = epics.PV(psname + ':seti')
    else:
        pv_sp = epics.PV(psname + ':Current-SP')
    return pv_sp


def check_egun_enabled():
    """."""
    pv = epics.PV('LI-01:EG-TriggerPS:enable')
    value = pv.get()
    return value


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
    elif psgroup.lower() in ('li-dipole', 'li-spectrometer'):
        for ps in allps:
            if ps.startswith('LI-01:PS-Spect'):
                psnames.append(ps)
    elif psgroup.lower() in ('li-quadrupoles', ):
        for ps in allps:
            if ps.startswith('LI-'):
                if 'QD' in ps or 'QF' in ps:
                    psnames.append(ps)
    elif psgroup.lower() in ('li-long-correctors', ):
        for ps in allps:
            if ps.startswith('LI-'):
                if 'CH' in ps or 'CV' in ps:
                    if '-1' not in ps and '-2' not in ps:
                        psnames.append(ps)
    elif psgroup.lower() in ('li-magnetic-lenses', ):
        for ps in allps:
            if 'Lens-' in ps:
                psnames.append(ps)
    elif psgroup.lower() in ('li-short-correctors', ):
        for ps in allps:
            if ps.startswith('LI-'):
                if 'CH' in ps or 'CV' in ps:
                    if '-1' in ps or '-2' in ps:
                        psnames.append(ps)
    elif psgroup.lower() in ('li-solenoids', ):
        for ps in allps:
            if 'Slnd' in ps:
                psnames.append(ps)
    elif psgroup.lower() == 'li':
        for ps in allps:
            if ps.startswith('LI-'):
                psnames.append(ps)
    elif psgroup.lower() == 'default':
        for ps in allps:
            if ps.startswith('LI-') or ps == 'TB-Fam:PS-B':
                psnames.append(ps)
    else:
        print('Invalid ps group {}!'.format(psgroup))
    return list(set(psnames))


def ps_list(psname):
    """."""
    t, w = gen_waveform(*parms[psname])
    dt = np.diff(t)
    dw = np.diff(w)
    print('{:<20s}: {:.02f} minutes, max {:.1f} A/s'.format(
        psname, max(t)/60.0, max(abs(dw/dt))))

    # plt.plot(dw/dt)
    # plt.show()


def ps_plot(psname):
    """."""
    t, w = gen_waveform(*parms[psname])
    plt.ion()
    fig = plt.figure()
    plt.plot(t, w, '-b')
    plt.plot(t, w, '.b')
    plt.xlabel('time [s]')
    plt.ylabel('Current [A]')
    plt.title(psname)
    while not stop_event:
        try:
            fig.canvas.flush_events()
        except:
            break
        time.sleep(0.20)


def ps_rampdown(psname):
    """."""
    time_step = 0.5  # [s]
    max_speed = 10.0  # [A/s]

    pv = create_pv_sp(psname)
    value = pv.value
    if value is None:
        print('{:<20s} disconnected.'.format(pv.pvname))
        sys.exit(-1)
    value = abs(value)
    total_time = value/max_speed
    nrpts = int(total_time/time_step)
    fv = np.linspace(1.0, 0, nrpts)
    print('{:<20s} ramping down with {} points...'.format(psname, nrpts))
    for i in range(len(fv)):
        new_value = value * fv[i]
        print('{:<20s} RD {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
              new_value, i+1, nrpts))
        ps_set_sp(pv, new_value)
        time.sleep(time_step)
    print('{:<20s} ramp down finished.'.format(psname))


def ps_cycle(psname):
    """."""
    if psname == 'LI-01:PS-Spect':
        if check_egun_enabled():
            print('Linac EGun pulse is enabled! Please disable it.')
            return
    t, w = gen_waveform(*parms[psname])
    ps_rampdown(psname)
    pv_sp = create_pv_sp(psname)
    print('{:<20s} cycling with {} points...'.format(psname, len(t)))
    for i in range(0, len(t)-1):
        print('{:<20s} CY {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
              w[i], i+1, len(w)))
        ps_set_sp(pv_sp, w[i])
        time.sleep(t[i+1]-t[i])
        if stop_event:
            print('Force stop cycling for {}...'.format(psname))
            return False
    print('{:<20s} CY {:+010.4f} A  ({:03d}/{:03d})'.format(psname,
          w[i], i+1, len(w)))
    pv_sp.value = w[-1]
    print('{:<20s} cycling finished.'.format(psname))
    return True


def exec_all(psnames, target):
    """."""
    if target == ps_cycle and 'LI-01:PS-Spect' in psnames:
        LocalThread = Thread
        if check_egun_enabled():
            print('Linac EGun pulse is enabled! Please disable it.')
            return
    elif target == ps_rampdown:
        LocalThread = Thread
    else:
        LocalThread = Process
    threads = []
    for psname in psnames:
        process = LocalThread(target=target, args=(psname,))
        process.start()
        threads.append(process)
    for process in threads:
        process.join()


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
    print("       --help               print this help")
    print("")
    print("       --list               list power supplies")
    print("")
    print("       --plot               plot demag curves")
    print("")
    print("       --rampdown           ramp selected power supplies down to zero current")
    print("")
    print("       all                  demag all magnets")
    print("")
    print("       default              demag LI magnets and TB dipoles")
    print("")
    print("       tb-dipoles           demag TB dipoles")
    print("")
    print("       tb-quadrupoles       demag TB quadrupoles")
    print("")
    print("       tb-correctors        demag TB correctors")
    print("")
    print("       tb                   demag TB magnets")
    print("")
    print("       bo-dipoles           demag BO dipoles")
    print("")
    print("       bo-quadrupoles       demag BO quadrupoles")
    print("")
    print("       bo-sextupoles        demag BO sextupoles")
    print("")
    print("       bo-correctors        demag BO correctors")
    print("")
    print("       bo                   demag BO magnets")
    print("")
    print("       li-dipole            demag LI dipole or spectrometer")
    print("")
    print("       li-spectrometer      demag LI dipole or spectrometer")
    print("")
    print("       li-quadrupoles       demag LI quadrupoles")
    print("")
    print("       li-short-correctors  demag LI short correctors")
    print("")
    print("       li-long-correctors   demag LI long correctors")
    print("")
    print("       li-solenoids         demag LI solenoids")
    print("")
    print("       li                   demag LI magnets")
    print("")
    print("       <POWER-SUPPLY>  demag magnets excitated by <POWER-SUPPLY>")
    print("")
    print("       and so on...")
    print("")
    print("AUTHOR")
    print("       FACS-LNLS.")


def process_argv():
    """."""
    plot_flag, list_flag, rmpdown_flag = False, False, False
    argv = [v for v in sys.argv[1:]]
    if '--help' in argv:
        print_help()
        sys.exit(0)
    if '--plot' in argv:
        plot_flag = True
        argv.remove('--plot')
    if '--list' in argv:
        list_flag = True
        argv.remove('--list')
    if '--rampdown' in argv:
        rmpdown_flag = True
        argv.remove('--rampdown')

    psnames = []
    for arg in argv:
        psnames += select_psnames(arg)
    psnames = sorted(list(set(psnames)))
    return psnames, plot_flag, list_flag, rmpdown_flag


def run():
    """."""
    # convert li psnames from old to new
    if NEW_LI_NAMES:
        conv_li_psnames()

    psnames, plot_flag, list_flag, rmpdown_flag = process_argv()

    # Define abort function
    signal.signal(signal.SIGINT, _stop_now)
    signal.signal(signal.SIGTERM, _stop_now)

    if list_flag:
        print('Selecting {} power supplies:'.format(len(psnames)))
        exec_all(psnames, ps_list)
    elif plot_flag:
        print('Plotting cycling waveforms for {} power supplies:'.format(
            len(psnames)))
        exec_all(psnames, ps_plot)
    elif rmpdown_flag:
        print('Ramping down {} power supplies:'.format(len(psnames)))
        exec_all(psnames, ps_rampdown)
    else:
        print('Cycling magnets with {} power supplies:'.format(len(psnames)))
        exec_all(psnames, ps_cycle)


if __name__ == "__main__":
    run()
