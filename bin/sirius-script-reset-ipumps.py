#!/usr/bin/env python-sirius

import time
import epics
    
CONTROLLERS = {
    'SI-RA01:VA-SIPC-06':
        ['SI-01SAFE:VA-SIP150-MD',
         'SI-01C2FE:VA-SIP150-MD',
         'SI-0102BCFE:VA-SIP150-MD',
         'SR-RA01:VA-SIPC-06:C4'],
    'SI-RA02:VA-SIPC-05':
        ['SI-02C4:VA-SIP20-BG',
         'SI-03M1:VA-SIP20-BG',
         'SI-02SBFE:VA-SIP150-MD',
         'SI-02BCFE:VA-SIP150-MD',
        ],
    'SI-RA03:VA-SIPC-05':
        ['SI-03SPFE:VA-SIP150-MD',
         'SI-03C2FE:VA-SIP150-MD',
         'SI-03BCFE:VA-SIP150-MD',
         'SI-RA03:VA-SIPC-05:C4',
        ],
}


ION_PUMPS = [
    'SI-01BCFE:VA-SIP150-MD',
    'SI-02BCFE:VA-SIP150-MD',
    'SI-03BCFE:VA-SIP150-MD',
    'SI-04BCFE:VA-SIP150-MD',
    'SI-05BCFE:VA-SIP150-MD',
    'SI-06BCFE:VA-SIP150-MD',
    'SI-07BCFE:VA-SIP150-MD',
    'SI-08BCFE:VA-SIP150-MD',
    'SI-09BCFE:VA-SIP150-MD',
    'SI-10BCFE:VA-SIP150-MD',
    'SI-11BCFE:VA-SIP150-MD',
    'SI-12BCFE:VA-SIP150-MD',
    'SI-13BCFE:VA-SIP150-MD',
    'SI-14BCFE:VA-SIP150-MD',
    'SI-15BCFE:VA-SIP150-MD',
    'SI-16BCFE:VA-SIP150-MD',
    'SI-17BCFE:VA-SIP150-MD',
    'SI-18BCFE:VA-SIP150-MD',
    'SI-19BCFE:VA-SIP150-MD',
    'SI-20BCFE:VA-SIP150-MD',
    ]



def check_currents(pvs, threshold=0):
    while True:
        print('checking all ion pumps...')
        for ion_pump, pv in pvs.items():
            if pv.value < threshold:
                print('ion pump {} has current below threshold!'.format(ion_pump))
        time.sleep(0.2)
        
def create_ion_pumps_currents_pvs(ion_pumps):
    pvs = {ion_pump:epics.PV(ion_pump + ':Current-Mon') for ion_pump in ion_pumps}
    for pv in pvs.values():
        if not pv.wait_for_connection(timeout=10):
            print('timeout in {}'.format(pv.pvname))
    return pvs


pvs = create_ion_pumps_currents_pvs(ION_PUMPS)
check_currents(pvs, threshold=2e-7)




