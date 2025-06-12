#!/usr/bin/env python-sirius
"""Script to set LOCO-fitted strengths to SI and correct coupling."""

import os
import sys

import numpy as np
from mathphys.functions import load_pickle
from apsuite.commisslib.apply_strengths import (
    SetOpticsMode,
    SISetTrimStrengths,
)

# Achromatic skew quadrupole variations to adjust betatron coupling,
# it is -(v1 + v4)/np.sqrt(2) where v1 and v4 are the first and fourth
# left-singular vectors of jacobian matrix calculated with
# apsuite.optics.coupling_correction.calc_jacobian_matrix() using the
# nominal SIRIUS lattice
ACHROM_QS_ADJ = 1e-4 * np.array(
    [
        -0.53435125,
        1.83818311,
        1.98691151,
        1.75361165,
        1.56175837,
        -0.88710175,
        -1.15014152,
        -2.18259391,
        -0.53435125,
        1.83818311,
        1.98691151,
        1.75361165,
        1.56175837,
        -0.88710175,
        -1.15014152,
        -2.18259391,
        -0.53435125,
        1.83818311,
        1.98691151,
        1.75361165,
        1.56175837,
        -0.88710175,
        -1.15014152,
        -2.18259391,
        -0.53435125,
        1.83818311,
        1.98691151,
        1.75361165,
        1.56175837,
        -0.88710175,
        -1.15014152,
        -2.18259391,
        -0.53435125,
        1.83818311,
        1.98691151,
        1.75361165,
        1.56175837,
        -0.88710175,
        -1.15014152,
        -2.18259391,
    ]
)
TIMEOUT = 10
WAIT_MON = False


def ask_yes_no(prompt):
    """Prompt user for yes/no input. Default to yes."""
    print(f"{prompt} [Y/N]: ", end="", flush=True)
    try:
        response = input().strip().lower()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    return response in ("", "y", "yes")


def prompt_apply_reapply(apply_func):
    """Prompt to accept changes and apply, then prompt to reapply if needed."""
    if not ask_yes_no("Accept changes?"):
        return
    ok = apply_func()
    while not ok:
        if ask_yes_no("Application failed. Try again?"):
            print("Reapplying...")
            ok = apply_func()


def apply_family_average(folder, set_fams_avg):
    """Apply quadrupoles average strengths."""
    print("\nApplying families average...")
    mag_sel = "quadrupoles"
    mags, init_strengths = set_fams_avg.get_strengths(magname_filter=mag_sel)
    fam_avg = load_pickle(folder + "quad_family_average.pickle")
    delta_avg = np.array([fam_avg[mag.dev] for mag in mags])
    goal_stren = init_strengths - delta_avg

    def _apply_strengths(apply=True):
        return set_fams_avg.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
            timeout=TIMEOUT,
            wait_mon=WAIT_MON,
        )

    _apply_strengths(apply=False)

    prompt_apply_reapply(_apply_strengths)


def apply_normal_quad_trims(folder, set_trims):
    """Apply normal quads trims strengths."""
    print("\nApplying normal quads trims...")
    mag_sel = "quadrupoles"
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    deltas = np.loadtxt(folder + "quad_trims_deltakl_zero_average.txt")
    goal_stren = init_strengths - deltas
    mean = np.mean(deltas)
    print(f"Mean close to zero? {np.isclose(mean, 0)}. Mean: {mean}")

    def _apply_strengths(apply=True):
        return set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
            timeout=TIMEOUT,
            wait_mon=WAIT_MON,
        )

    _apply_strengths(apply=False)

    prompt_apply_reapply(_apply_strengths)


def apply_skew_quad_trims(folder, set_trims):
    """Apply skew quads trims strengths."""
    print("\nApplying skew quads trims...")
    mag_sel = "skew_quadrupole"
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    deltas = np.loadtxt(folder + "skewquad_deltaksl.txt")
    goal_stren = init_strengths - deltas

    def _apply_strengths(apply=True):
        return set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
            timeout=TIMEOUT,
            wait_mon=WAIT_MON,
        )

    _apply_strengths(apply=False)

    prompt_apply_reapply(_apply_strengths)


def control_coupling(set_trims):
    """Control coupling variation [%]."""
    try:
        coupling = float(input("Insert desired coupling variation in [%] = "))
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    if not coupling:
        return
    print(f"Applying {coupling:.2f}% of coupling variation...")
    mag_sel = ".*M1:PS-QS.*|.*M2:PS-QS.*"
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    # 1.2 is a heuristic factor to get a 1:1 relation to coupling variation
    delta_stren = -ACHROM_QS_ADJ * 1.2 * coupling
    goal_stren = init_strengths + delta_stren

    def _apply_strengths(apply=True):
        return set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
            timeout=TIMEOUT,
            wait_mon=WAIT_MON,
        )

    _apply_strengths(apply=False)

    prompt_apply_reapply(_apply_strengths)


def main():
    """."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Applies LOCO-fitted strengths to the machine."
    )

    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default=os.getcwd(),
        help="Path to folder containing fitted-strengths files. "
        "Defaults to current working directory.",
    )

    args = parser.parse_args()
    folder = args.folder
    if not folder.endswith("/"):
        folder += "/"

    set_fams_avg = SetOpticsMode(acc="SI", optics_mode=None)
    set_trims = SISetTrimStrengths(model=None)

    apply_family_average(folder, set_fams_avg)
    apply_normal_quad_trims(folder, set_trims)
    apply_skew_quad_trims(folder, set_trims)
    control_coupling(set_trims)


if __name__ == "__main__":
    main()
