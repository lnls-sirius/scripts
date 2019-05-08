#!/usr/bin/env python-sirius

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from siriuspy.epics import PV
from siriuspy.csdevice.orbitcorr import SOFBFactory


def get_fft(val):
    fft = np.fft.rfft(val, axis=0)
    absfft = np.abs(fft)
    absfft += np.max(absfft) * np.linspace(0, 1, absfft.shape[1])[None, :]
    freq = np.linspace(0, 0.5, absfft.shape[0])
    return absfft, freq


def default_cm(ncolors):
    return cm.brg(np.linspace(0, 1, ncolors+1))


if __name__ == '__main__':

    csorb = SOFBFactory.create('bo')
    spos = np.array(csorb.BPM_POS)

    # bpmsx = [PV(bpm + ':GEN_XArrayData') for bpm in csorb.BPM_NAMES]
    # bpmsy = [PV(bpm + ':GEN_YArrayData') for bpm in csorb.BPM_NAMES]
    # bpmss = [PV(bpm + ':GEN_YArrayData') for bpm in csorb.BPM_NAMES]

    pv_posx = PV('BO-Glob:AP-SOFB:MTurnOrbX-Mon')
    pv_posy = PV('BO-Glob:AP-SOFB:MTurnOrbY-Mon')
    pv_poss = PV('BO-Glob:AP-SOFB:MTurnOrbSum-Mon')

    posx = pv_posx.get().reshape(-1, 50) / 1e6
    absfftx, freqx = get_fft(posx)
    posy = pv_posy.get().reshape(-1, 50) / 1e6
    absffty, freqy = get_fft(posy)

    colors = default_cm(spos.shape[0])
    f = plt.figure(figsize=(11, 5))
    gs = gridspec.GridSpec(2, 2)
    gs.update(top=0.95, left=0.10, right=0.98, hspace=0.3, wspace=0.25)
    axposx = plt.subplot(gs[0, 0])
    axposy = plt.subplot(gs[1, 0], sharex=axposx)
    axfftx = plt.subplot(gs[0, 1])
    axffty = plt.subplot(gs[1, 1], sharex=axfftx)

    axposx.set_ylabel('Pos X [um]')
    axposy.set_ylabel('Pos Y [um]')
    axposx.set_xlabel('Turn Number')
    axposy.set_xlabel('Turn Number')
    axfftx.set_ylabel('abs(FFT) X [a.u.]')
    axffty.set_ylabel('abs(FFT) Y [a.u.]')
    axfftx.set_xlabel('tune')
    axffty.set_xlabel('tune')
    axposx.plot(posx)
    axposy.plot(posy)
    axfftx.plot(freqx, absfftx)
    axffty.plot(freqy, absffty)
    plt.show()
