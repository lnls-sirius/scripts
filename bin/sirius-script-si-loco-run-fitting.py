#!/usr/bin/env python-sirius
"""Script for running LOCO algorithm."""

import os
import sys
import time

from mathphys.functions import save, load
import numpy as np

import siriuspy.clientconfigdb as servconf
from pymodels import si
import pyaccel as pyac
from apsuite.loco.config import LOCOConfigSI
from apsuite.loco.main import LOCO
from apsuite.loco.report import LOCOReport
from apsuite.optics_analysis.tune_correction import TuneCorr
import apsuite.commisslib as commisslib

# --- Constants ---
TUNE_X_INTEGER = 49
TUNE_Y_INTEGER = 14
DELTA_KICK_X_MEAS = 5e-6  # [rad]
DELTA_KICK_Y_MEAS = 5e-6  # [rad]
DELTA_FREQUENCY_MEAS = 37.5  # [Hz]

WEIGHT_CORR_SIZE = 281
DISPERSION_FACTOR = 2
DISPERSION_WEIGHT_MULTIPLIER = 75 / 15 * 1e6

QUAD_NUMBER = 270
SEXT_NUMBER = 280
DIP_NUMBER = 100

SVD_SELECTION_VALUE = -1

JACOBIAN_KL_QUAD_FNAME = "6d_KL_quadrupoles_trims"
JACOBIAN_KSL_SKEWQUAD_FNAME = "6d_KsL_skew_quadrupoles"

DEFAULT_NRITERS = 20
DEFAULT_DELTAKL_WEIGHT = 1000
DEFAULT_LAMBDA_LM = 0.001


def load_data(fname):
    """Loads LOCO data from a file."""
    sys.modules["apsuite.commissioning_scripts"] = commisslib
    return load(fname)


def move_tunes(model, tunex_goal, tuney_goal):
    """Adjusts the tunes of the model to match measured values."""
    tunecorr = TuneCorr(
        model, "SI", method="Proportional", grouping="TwoKnobs"
    )
    tunecorr.get_tunes(model)
    print(f"    tunes init  : {str(tunecorr.get_tunes(model))}")
    tunemat = tunecorr.calc_jacobian_matrix()
    tunecorr.correct_parameters(
        model=model,
        goal_parameters=np.array([tunex_goal, tuney_goal]),
        jacobian_matrix=tunemat,
        tol=1e-10,
    )
    print(f"    tunes final  : {str(tunecorr.get_tunes(model))}")


def _initialize_config_and_model():
    """Initializes LOCOConfigSI and the accelerator model."""
    config = LOCOConfigSI()
    config.model = si.create_accelerator()
    config.dim = "6d"
    return config


def _configure_cavity_and_radiation(config):
    """Configures cavity and radiation settings based on dimension."""
    if config.dim == "4d":
        config.model.cavity_on = False
        config.model.radiation_on = False
    elif config.dim == "6d":
        config.model.cavity_on = True
        config.model.radiation_on = False


def _configure_jacobian_elements(config):
    """Configures Jacobian matrix elements for LOCO."""
    config.use_dispersion = True
    config.use_diagonal = True
    config.use_offdiagonal = True


def _configure_fitting_families(config):
    """Configures whether to fit quadrupoles and dipoles in families."""
    config.use_quad_families = False
    config.use_dip_families = False


def _configure_constraints(config, deltakl_weight):
    """Configures constraints for LOCO fitting."""
    config.constraint_deltakl_step = True
    config.constraint_deltakl_total = False
    config.deltakl_normalization = 1 / deltakl_weight
    config.tolerance_delta = 1e-6
    config.tolerance_overfit = 1e-6


def _configure_inversion_and_minimization(config, lambda_lm):
    """Configures Jacobian inversion and minimization methods."""
    config.inv_method = LOCOConfigSI.INVERSION.Transpose
    config.min_method = LOCOConfigSI.MINIMIZATION.LevenbergMarquardt
    config.lambda_lm = lambda_lm
    config.fixed_lambda = False


def _configure_elements_to_fit(config):
    """Configures which elements to include in the fit."""
    config.fit_quadrupoles = True
    config.fit_sextupoles = False
    config.fit_dipoles = False
    config.quadrupoles_to_fit = None
    config.sextupoles_to_fit = None
    config.skew_quadrupoles_to_fit = config.famname_skewquadset.copy()
    fc2_idx = config.skew_quadrupoles_to_fit.index("FC2")
    config.skew_quadrupoles_to_fit.pop(fc2_idx)
    config.dipoles_to_fit = None


def _configure_coupling_and_gains(config):
    """Configures coupling, BPM, and corrector gains fitting."""
    config.fit_dipoles_kick = False
    if config.use_offdiagonal:
        config.fit_quadrupoles_coupling = False
        config.fit_sextupoles_coupling = False
        config.fit_dipoles_coupling = False
        config.fit_roll_bpm = True
        config.fit_skew_quadrupoles = True
    else:
        config.fit_quadrupoles_coupling = False
        config.fit_sextupoles_coupling = False
        config.fit_dipoles_coupling = False
        config.fit_roll_bpm = False
        config.fit_skew_quadrupoles = False
    config.fit_energy_shift = False
    config.fit_gain_bpm = True
    config.fit_gain_corr = True


