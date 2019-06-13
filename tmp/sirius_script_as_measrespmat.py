#!/usr/bin/env python-sirius

import time
from threading import Thread
from copy import deepcopy as _dcopy
import numpy as np
from siriuspy.epics import PV
from siriuspy.csdevice.orbitcorr import SOFBFactory


class MeasRespMat:

    def __init__(self):
        self._bosofb = SOFBFactory.create('bo')
        self._tbsofb = SOFBFactory.create('tb')
        corrs = \
            self._tbsofb.CH_NAMES + self._bosofb.CH_NAMES +\
            self._tbsofb.CV_NAMES + self._bosofb.CV_NAMES
        corrs = [nme + ':Kick-SP' for nme in corrs]
        corrs = corrs + [
            'TB-04:PM-InjSept:Kick-SP', 'BO-01D:PM-InjKckr:Kick-SP']
        self._corr_pvs = [PV(cor) for cor in corrs]
        self._orb_pvs = [
            PV('TB-Glob:AP-SOFB:SPassOrbX-Mon'),
            PV('BO-Glob:AP-SOFB:MTurnIdxOrbX-Mon'),
            PV('TB-Glob:AP-SOFB:SPassOrbY-Mon'),
            PV('BO-Glob:AP-SOFB:MTurnIdxOrbY-Mon')]
        self._reset_pvs = [
            PV('BO-Glob:AP-SOFB:SmoothReset-Cmd'),
            PV('TB-Glob:AP-SOFB:SmoothReset-Cmd')]
        self._wait_pv = PV('BO-Glob:AP-SOFB:SmoothNrPts-RB')
        self._len_orb = 2*len(self._bosofb.BPM_NAMES)
        self._len_orb += 2*len(self._tbsofb.BPM_NAMES)
        self._thread = None
        self._respmat = None
        self._stop = False
        self._index = 0

    @property
    def connected(self):
        for cor in self._corr_pvs:
            if not cor.connected:
                print('Corrector {} not connected.'.format(cor.pvname))
                return False
        for bpm in self._orb_pvs:
            if not bpm.connected:
                print('Orbit {} not connected.'.format(bpm.pvname))
                return False
        for res in self._reset_pvs:
            if not res.connected:
                print('Orbit {} not connected.'.format(res.pvname))
                return False
        if not self._wait_pv.connected:
            print('Wait PV {} not connected.'.format(self._wait_pv.pvname))
            return False
        return True

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, value):
        self._index = int(value)

    @property
    def current_corrector(self):
        return self._corr_pvs[self._index].pvname

    @property
    def respmat(self):
        return _dcopy(self._respmat)

    def stop_meas(self):
        self._stop = True

    def start_meas(self):
        if self._thread is not None and self._thread.is_alive():
            return False
        self._stop = False
        self._thread = Thread(target=self._meas_respmat, daemon=True)

    def save_respmat_tofile(self, name=None):
        if not isinstance(self._respmat, np.ndarray):
            print('RespMat is not ready yet')
            return
        name = name or 'respmat-tb-bo.txt'
        np.savetxt(name, self._respmat)

    def get_orbit(self):
        time.sleep(1)
        for pvr in self._reset_pvs:
            pvr.value = 1
        time.sleep(self._wait_pv.value * 0.5 + 1)
        orb = np.array([orb.value for orb in self._orb_pvs])
        return orb.flatten()

    def _meas_respmat(self):
        if not self._respmat:
            self._respmat = list()
        print('\n\nStarting measurement of RespMat:\n')
        for i, corr in enumerate(self._index, self._corr_pvs[self._index:]):
            if 'MA-CH:' in corr.pvname:
                dtheta = 250  # in urad
            elif 'MA-CV:' in corr.pvname:
                dtheta = 150  # in urad
            elif 'PM-InjSept:' in corr.pvname:
                dtheta = 0.150  # in mrad
            else:
                dtheta = 0.150  # in mrad
            corr.value += dtheta/2
            orbp = self.get_orbit()
            corr.value -= dtheta
            orbn = self.get_orbit()
            corr.value += dtheta/2
            self._respmat.append((orbp-orbn)/dtheta)
            self._index = i
            print('    Measuring {0:d} of {1:d}: Magnet {2:s}'.format(
                self._index, len(self._corr_pvs), self.current_corrector))
            if self._stop:
                break
        else:
            self._index = 0
            self._respmat = np.array(self._respmat).T


if __name__ == '__main__':
    meas = MeasRespMat()
