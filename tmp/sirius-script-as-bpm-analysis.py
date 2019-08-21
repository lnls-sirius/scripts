#!/usr/bin/env python-sirius

import numpy as np
import scipy.io as scio
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from siriuspy.epics import PV
from siriuspy.csdevice.orbitcorr import SOFBFactory


def get_fft(val):
    fft = np.fft.rfft(val, axis=0)
    absfft = np.abs(fft)
    freq = np.linspace(0, 0.5, absfft.shape[0])
    d =  absfft.shape[1]//10
    return absfft[d:-d], freq[d:-d]


def update_colors(ax):
    lines = ax.lines
    colors = cm.winter(np.linspace(0, 1, len(lines)))
    for c, l in zip(colors, lines):
        l.set_color(c)


if __name__ == '__main__':

    csorb = SOFBFactory.create('bo')
    spos = np.array(csorb.BPM_POS)
    nrb = spos.size

    # bpmsx = [PV(bpm + ':GEN_XArrayData') for bpm in csorb.BPM_NAMES]
    # bpmsy = [PV(bpm + ':GEN_YArrayData') for bpm in csorb.BPM_NAMES]
    # bpmss = [PV(bpm + ':GEN_YArrayData') for bpm in csorb.BPM_NAMES]

    pv_posx = PV('BO-Glob:AP-SOFB:MTurnOrbX-Mon')
    pv_posy = PV('BO-Glob:AP-SOFB:MTurnOrbY-Mon')
    pv_poss = PV('BO-Glob:AP-SOFB:MTurnOrbSum-Mon')

    # posx = pv_posx.get().reshape(-1, nrb) / 1e6
    # posy = pv_posy.get().reshape(-1, nrb) / 1e6
    # poss = pv_posy.get().reshape(-1, nrb)
    wave = scio.loadmat(
        '/home/fernando/Downloads/' +
        'data_boo_2019-05-07_tbt_several_injections.mat')
    wave = wave['wvfs']
    posx = np.mean(wave[:150, 0::3], axis=2)/1e3
    posy = np.mean(wave[:150, 1::3], axis=2)/1e3
    poss = np.mean(wave[:150, 2::3], axis=2)/2**28
    fftx, freqx = get_fft(posx)
    ffty, freqy = get_fft(posy)

    offsets = np.arange(nrb)[None, :] * 1
    posx += np.max(posx) * offsets * 0.1
    posy += np.max(posy) * offsets * 0.1
    poss += np.max(poss) * offsets * 0
    fftx += np.max(fftx) * offsets * 1
    ffty += np.max(ffty) * offsets * 1

    f = plt.figure(figsize=(11, 8))
    gs = gridspec.GridSpec(3, 2)
    gs.update(
        top=0.98, bottom=0.06, left=0.10, right=0.98,
        hspace=0.3, wspace=0.25)
    axposs = plt.subplot(gs[0, :])
    axposx = plt.subplot(gs[1, 0])
    axposy = plt.subplot(gs[1, 1])
    axfftx = plt.subplot(gs[2, 0])
    axffty = plt.subplot(gs[2, 1])

    axposx.set_ylabel('Pos X [um]')
    axposy.set_ylabel('Pos Y [um]')
    axposs.set_ylabel('Sum [a.u.]')
    axposx.set_xlabel('Turn Number')
    axposy.set_xlabel('Turn Number')
    axposs.set_xlabel('Turn Number')
    axfftx.set_ylabel('abs(FFT) X [a.u.]')
    axffty.set_ylabel('abs(FFT) Y [a.u.]')
    axfftx.set_xlabel('tune')
    axffty.set_xlabel('tune')
    axposx.plot(posx)
    axposy.plot(posy)
    axposs.plot(poss)
    axfftx.plot(freqx, fftx)
    axffty.plot(freqy, ffty)
    update_colors(axposx)
    update_colors(axposy)
    update_colors(axfftx)
    update_colors(axffty)
    plt.show()
