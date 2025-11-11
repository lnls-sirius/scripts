#!/usr/bin/env python-sirius
"""Script for analyzing BBA measurements."""

from datetime import datetime
import matplotlib.pyplot as mplt
import matplotlib.cm as mcmap
import matplotlib.patches as mpatch

from matplotlib import rcParams
import numpy as np
from siriuspy.clientconfigdb import ConfigDBClient
from siriuspy.sofb.csdev import SOFBFactory
from apsuite.commisslib.measure_bba import DoBBA

rcParams.update(
    {
        "font.size": 18,
        "lines.linewidth": 2,
        "axes.grid": True,
        "grid.alpha": 0.5,
        "grid.linestyle": "--",
    }
)


def print_dobba(dobba):
    """."""
    for idx, bpmname in enumerate(dobba.measuredbpms):
        print(f"{idx:03d} {bpmname:<16s}  ", end="")
        if (idx + 1) % 3 == 0:
            print()


def plot_results(
    bba_orb_new,
    bba_orb_old,
    new_bba_orb_name,
    previous_bba_orb_name,
    cltorb,
    plot_diff=True,
):
    """."""
    if plot_diff:
        ox = np.array(bba_orb_new["x"]) - np.array(bba_orb_old["x"])
        oy = np.array(bba_orb_new["y"]) - np.array(bba_orb_old["y"])
    else:
        ox = np.array(bba_orb_new["x"])
        oy = np.array(bba_orb_new["y"])

    fig, ax = mplt.subplots(figsize=(9, 7))

    sofb = SOFBFactory.create("SI")
    sigx = ox.std()
    sigy = oy.std()
    nsig = 2
    bound_type = "rect"

    if bound_type == "ell":
        idcs = (
            (ox * ox / (nsig**2 * sigx * sigx) + oy * oy / (nsig**2 * sigy * sigy)) > 1
        ).nonzero()[0]
    else:
        idcs = (
            (np.abs(ox) / (nsig * sigx) > 1) | (np.abs(oy) / (nsig * sigy) > 1)
        ).nonzero()[0]

    cores = mcmap.jet(np.linspace(0, 1, idcs.size))

    ax.plot(ox, oy, "o")

    for i, idx in enumerate(idcs):
        ax.plot(
            ox[idx],
            oy[idx],
            "o",
            color=cores[i],
            label=sofb.bpm_nicknames[idx],
        )

    propts = dict(
        width=2 * sigx * nsig,
        height=2 * sigy * nsig,
        edgecolor="k",
        facecolor="none",
        linestyle="--",
        label=r"${0:.1f}\times\sigma$".format(nsig),
    )
    if bound_type == "ell":
        ell = mpatch.Ellipse((0, 0), **propts)
    else:
        ell = mpatch.Rectangle((-sigx * nsig, -sigy * nsig), **propts)

    ax.add_patch(ell)

    dtime_old = datetime.fromtimestamp(
        cltorb.get_config_info(previous_bba_orb_name)["created"]
    ).strftime("%d/%m/%Y")
    dtime_now = datetime.now().strftime("%d/%m/%Y")

    ax.set_ylabel("$\Delta y\, [\mu m]$")
    ax.set_xlabel("$\Delta x\, [\mu m]$")
    ax.legend(loc="center left", bbox_to_anchor=(1, 0.5), fontsize="xx-small")

    # ax.plot(ox[2*8-1:3*8-1], oy[2*8-1:3*8-1], 'kx')

    if plot_diff:
        ax.set_title(
            f"Diff. BBAs from {dtime_now:s} - {dtime_old:s}\n"
            r"$\sigma_x = {0:.1f},\,\, \sigma_y = {1:.1f}$".format(sigx, sigy)
        )

        fig.savefig(f"diff_to_{previous_bba_orb_name:s}.png")
    else:
        ax.set_title(
            f"BBA from {dtime_now:s}\n"
            r"$\sigma_x = {0:.1f},\,\, \sigma_y = {1:.1f}$".format(sigx, sigy)
        )
        fig.savefig(f"bba{new_bba_orb_name:s}.png")
    fig.tight_layout()
    fig.show()


