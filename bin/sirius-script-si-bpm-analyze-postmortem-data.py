#!/usr/bin/env python-sirius
"""."""

import argparse
import os
import subprocess
from pathlib import Path

import numpy as np
from apsuite.commisslib.meas_bpms_signals import AcqBPMsSignals
from matplotlib import pyplot as plt
from siriuspy.clientarch import Time
from siriuspy.devices import SOFB


def acquire_data():
    """."""
    acq = AcqBPMsSignals(ispost_mortem=True)
    acq.wait_for_connection()
    acq.data = acq.get_data()

    return acq, acq.data


def prepare_output_dir(data, folder=None):
    """."""
    timestamp = Time(data['timestamp'])

    day = timestamp.strftime('%Y-%m-%d')
    stamp = timestamp.strftime('%Y-%m-%d-%Hh%Mm%Ss')

    if folder is None:
        base = Path.home() / 'shared' / 'screens-iocs' / 'data_by_day'

        if not base.exists() or not os.access(base, os.W_OK):
            base = Path.home()
    else:
        base = Path(folder).expanduser()

    outdir = base / f'{day}-SI_postmortem_data'
    outdir.mkdir(parents=True, exist_ok=True)

    return outdir, stamp


def compute_orbit_distortion(data):
    """."""
    x = data['orbx']
    y = data['orby']

    nsamples = min(len(x) // 2, x.shape[0])

    # orbit distortion (along BPMs)
    orbx_dist = x[:100].mean(axis=0) - x[nsamples - 100 : nsamples].mean(
        axis=0
    )
    orby_dist = y[:100].mean(axis=0) - y[nsamples - 100 : nsamples].mean(
        axis=0
    )

    # orbit distortion (along time)
    orbx_drift = x - x[:100].mean(axis=0)
    orby_drift = y - y[:100].mean(axis=0)

    tim = (-(np.arange(nsamples) / data['sampling_frequency'] * 1e3))[::-1]

    return orbx_dist, orby_dist, orbx_drift, orby_drift, tim, nsamples


def compute_correctors(sofb, orbx_dist, orby_dist):
    """."""
    corrs = sofb.invrespmat @ np.hstack([orbx_dist, orby_dist])

    chs = corrs[:120]
    cvs = corrs[120:280]

    outch = np.abs(chs) > 2 * chs.std()
    outcv = np.abs(cvs) > 2 * cvs.std()

    return chs, cvs, outch, outcv


def plot_results(
    sofb,
    stamp,
    orbx_dist,
    orby_dist,
    orbx_drift,
    orby_drift,
    tim,
    nsamples,
    chs,
    cvs,
    outch,
    outcv,
):
    """."""
    bpms_names = np.asarray(sofb.data.bpm_names)
    ch_names = np.asarray(sofb.data.ch_names)
    cv_names = np.asarray(sofb.data.cv_names)

    idcsx = np.argsort(np.abs(orbx_dist))
    idcsy = np.argsort(np.abs(orby_dist))

    fig, axs = plt.subplots(
        3,
        2,
        figsize=(14, 14),
    )

    # orbit distortion
    axs[0, 0].plot(orbx_dist)
    axs[0, 0].set_title('horizontal orbit distortion')
    axs[0, 0].set_xlabel('bpms index')
    axs[0, 0].set_ylabel('orbit distortion [um]')

    axs[0, 1].plot(orby_dist)
    axs[0, 1].set_title('vertical orbit distortion')
    axs[0, 1].set_xlabel('bpms index')

    # bpms time drift for bpms w/ largest distortions
    for k, alpha in zip(range(1, 6), [1, 0.8, 0.6, 0.4, 0.2]):
        idx = idcsx[-k]
        axs[1, 0].plot(
            tim,
            orbx_drift[:nsamples, idx],
            alpha=alpha,
            label=bpms_names[idx],
        )
    axs[1, 0].set_title('horizontal orbit drift (largest BPMs drifts only)')
    axs[1, 0].set_xlabel('time [ms]')
    axs[1, 0].set_ylabel('orbit drift [um]')
    axs[1, 0].legend()

    for k, alpha in zip(range(1, 6), [1, 0.8, 0.6, 0.4, 0.2]):
        idx = idcsy[-k]
        axs[1, 1].plot(
            tim,
            orby_drift[:nsamples, idx],
            alpha=alpha,
            label=bpms_names[idx],
        )

    axs[1, 1].legend()
    axs[1, 1].set_title('vertical orbit drift (largest BPMs drifts only)')
    axs[1, 1].set_xlabel('time [ms]')

    # horizontal correctors
    axs[2, 0].plot(chs)

    idx = np.where(outch)[0]

    axs[2, 0].plot(idx, chs[idx], 'o', color='red', mfc='none')

    for i in idx:
        axs[2, 0].annotate(
            ch_names[i],
            (i, chs[i]),
            xytext=(3, 3),
            textcoords='offset points',
            fontsize=8,
            color='red',
        )
    axs[2, 0].set_ylabel('corrector strengths [urad]')
    axs[2, 0].set_title(
        'horizontal correctors strengths explaining the distortions'
    )
    axs[2, 0].set_xlabel('CH index')

    # vertical correctors
    axs[2, 1].plot(cvs)

    idx = np.where(outcv)[0]

    axs[2, 1].plot(idx, cvs[idx], 'o', color='red', mfc='none')

    for i in idx:
        axs[2, 1].annotate(
            cv_names[i],
            (i, cvs[i]),
            xytext=(3, 3),
            textcoords='offset points',
            fontsize=8,
            color='red',
        )
    axs[2, 1].set_title(
        'vertical correctors strengths explaining the distortions'
    )
    axs[2, 1].set_xlabel('CV index')

    plt.suptitle('SI BPMs pos-mortem analysis\n{}'.format(stamp))

    return fig


def save_and_show(fig, outdir):
    """."""
    filename = outdir / 'postmortem_analysis.png'

    fig.savefig(
        filename,
        dpi=300,
        bbox_inches='tight',
    )
    print(f'Post-mortem analysis figure saved to {filename}.')

    try:
        subprocess.Popen(['xdg-open', str(filename)])
    except Exception as e:
        print(f'Failed to open image: {e}')


def main():
    """."""
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-f',
        '--folder',
        default=None,
        help=(
            'Base folder where the output directory will be created. '
            'Defaults to ~/shared/screens-iocs/data_by_day. '
            'If unavailable or w/o writing permissions, falls back to $HOME.'
        ),
    )

    args = parser.parse_args()

    acq, data = acquire_data()

    outdir, stamp = prepare_output_dir(
        data,
        folder=args.folder,
    )

    acq.save_data(str(outdir / f'postmortem_data_{stamp}.pickle'))

    sofb = SOFB(SOFB.DEVICES.SI)

    (
        orbx_dist,
        orby_dist,
        orbx_drift,
        orby_drift,
        tim,
        nsamples,
    ) = compute_orbit_distortion(data)

    (
        chs,
        cvs,
        outch,
        outcv,
    ) = compute_correctors(sofb, orbx_dist, orby_dist)

    fig = plot_results(
        sofb,
        stamp,
        orbx_dist,
        orby_dist,
        orbx_drift,
        orby_drift,
        tim,
        nsamples,
        chs,
        cvs,
        outch,
        outcv,
    )

    save_and_show(fig, outdir)


if __name__ == '__main__':
    main()
