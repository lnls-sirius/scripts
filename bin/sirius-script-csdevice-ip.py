#!/usr/bin/env python-sirius
"""Script that returns csdevice IP."""

import sys as _sys
from siriuspy.csdevice.util import get_device_2_ioc_ip as _get_device_2_ioc_ip
from siriuspy.search.ps_search import PSSearch as _PSSearch


def get_devname():
    """."""
    args = [v for v in _sys.argv[1:]]

    is_dclink = False
    if '--dclink' in args:
        is_dclink = True
        args.remove('--dclink')

    if is_dclink:
        psname = args[0]
        devname = _PSSearch.conv_psname_2_dclink(psname)
    else:
        devname = args[0]
    return devname


def get_ip():
    """."""
    dev2ip = _get_device_2_ioc_ip()
    devname = get_devname()
    if devname in dev2ip:
        ip = dev2ip[devname]
    else:
        ip = None
    return ip


def run():
    """."""
    ip = get_ip()
    print(ip)


run()