def _configure_measurement_kicks(config):
    """Configures kicks used in the measurements."""
    config.delta_kickx_meas = DELTA_KICK_X_MEAS
    config.delta_kicky_meas = DELTA_KICK_Y_MEAS
    config.delta_frequency_meas = DELTA_FREQUENCY_MEAS


def _configure_girder_shifts(config):
    """Configures girder shift fitting."""
    config.fit_girder_shift = False


def _configure_weights(config):
    """Configures weights for BPMs, correctors, and gradients."""
    config.weight_bpm = None
    config.weight_corr = np.ones(WEIGHT_CORR_SIZE)
    config.weight_corr[-1] = DISPERSION_FACTOR * DISPERSION_WEIGHT_MULTIPLIER
    config.weight_deltakl = np.ones(
        QUAD_NUMBER + 0 * SEXT_NUMBER + 0 * DIP_NUMBER
    )


def _configure_svd(config):
    """Configures SVD method and selection."""
    config.svd_method = LOCOConfigSI.SVD.Selection
    config.svd_sel = SVD_SELECTION_VALUE
    config.parallel = True


def create_loco_config(
    goal_tunes,
    deltakl_weight=DEFAULT_DELTAKL_WEIGHT,
    lambda_lm=DEFAULT_LAMBDA_LM,
):
    """Creates and configures the LOCO object."""
    config = _initialize_config_and_model()

    _configure_cavity_and_radiation(config)
    _configure_jacobian_elements(config)
    _configure_fitting_families(config)
    _configure_constraints(config, deltakl_weight)
    _configure_inversion_and_minimization(config, lambda_lm)
    _configure_elements_to_fit(config)
    _configure_coupling_and_gains(config)
    _configure_measurement_kicks(config)
    _configure_girder_shifts(config)
    _configure_weights(config)
    _configure_svd(config)

    print("--- changing tunes for nominal model...")
    move_tunes(
        config.model,
        TUNE_X_INTEGER + goal_tunes[0],
        TUNE_Y_INTEGER + goal_tunes[1],
    )
    config.update()
    return config


def create_loco(
    loco_setup,
    load_jacobian=False,
    save_jacobian=False,
    folder_jacobian="",
    goal_tunes=None,
    deltakl_weight=DEFAULT_DELTAKL_WEIGHT,
    lambda_lm=DEFAULT_LAMBDA_LM,
):
    """Creates a LOCO object with the given setup."""
    config = create_loco_config(
        goal_tunes=goal_tunes,
        deltakl_weight=deltakl_weight,
        lambda_lm=lambda_lm,
    )

    if "orbmat_name" in loco_setup:
        client = servconf.ConfigDBClient(config_type="si_orbcorr_respm")
        orbmat_meas = np.array(
            client.get_config_value(name=loco_setup["orbmat_name"])
        )
        print("loading respmat from ServConf")
    elif "respmat" in loco_setup:
        orbmat_meas = loco_setup["respmat"]
        print("loading respmat from LOCO input file")
    else:
        raise Exception("LOCO input file do not have matrix or config name.")

    orbmat_meas[:, -1] *= 1e-6  # convert dispersion column from um to m
    config.goalmat = orbmat_meas

    alpha = pyac.optics.get_mcf(config.model)
    rf_frequency = loco_setup["rf_frequency"]
    config.measured_dispersion = -1 * alpha * rf_frequency * orbmat_meas[:, -1]

    config.update()
    print("")
    print(config)

    print("[create loco object]")
    loco = LOCO(config=config, save_jacobian_matrices=save_jacobian)

    if load_jacobian:
        loco.update(
            fname_jloco_kl_quad=os.path.join(
                folder_jacobian, JACOBIAN_KL_QUAD_FNAME
            ),
            fname_jloco_ksl_skewquad=os.path.join(
                folder_jacobian, JACOBIAN_KSL_SKEWQUAD_FNAME
            ),
        )
    else:
        loco.update()
    return loco


