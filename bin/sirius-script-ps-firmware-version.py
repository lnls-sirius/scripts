#!/usr/bin/env python-sirius
"""."""

import epics
import sys


from siriuspy.search import PSSearch


def select_psnames(psgroup):
    """."""
    # select only PS
    allps = []
    for ps in PSSearch.get_psnames():
        if ':PS-' in ps:
            allps.append(ps)
    psnames = []
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
            if ':PS-QD' in ps or ':PS-QF' in ps:
                psnames.append(ps)
    elif psgroup.lower() in ('li-magnetic-lenses', ):
        for ps in allps:
            if ':PS-Lens' in ps:
                psnames.append(ps)
    elif psgroup.lower() in ('li-correctors', ):
        for ps in allps:
            if ':PS-CH' in ps or ':PS-CV':
                psnames.append(ps)
    elif psgroup.lower() in ('li-solenoids', ):
        for ps in allps:
            if ':PS-Slnd' in ps:
                psnames.append(ps)
    elif psgroup.lower() == 'li':
        for ps in allps:
            if ps.startswith('LI-01:'):
                psnames.append(ps)
    return psnames


def print_help():
    """."""
    print("NAME")
    print("       sirius-script-ps-firmware-version.py - Print power supply firmware version")
    print("")
    print("SINOPSIS")
    print("       sirius-script-ps-firmware-version.py [--help] [--list ][all] [OTHERS]...")
    print("")
    print("DESCRIPTION")
    print("       Script used to print running versions of power supply firmwares")
    print("")
    print("       --help               print this help")
    print("")
    print("       --list               list power supplies")
    print("")
    print("       all                  versions of all magnets")
    print("")
    print("       tb-dipoles           versions of TB dipoles")
    print("")
    print("       tb-quadrupoles       versions of TB quadrupoles")
    print("")
    print("       tb-correctors        versions of TB correctors")
    print("")
    print("       tb                   versions of TB magnets")
    print("")
    print("       bo-dipoles           versions of BO dipoles")
    print("")
    print("       bo-quadrupoles       versions of BO quadrupoles")
    print("")
    print("       bo-sextupoles        versions of BO sextupoles")
    print("")
    print("       bo-correctors        versions of BO correctors")
    print("")
    print("       bo                   versions of BO magnets")
    print("")
    print("       li-dipole            versions of LI dipole or spectrometer")
    print("")
    print("       li-spectrometer      versions of LI dipole or spectrometer")
    print("")
    print("       li-quadrupoles       versions of LI quadrupoles")
    print("")
    print("       li-correctors        versions of LI correctors")
    print("")
    print("       li-solenoids         versions of LI solenoids")
    print("")
    print("       li                   versions of LI magnets")
    print("")
    print("       <POWER-SUPPLY>       versions of magnets excitated by <POWER-SUPPLY>")
    print("")
    print("       and so on...")
    print("")
    print("AUTHOR")
    print("       FACS-LNLS.")


def print_version(psnames):
    """."""
    nrls = max([len(ps) for ps in psnames])
    fmts = '{:<' + str(nrls) + '}: {}'
    for ps in psnames:
        pv = epics.PV(ps + ':Version-Cte', connection_timeout=0.1)
        print(fmts.format(ps, pv.value))


def run():
    """."""
    argv = [v for v in sys.argv[1:]]
    if len(argv) == 0 or '--help' in argv:
        print_help()
        sys.exit(0)

    list_flag = False
    psnames = []
    for arg in argv:
        if arg == '--list':
            list_flag = True
        else:
            psnames += select_psnames(arg)

    if list_flag:
        for ps in psnames:
            print(ps)
    else:
        print_version(psnames)


run()
