#!/usr/bin/env python-sirius

import sys
import getpass
from siriuspy.clientarch import ClientArchiver


DEFAULT_FUNCTION = 'NONE'


def rename_dclinks():
    """."""

    print('[rename_dclinks]')
    print()

    rename_table = {
        'IA-01RaCtrl:PS-DCLink-AS1': 'IA-01RaPS01:PS-DCLink-AS',
        'IA-01RaCtrl:PS-DCLink-AS2': 'IA-01RaPS02:PS-DCLink-SI',
        'IA-02RaCtrl:PS-DCLink-AS1': 'IA-02RaPS01:PS-DCLink-AS',
        'IA-02RaCtrl:PS-DCLink-AS2': 'IA-02RaPS02:PS-DCLink-SI',
        'IA-03RaCtrl:PS-DCLink-AS1': 'IA-03RaPS01:PS-DCLink-AS',
        'IA-03RaCtrl:PS-DCLink-AS2': 'IA-03RaPS02:PS-DCLink-SI',
        'IA-04RaCtrl:PS-DCLink-AS1': 'IA-04RaPS01:PS-DCLink-AS',
        'IA-04RaCtrl:PS-DCLink-AS2': 'IA-04RaPS02:PS-DCLink-SI',
        'IA-05RaCtrl:PS-DCLink-AS1': 'IA-05RaPS01:PS-DCLink-AS',
        'IA-05RaCtrl:PS-DCLink-AS2': 'IA-05RaPS02:PS-DCLink-SI',
        'IA-06RaCtrl:PS-DCLink-AS1': 'IA-06RaPS01:PS-DCLink-AS',
        'IA-06RaCtrl:PS-DCLink-AS2': 'IA-06RaPS02:PS-DCLink-SI',
        'IA-07RaCtrl:PS-DCLink-AS1': 'IA-07RaPS01:PS-DCLink-AS',
        'IA-07RaCtrl:PS-DCLink-AS2': 'IA-07RaPS02:PS-DCLink-SI',
        'IA-08RaCtrl:PS-DCLink-AS1': 'IA-08RaPS01:PS-DCLink-AS',
        'IA-08RaCtrl:PS-DCLink-AS2': 'IA-08RaPS02:PS-DCLink-SI',
        'IA-09RaCtrl:PS-DCLink-AS1': 'IA-09RaPS01:PS-DCLink-AS',
        'IA-09RaCtrl:PS-DCLink-AS2': 'IA-09RaPS02:PS-DCLink-SI',
        'IA-10RaCtrl:PS-DCLink-AS1': 'IA-10RaPS01:PS-DCLink-AS',
        'IA-10RaCtrl:PS-DCLink-AS2': 'IA-10RaPS02:PS-DCLink-SI',
        'IA-11RaCtrl:PS-DCLink-AS1': 'IA-11RaPS01:PS-DCLink-AS',
        'IA-11RaCtrl:PS-DCLink-AS2': 'IA-11RaPS02:PS-DCLink-SI',
        'IA-12RaCtrl:PS-DCLink-AS1': 'IA-12RaPS01:PS-DCLink-AS',
        'IA-12RaCtrl:PS-DCLink-AS2': 'IA-12RaPS02:PS-DCLink-SI',
        'IA-13RaCtrl:PS-DCLink-AS1': 'IA-13RaPS01:PS-DCLink-AS',
        'IA-13RaCtrl:PS-DCLink-AS2': 'IA-13RaPS02:PS-DCLink-SI',
        'IA-14RaCtrl:PS-DCLink-AS1': 'IA-14RaPS01:PS-DCLink-AS',
        'IA-14RaCtrl:PS-DCLink-AS2': 'IA-14RaPS02:PS-DCLink-SI',
        'IA-15RaCtrl:PS-DCLink-AS1': 'IA-15RaPS01:PS-DCLink-AS',
        'IA-15RaCtrl:PS-DCLink-AS2': 'IA-15RaPS02:PS-DCLink-SI',
        'IA-16RaCtrl:PS-DCLink-AS1': 'IA-16RaPS01:PS-DCLink-AS',
        'IA-16RaCtrl:PS-DCLink-AS2': 'IA-16RaPS02:PS-DCLink-SI',
        'IA-17RaCtrl:PS-DCLink-AS1': 'IA-17RaPS01:PS-DCLink-AS',
        'IA-17RaCtrl:PS-DCLink-AS2': 'IA-17RaPS02:PS-DCLink-SI',
        'IA-18RaCtrl:PS-DCLink-AS1': 'IA-18RaPS01:PS-DCLink-AS',
        'IA-18RaCtrl:PS-DCLink-AS2': 'IA-18RaPS02:PS-DCLink-SI',
        'IA-19RaCtrl:PS-DCLink-AS1': 'IA-19RaPS01:PS-DCLink-AS',
        'IA-19RaCtrl:PS-DCLink-AS2': 'IA-19RaPS02:PS-DCLink-SI',
        'IA-20RaCtrl:PS-DCLink-AS1': 'IA-20RaPS01:PS-DCLink-AS',
        'IA-20RaCtrl:PS-DCLink-AS2': 'IA-20RaPS02:PS-DCLink-SI'}

    carch = ClientArchiver()

    # authentication
    print('- authenticating...')
    username, password = get_authentication()
    # username, password = 'ximenes.resende', 'SENHA'
    ret = carch.login(username, password)
    if not ret:
        print('Could not be authenticated!')
        return
    print()

    print('- renaming PVs')
    print()
    for old_name, new_name in rename_table.items():
        print(' * {} -> {}'. format(old_name, new_name))
        print()
        dclink_name_pvs = old_name + ':*'
        pvs = carch.getAllPVs(dclink_name_pvs)
        for old_pv in pvs:
            new_pv = old_pv.replace(old_name, new_name)
            rename_pv(carch, old_pv, new_pv)
            print(' . {} -> {}'.format(old_pv, new_pv))
            rename_pv(carch, old_name, new_name)
        print()


def rename_pv(carch, old_pv, new_pv):
    """."""
    # pause
    print('   pausing...')
    carch.pausePVs(old_pv)
    # rename
    print('   renaming...')
    carch.renamePV(old_pv, new_pv)
    # resume
    print('   resuming...')
    carch.resumePVs(new_pv)


def get_authentication():
    """."""
    username = input('archiver username: ')
    password = getpass.getpass('username password: ')
    return username, password


def get_function():
    """."""
    if len(sys.argv) == 1:
        funcname = DEFAULT_FUNCTION
    else:
        funcname = sys.argv[1]
    # return symbol to the function to be executed
    return globals()[funcname]


def print_help():
    """."""
    _, ename = sys.argv[0].split('sirius')
    ename = 'sirius' + ename
    print('Usage: {} FUNCTION'.format(ename))


def run():
    """."""
    if len(sys.argv) > 2:
        print_help()
    else:
        func = get_function()
        func()


if __name__ == "__main__":
    run()
