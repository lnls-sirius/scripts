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


def ask_yes_no(prompt):
    """Prompt user for yes/no input. Default to yes."""
    print(f"{prompt} [Y/N]: ", end="", flush=True)
    try:
        response = input().strip().lower()
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    return response in ("", "y", "yes")


def prompt_apply_then_check(apply_func):
    """Prompt to accept changes and apply, then prompt to reapply if needed."""
    if not ask_yes_no("Accept changes?"):
        sys.exit(0)
    apply_func()
    if ask_yes_no("Check if applied?"):
        print("Reapplying...")
        apply_func()


def apply_family_average(folder):
    """Apply quadrupoles average strengths."""
    print("Applying families average...")
    mag_sel = "quadrupoles"
    set_optics = SetOpticsMode(acc="SI", optics_mode=None)
    mags, init_strengths = set_optics.get_strengths(magname_filter=mag_sel)
    fam_avg = load_pickle(folder + "quad_family_average.pickle")
    delta_avg = np.array([fam_avg[mag.dev] for mag in mags])
    goal_stren = init_strengths - delta_avg

    def _apply_strengths(apply=True):
        set_optics.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
        )

    _apply_strengths(apply=False)

    prompt_apply_then_check(_apply_strengths)


def apply_normal_quad_trims(folder):
    """Apply normal quads trims strengths."""
    print("Applying normal quads trims...")
    mag_sel = "quadrupoles"
    set_trims = SISetTrimStrengths(model=None)
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    deltas = np.loadtxt(folder + "quad_trims_deltakl_no_average__.txt")
    goal_stren = init_strengths - deltas
    mean = np.mean(deltas)
    print(f"Mean close to zero? {np.isclose(mean, 0)}. Mean: {mean}")

    def _apply_strengths(apply=True):
        set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
        )

    _apply_strengths(apply=False)

    prompt_apply_then_check(_apply_strengths)


def apply_skew_quad_trims(folder):
    """Apply skew quads trims strengths."""
    print("Applying skew quads trims...")
    mag_sel = "skew_quadrupole"
    set_trims = SISetTrimStrengths(model=None)
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    deltas = np.loadtxt(folder + "skewquad_deltaksl__.txt")
    goal_stren = init_strengths - deltas

    def _apply_strengths(apply=True):
        set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
        )

    _apply_strengths(apply=False)

    prompt_apply_then_check(_apply_strengths)


def control_coupling():
    """Control coupling variation [%]."""
    print("Insert desired coupling variation in [%]", end="", flush=True)
    try:
        coupling = float(input())
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(1)
    if not coupling:
        return
    print(f"Applying {coupling:.2f}% of coupling variation...")
    mag_sel = ".*M1:PS-QS.*|.*M2:PS-QS.*"
    set_trims = SISetTrimStrengths(model=None)
    _, init_strengths = set_trims.get_strengths(magname_filter=mag_sel)
    # 1.2 is a heuristic factor to get a 1:1 relation to coupling variation
    delta_stren = -ACHROM_QS_ADJ * 1.2 * coupling
    goal_stren = init_strengths + delta_stren

    def _apply_strengths(apply=True):
        set_trims.apply_strengths(
            strengths=goal_stren,
            magname_filter=mag_sel,
            percentage=100,
            apply=apply,
            print_change=True,
        )

    _apply_strengths(apply=False)

    prompt_apply_then_check(_apply_strengths)


def print_help():
    """."""
    print("""
    Usage: script.py [FOLDER]

    Arguments:
    FOLDER     Optional. Path to the folder containing the pickle and txt
               files. If not provided, the current working directory is used.

    This script applies average corrections and trims for quadrupoles,
    skew quadrupoles, and corrects transverse coupling using files found in
    the specified folder.

    You will be prompted to confirm before any changes are applied.
    """)


def main():
    """."""
    if "-h" in sys.argv or "--help" in sys.argv:
        print_help()
        sys.exit(0)

    folder = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    if not folder.endswith("/"):
        folder += "/"

    apply_family_average(folder)
    apply_normal_quad_trims(folder)
    apply_skew_quad_trims(folder)
    control_coupling()


if __name__ == "__main__":
    main()