def main():
    """."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(description="Analyze BBA meas. data.")

    parser.add_argument(
        "-f",
        "--filenames",
        nargs="+",
        help="Space-separated list of filenames for BBA measurement data. "
        "If more than one filename is given, BBA data is combined.",
    )

    parser.add_argument(
        "-m",
        "--method",
        default="linear",
        help="Process data method: 'linear' (bowtie plots) or "
        "quadratic (parabola plots). Defaults to 'linear'.",
    )

    parser.add_argument(
        "--process_data_mode",
        type=str,
        default="symm",
        help="Process data mode. Defaults to 'symm'.",
    )

    parser.add_argument(
        "-s",
        "--bpms-summary",
        action="store_true",
        help="Plot all the BPMs measurement summary (orbdists vs offset) "
        "Defaults to False, in which case summary will be shown only for bad "
        "measurement BPMs ",
    )

    parser.add_argument(
        "-c",
        "--compare_methods",
        action="store_true",
        help="Plot comparison linear and quadratic fitting methods. Defaults to False.",
    )

    parser.add_argument(
        "--maxstd",
        type=float,
        default=10.0,
        help="Threshold for data adequacy. Used to define BPMS to redo.",
    )

    parser.add_argument(
        "-p",
        "--previous_bba_orb_name",
        type=str,
        default="bba_orb",
        help="Name of previous BBA orb saved in servconf. Defaults to 'bba_orb'. ",
    )

    parser.add_argument(
        "-n",
        "--new_bba_orb_name",
        type=str,
        default="bba_orb",
        help="Name of new BBA orb to be saved in servconf. Defaults to 'bba_orb'. ",
    )

    parser.add_argument(
        "-i",
        "--insert_config",
        action="store_true",
        help="If given, insert new BBA orb to servconf with name '-new_bba_orb_name'.",
    )

    parser.add_argument(
        "-d--plot_diff",
        action="store_true",
        help="If given, plot BBA orb diff from previous BBA orb",
    )

    args = parser.parse_args()
    fnames = args.filenames
    mode = args.process_data_mode

    dobba_list = list()
    for fname in fnames:
        print(fname)
        dobba = DoBBA(isonline=False)
        dobba.load_and_apply(fname)
        print_dobba(dobba)
        dobba_list.append(dobba)
        print()
    dobba = DoBBA(isonline=False)
    dobba = dobba.combine_bbas(dobba_list)

    dobba.process_data(mode=mode)
    if args.bpms_summary:
        bpms = dobba.measuredbpms
        for bpm in bpms:
            dobba.make_figure_bpm_summary(bpm)

    if args.compare_methods:
        dobba.make_figure_compare_methods(plotdiff=False)

    # bpms_redo = dobba.filter_problems(maxstd=10, probtype='ext std')
    bpms_redo = dobba.filter_problems(
        maxstd=args.maxstd, probtype="ext std", method=args.method
    )

    for bpm in bpms_redo:
        dobba.make_figure_bpm_summary(bpm)

    print(f"Number of BPMS to redo: {len(bpms_redo)}")
    print("BPMS to redo:")
    for bpm in bpms_redo:
        print(f"\t{bpm}")

    bba_orbx, bba_orby = dobba.get_bba_results(method=args.method + "_fitting")
    idcs_bba = [dobba.data["bpmnames"].index(b) for b in dobba.measuredbpms]

    cltorb = ConfigDBClient(config_type="si_orbit")
    bba_orb_ref = cltorb.get_config_value(args.previous_bba_orb_name)
    bba_orb_new = bba_orb_ref.copy()
    for idx in idcs_bba:
        oldx, newx = bba_orb_ref["x"][idx], bba_orbx[idx]
        oldy, newy = bba_orb_ref["y"][idx], bba_orby[idx]

        bpmname = dobba.data["bpmnames"][idx]
        print("BBA Orb Comparison")
        print("BPM name BPM index orbx_old -> orbx_new | orby_old -> orby_new")
        print(
            f"{bpmname:<20s} {idx:03d} : {oldx:+07.2f} -> {newx:+07.2f} | {oldy:+07.2f} -> {newy:+07.2f}"
        )
        bba_orb_new["x"][idx] = float(bba_orbx[idx])
        bba_orb_new["y"][idx] = float(bba_orby[idx])

    if args.insert_config:
        cltorb.insert_config(args.new_bba_orb_name, bba_orb_new)

    plot_results(
        bba_orb_new,
        bba_orb_ref,
        args.new_bba_orb_name,
        args.previous_bba_orb_name,
        args.plot_diff,
    )
