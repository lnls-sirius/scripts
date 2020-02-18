#!/usr/bin/env python-sirius

from siriuspy.clientconfigdb import ConfigDBClient as CDBClient


def rename_pvname(pvname):
    """."""
    return pvname.replace(':seti', ':Current-SP')


def update_configdb(conn, config_name, config_value):
    """."""
    pvs_data = config_value['pvs']
    for j, data in enumerate(pvs_data):
        pvname, value, delay = data
        if pvname.startswith('LI-') and ':PS-' in pvname:
            print('{:<30s} {} {}'.format(pvname, value, delay))
    print()
    conn.insert_config(name=config_name, value=config_value)


def rename_in_config(conn, config_name, config_value):
    """."""
    pvs_data = config_value['pvs']
    changed = False
    for j, data in enumerate(pvs_data):
        pvname, *_ = data
        if pvname.startswith('LI-') and ':PS-' in pvname and ':seti' in pvname:
            if not changed:
                print('{}'.format(config_name))
            changed = True
            new_pvname = rename_pvname(pvname)
            pvs_data[j][0] = new_pvname
            # print('{} -> {}'.format(pvname, new_pvname))
    if changed:
        update_configdb(conn, config_name, config_value)
        print()
        return True
    return False


def rename_global_config():
    """."""
    conn = CDBClient(config_type='global_config')
    configs = conn.find_configs()

    for config in configs:
        config_name = config['name']
        # config_name = 'si_chromcorr_orbcorr_tmp'
        config_value = conn.get_config_value(config_name)
        changed = rename_in_config(conn, config_name, config_value)
        if changed:
            break


rename_global_config()
