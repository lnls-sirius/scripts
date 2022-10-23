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

    'SI-RA05:VA-SIPC-05':
        ['SI-05SAFE:VA-SIP150-MD',
         'SI-05C2FE:VA-SIP150-MD',
         'SI-05BCFE:VA-SIP150-MD',
         'SI-RA05:VA-SIPC-05:C4',
        ],

    'SI-RA06:VA-SIPC-04':
        ['SI-06C4:VA-SIP20-BG',
         'SI-07M1:VA-SIP20-BG',
         'SI-06SBFE:VA-SIP150-MD',
         'SI-06BCFE:VA-SIP150-MD',
        ],

    'SI-RA07:VA-SIPC-05':
        ['SI-07SPFE:VA-SIP150-MD',
         'SI-07C2FE:VA-SIP150-MD',
         'SI-07BCFE:VA-SIP150-MD',
         'SR-RA07:VA-SIPC-05:C4',
        ],

    'SI-RA09:VA-SIPC-05':
        ['SI-09SAFE:VA-SIP150-MD',
         'SI-09C2FE:VA-SIP150-MD',
         'SI-09BCFE:VA-SIP150-MD',
         'SR-RA09:VA-SIPC-05:C4',
        ],

    'SI-RA10:VA-SIPC-04':
        ['SI-10C4:VA-SIP20-BG',
         'SI-11M1:VA-SIP20-BG',
         'SI-10SBFE:VA-SIP150-MD',
         'SI-10BCFE:VA-SIP150-MD',
        ],

    'SI-RA11:VA-SIPC-05':
        ['SI-11SPFE:VA-SIP150-MD',
         'SI-11C2FE:VA-SIP150-MD',
         'SI-11BCFE:VA-SIP150-MD',
         'SR-RA11:VA-SIPC-05:C4',
        ],

    'SI-RA12:VA-SIPC-04':
        ['SI-12C4:VA-SIP20-BG',
         'SI-13M1:VA-SIP20-BG',
         'SI-12SBFE:VA-SIP150-MD',
         'SI-12BCFE:VA-SIP150-MD',
        ],

    'SI-RA13:VA-SIPC-05':
        ['SI-13SAFE:VA-SIP150-MD',
         'SI-13C2FE:VA-SIP150-MD',
         'SI-13BCFE:VA-SIP150-MD',
         'SR-RA13:VA-SIPC-05:C4',
        ],

    'SI-RA14:VA-SIPC-04':
        ['SI-14C4:VA-SIP20-BG',
         'SI-15M1:VA-SIP20-BG',
         'SI-14SBFE:VA-SIP150-MD',
         'SI-14BCFE:VA-SIP150-MD',
        ],

    'SI-RA15:VA-SIPC-05':
        ['SI-15SPFE:VA-SIP150-MD',
         'SI-15C2FE:VA-SIP150-MD',
         'SI-15BCFE:VA-SIP150-MD',
         'SR-RA15:VA-SIPC-05:C4',
        ],

    'SI-RA16:VA-SIPC-04':
        ['SI-16C4:VA-SIP20-BG',
         'SI-17M1:VA-SIP20-BG',
         'SI-16SBFE:VA-SIP150-MD',
         'SI-16BCFE:VA-SIP150-MD',
        ],

    'SI-RA17:VA-SIPC-05':
        ['SI-17SAFE:VA-SIP150-MD',
         'SI-17C2FE:VA-SIP150-MD',
         'SI-17BCFE:VA-SIP150-MD',
         'SR-RA17:VA-SIPC-05:C4',
        ],

    'SI-RA18:VA-SIPC-04':
        ['SI-18C4:VA-SIP20-BG',
         'SI-19M1:VA-SIP20-BG',
         'SI-18SBFE:VA-SIP150-MD',
         'SI-18BCFE:VA-SIP150-MD',
        ],  

    'SI-RA19:VA-SIPC-05':
        ['SI-19SPFE:VA-SIP150-MD',
         'SI-19C2FE:VA-SIP150-MD',
         'SI-19BCFE:VA-SIP150-MD',
         'SR-RA19:VA-SIPC-05:C4',
        ],

    'SI-RA20:VA-SIPC-06':
        ['SI-20C4:VA-SIP20-BG',
         'SI-01M1:VA-SIP20-BG',
         'SI-20SBFE:VA-SIP150-MD',
         'SI-20BCFE:VA-SIP150-MD',
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
    'SI-01C2FE:VA-SIP150-MD',
    'SI-03C2FE:VA-SIP150-MD',
    'SI-05C2FE:VA-SIP150-MD',
    'SI-07C2FE:VA-SIP150-MD',
    'SI-09C2FE:VA-SIP150-MD',
    'SI-11C2FE:VA-SIP150-MD',
    'SI-13C2FE:VA-SIP150-MD',
    'SI-15C2FE:VA-SIP150-MD',
    'SI-17C2FE:VA-SIP150-MD',
    'SI-19C2FE:VA-SIP150-MD',
    'SI-02SBFE:VA-SIP150-MD',
    'SI-04SBFE:VA-SIP150-MD',
    'SI-06SBFE:VA-SIP150-MD',
    'SI-08SBFE:VA-SIP150-MD',
    'SI-10SBFE:VA-SIP150-MD',
    'SI-12SBFE:VA-SIP150-MD',
    'SI-14SBFE:VA-SIP150-MD',
    'SI-16SBFE:VA-SIP150-MD',
    'SI-18SBFE:VA-SIP150-MD',
    'SI-20SBFE:VA-SIP150-MD',
    'SI-01SAFE:VA-SIP150-MD',
    'SI-05SAFE:VA-SIP150-MD',
    'SI-09SAFE:VA-SIP150-MD',
    'SI-13SAFE:VA-SIP150-MD',
    'SI-17SAFE:VA-SIP150-MD',
    'SI-03SPFE:VA-SIP150-MD',
    'SI-07SPFE:VA-SIP150-MD',
    'SI-11SPFE:VA-SIP150-MD',
    'SI-15SPFE:VA-SIP150-MD',
    'SI-19SPFE:VA-SIP150-MD',
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