def run_and_save(
    setup_name,
    file_name,
    load_jacobian=False,
    save_jacobian=False,
    folder_jacobian=None,
    nriters=DEFAULT_NRITERS,
    deltakl_weight=DEFAULT_DELTAKL_WEIGHT,
    lambda_lm=DEFAULT_LAMBDA_LM,
    goal_tunes=None,
    force_tunes=False,
):
    """Runs the LOCO fitting and saves the results."""
    setup = load_data(setup_name)
    if "data" in setup.keys():
        setup = setup["data"]

    t0 = time.time()
    if goal_tunes is None:
        tunex_goal, tuney_goal = setup["tunex"], setup["tuney"]
    else:
        tunex_goal, tuney_goal = goal_tunes

    loco = create_loco(
        setup,
        load_jacobian=load_jacobian,
        save_jacobian=save_jacobian,
        folder_jacobian=folder_jacobian,
        goal_tunes=[tunex_goal, tuney_goal],
        deltakl_weight=deltakl_weight,
        lambda_lm=lambda_lm,
    )
    loco.run_fit(niter=nriters)
    if force_tunes:
        print("--- changing tunes for fitted model...")
        move_tunes(
            loco.fitmodel,
            TUNE_X_INTEGER + tunex_goal,
            TUNE_Y_INTEGER + tuney_goal,
        )

    loco_data = dict(
        fit_model=loco.fitmodel,
        config=loco.config,
        gain_bpm=loco.bpm_gain,
        gain_corr=loco.corr_gain,
        roll_bpm=loco.bpm_roll,
        energy_shift=loco.energy_shift,
        chi_history=loco.chi_history,
        res_history=loco.residue_history,
        girder_shift=loco.girder_shift,
        kldelta_history=loco.kldelta_history,
        ksldelta_history=loco.ksldelta_history,
    )
    save(loco_data, file_name)
    print(f"{file_name} saved!")
    dt = time.time() - t0
    print("running time: {:.1f} minutes".format(dt / 60))


def cleanup_png_files(folder):
    """Cleans up generated PNG plot files."""
    lst = [
        "histogram",
        "3dplot",
        "quad_by_family",
        "quad_by_s",
        "skewquad_by_s",
        "gains",
        "beta_beating",
        "dispersion_function",
    ]
    for name in lst:
        try:
            os.remove(os.path.join(folder, name + ".png"))
        except FileNotFoundError:
            pass  # silently ignore missing files


def main():
    """Main function to run the LOCO algorithm."""
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Run LOCO fitting and save files in the specified folder."
    )
    parser.add_argument(
        "filename_setup",
        type=str,
        help="Name of the LOCO setup file (.pickle)",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        default=os.getcwd(),
        help="Path to the folder for output files. "
        "Default is the current directory.",
    )
    parser.add_argument(
        "-j",
        "--jacobianfolder",
        type=str,
        default=None,
        help="Optional path to a folder containing precomputed Jacobians. "
        "Default is to compute and save in current directory.",
    )
    parser.add_argument(
        "-t",
        "--tunes",
        nargs=2,
        type=float,
        metavar=("NUX", "NUY"),
        default=None,
        help="Optional fractional tunes (nux nuy). "
        "Example: --tunes 0.16 0.22. Default is the measured ones.",
    )
    parser.add_argument(
        "-ft",
        "--forcetunes",
        action="store_true",
        help="Force fitted model to have the initial tunes. "
        "Default: False, set to True if flag is given.",
    )
    parser.add_argument(
        "-n",
        "--nriters",
        type=int,
        default=DEFAULT_NRITERS,
        help="Option of Nr. of Iters. Default is 20.",
    )
    parser.add_argument(
        "-w",
        "--deltakl_weight",
        type=float,
        default=DEFAULT_DELTAKL_WEIGHT,
        help="Weight for DeltaKL variation constraint. Default is 0.1.",
    )
    parser.add_argument(
        "-l",
        "--lambda_lm",
        type=float,
        default=DEFAULT_LAMBDA_LM,
        help="Lambda parameter for LevenbergMarquardt. Default is 0.001",
    )
    parser.add_argument(
        "-r",
        "--report",
        action="store_true",
        help="Create report. Default: False, set to True if flag is given.",
    )
    parser.add_argument(
        "-c",
        "--cleanup",
        action="store_true",
        help="Cleanup .png files. "
        "Default: False, set to True if flag is given.",
    )

    args = parser.parse_args()

    fname_setup = args.filename_setup
    if not os.path.isfile(fname_setup):
        raise ValueError(f"LOCO setup {fname_setup} not in current directory!")

    folder = args.folder
    folder_jac = args.jacobianfolder
    load_jac = True if folder_jac else False
    save_jac = False if load_jac else True

    if not os.path.exists(folder):
        print(f"Creating {folder} directory to put files...")
        os.makedirs(folder)

    if not folder.endswith("/"):
        folder += "/"

    fname_fit = "fitting_" + os.path.splitext(fname_setup)[0]
    fname_fit_path = os.path.join(folder, fname_fit)

    run_and_save(
        setup_name=fname_setup,
        file_name=fname_fit_path,
        load_jacobian=load_jac,
        save_jacobian=save_jac,
        folder_jacobian=folder_jac,
        nriters=args.nriters,
        goal_tunes=args.tunes,
        deltakl_weight=args.deltakl_weight,
        lambda_lm=args.lambda_lm,
        force_tunes=args.forcetunes,
    )

    if args.report:
        print("Creating report...")
        report = LOCOReport()
        report.create_report(
            folder=folder, fname_fit=fname_fit, fname_setup=fname_setup
        )
        print(f"{folder}report.pdf created!")

        if args.cleanup:
            cleanup_png_files(folder)
            print("All .png files deleted!")


if __name__ == "__main__":
    main()
