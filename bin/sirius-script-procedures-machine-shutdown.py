#!/usr/bin/env python-sirius
"""Machine shutdown script."""


import logging as _log
import sys as _sys
import time as _time
from threading import Thread as _Thread

from siriuspy.callbacks import Callback as _Callback
from siriuspy.devices import ASLLRF as _ASLLRF, ASMPSCtrl as _ASMPSCtrl, \
    ASPPSCtrl as _ASPPSCtrl, BOLLRFPreAmp as _BOLLRFPreAmp, \
    BORF300VDCAmp as _BORF300VDCAmp, BORFCavMonitor as _BORFCavMonitor, \
    BORFDCAmp as _BORFDCAmp, DCCT as _DCCT, DeviceSet as _DeviceSet, \
    EGFilament as _EGFilament, EGHVPS as _EGHVPS, \
    EGTriggerPS as _EGTriggerPS, EVG as _EVG, HLFOFB as _HLFOFB, ID as _ID, \
    InjCtrl as _InjCtrl, LIModltr as _LIModltr, MachShift as _MachShift, \
    SILLRFPreAmp as _SILLRFPreAmp, SIRFACAmp as _SIRFACAmp, \
    SIRFCavMonitor as _SIRFCavMonitor, SIRFDCAmp as _SIRFDCAmp, \
    SOFB as _SOFB
from siriuspy.devices.bbb import BunchbyBunch as _BbB, Feedback as _BbBFB
from siriuspy.devices.pstesters import PSTesterFactory as _PSTesterFactory, \
    Triggers as _PSTriggers
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.pwrsupply.csdev import Const as _PSC  # noqa: N814
from siriuspy.search import HLTimeSearch as _HLTimeSearch, \
    PSSearch as _PSSearch

# Configure Logging
_log.basicConfig(
    format='%(levelname)7s | %(asctime)s ::: %(message)s',
    datefmt='%F %T', level=_log.INFO,
    handlers=[_log.StreamHandler(_sys.stdout, flush=True)],
    filemode='a')


class LogCallback(_Callback):
    """Base class for logging using callbacks."""

    def __init__(self, log_callback=None):
        """."""
        super().__init__(log_callback)

    def log(self, message):
        """Log by callback."""
        if self.has_callbacks:
            self.run_callbacks(message)
            return
        if 'ERR' in message:
            _log.error(message[4:])
        elif 'FATAL' in message:
            _log.error(message[6:])
        elif 'WARN' in message:
            _log.warning(message[5:])
        else:
            _log.info(message)


class ThreadWithReturnValue(_Thread):
    """."""

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None):
        """."""
        kwargs = {} if not kwargs else kwargs
        _Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        """."""
        if self._target is not None:
            self._return = self._target(*self._args, **self._kwargs)

    def join(self, *args):
        """."""
        _Thread.join(self, *args)
        return self._return


class IDParking(_DeviceSet, LogCallback):
    """ID."""

    TIMEOUT_WAIT_FOR_CONNECTION = 5.0  # [s]

    def __init__(self, devname, log_callback=None):
        """Init."""
        self._abort = False
        self._is_parking = False

        device = _ID(devname)
        self._device = device

        _DeviceSet.__init__(self, [device, ], devname=devname)
        LogCallback.__init__(self, log_callback)

    @property
    def is_parking(self):
        """Is running parking procedure."""
        return self._is_parking

    @property
    def device(self):
        """Return ID device."""
        return self._device

    def abort_execution(self):
        """Set abort execution flag."""
        self._abort = True

    def continue_execution(self):
        """Check whether to continue execution based on abort flag state."""
        if self._abort:
            self._abort = False
            self.log(f'ERR:Aborting {self.devname} parking.')
            self._is_parking = False
            return False
        return True

    def cmd_park_device(self):
        """Park ID."""
        self._is_parking = True

        # connections checking
        if not self._connections_checking():
            return False

        # beamline control
        if not self._disable_beamline_ctrl():
            return False

        # stopping previous movement
        if not self._stop_movements():
            return False

        # setting speeds
        if not self._set_speeds():
            return False

        # move to parked position
        if not self._move_to_parked():
            return False

        # success at this point
        self.log(f'Successfully parked {self.devname}.')
        self._is_parking = False
        return True

    # --- private methods ---

    def _connections_checking(self):
        self.log(f'Checking {self.devname} connections...')
        if not self.device.wait_for_connection(
                timeout=IDParking.TIMEOUT_WAIT_FOR_CONNECTION):
            self.log(f'ERR:{self.devname} not connected.')
            self._is_parking = False
            return False
        if not self.continue_execution():
            return False
        return True

    def _disable_beamline_ctrl(self):
        self.log(f'Stopping {self.devname} movement...')
        if not self.device.cmd_move_stop():
            self.log(f'ERR:Failed to stop {self.devname}.')
            self._is_parking = False
            return False
        if not self.continue_execution():
            return False
        return True

    def _stop_movements(self):
        self.log(f'Setting {self.devname} speeds...')
        value = self.device.pparameter_speed_max
        if value is not None:
            if not self.device.set_pparameter_speed(value):
                self.log(f'ERR:Failed to set {self.devname} pparam speed.')
                self._is_parking = False
                return False
        value = self._device.kparameter_speed_max
        if value is not None:
            if not self._device.set_kparameter_speed(value):
                self.log(f'ERR:Failed to set {self.devname} kparam speed.')
                self._is_parking = False
                return False
        if not self.continue_execution():
            return False
        return True

    def _set_speeds(self):
        self.log(f'Setting {self.devname} speeds...')
        value = self.device.pparameter_speed_max
        if value is not None:
            if not self.device.set_pparameter_speed(value):
                self.log(f'ERR:Failed to set {self.devname} pparam speed.')
                self._is_parking = False
                return False
        value = self._device.kparameter_speed_max
        if value is not None:
            if not self._device.set_kparameter_speed(value):
                self.log(f'ERR:Failed to set {self.devname} kparam speed.')
                self._is_parking = False
                return False
        if not self.continue_execution():
            return False
        return True

    def _move_to_parked(self):
        self.log(f'Sending {self.devname} to parked position...')
        if not self.device.cmd_move_park():
            self.log(f'ERR:Failed to move {self.devname} to parked position.')
            self._is_parking = False
            return False
        return True


class MachineShutdown(_DeviceSet, LogCallback):
    """Machine Shutdown device."""

    DEFAULT_CHECK_TIMEOUT = 10
    DEFAULT_CONN_TIMEOUT = 5
    DEFAULT_TINYSLEEP = 0.1

    EG_FILA_CURR_STDBY = 1.1  # [A]
    EG_BIAS_VOLT_STDBY = -100  # [V]
    BORF_SLREF_STDBY = 62  # [mV]
    SIRF_SLREF_STDBY = 60  # [mV]
    EBEAM_MAX_CURRENT = 1  # [mA]

    def __init__(self, log_callback=None):
        """."""
        self._log_callback = log_callback
        self._abort = False

        self._devrefs = self._create_devices()
        devices = list(self._devrefs.values())
        _DeviceSet.__init__(self, devices, devname='AS-Glob:AP-MachShutdown')

        LogCallback.__init__(self, log_callback)

    def abort_execution(self):
        """Set abort execution flag."""
        self._abort = True

    def continue_execution(self):
        """Check whether to continue execution based on abort flag state."""
        if self._abort:
            self._abort = False
            self.log('ERR:Abort received.')
            for idn in ['apu22_06SB', 'apu22_07SP', 'apu22_08SB', 'apu22_09SA',
                        'apu58_11SP', 'delta52_10SB', 'papu50_17SA']:
                if self._devrefs[idn].is_parking:
                    self._devrefs[idn].abort_execution()
            return False
        return True

    def s01_close_gamma_shutter(self):
        """Try to close gamma shutter."""
        self.log('Step 01: Closing gamma shutter...')

        dev = self._devrefs['asmpsctrl']
        is_ok = dev.cmd_gamma_disable()
        if not is_ok:
            self.log('WARN:Could not close gamma shutter.')
            self.log('WARN:Continuing anyway...')
            return False

        self.log('Gamma Shutter closed.')
        return True

    def s02_macshift_update(self):
        """Change Machine Shift to Maintenance."""
        self.log('Step 02: Updating Machine Shift...')

        new_mode = 'Shutdown'

        machshift = self._devrefs['machshift']
        machshift.mode = new_mode

        is_ok = machshift.wait_mode(new_mode)
        if not is_ok:
            self.log('WARN:Could not change MachShift to Shutdown.')
            self.log('WARN:Continuing anyway...')
            return False

        self.log('Machine Shift updated.')
        return True

    def s03_injmode_update(self):
        """Change Injection Mode to Decay."""
        self.log('Step 03: Changing Injection Mode to Decay...')

        injctrl = self._devrefs['injctrl']

        new_injmode = 'Decay'

        injctrl.injmode = new_injmode
        is_ok = injctrl.wait_injmode(new_injmode)
        if not is_ok:
            self.log('ERR:Could not change InjMode to Decay.')
            return False

        self.log('InjMode changed to Decay.')
        return True

    def s04_injcontrol_disable(self):
        """Turn off injection system."""
        self.log('Step 04: Turning off Injection system...')

        self.log('Turning off EVG Injection table...')
        is_ok = self._devrefs['evg'].cmd_turn_off_injection(wait_rb=True)
        if not is_ok:
            self.log('ERR:Could not turn off Injection table.')
            return False

        if not self.continue_execution():
            return False

        self.log('...done. Turning off Egun trigger...')
        is_ok = self._devrefs['egtriggerps'].cmd_disable_trigger()
        if not is_ok:
            self.log('ERR:Could not turn off EGun trigger.')
            return False

        if not self.continue_execution():
            return False

        self.log('...done. Turning off injection system...')
        injctrl = self._devrefs['injctrl']
        injctrl.cmd_injsys_turn_off()
        injctrl.wait_injsys_cmd_finish(timeout=30)
        if not injctrl.check_injsys_cmd_completed():
            self.log('ERR:Could not turn off Injection system.')
            return False

        self.log('...done.')
        return True

    def s05_ids_parking(self):
        """Park IDs."""
        self.log('Step 05: Parking IDs...')

        self.log('Sending park command for IDs...')
        threads = list()
        for dev in self._devrefs.values():
            if isinstance(dev, IDParking):
                thread = ThreadWithReturnValue(
                    target=dev.cmd_park_device, daemon=True)
                thread.start()
                threads.append(thread)
        self.log('...waiting for parking...')
        all_ret = True
        for thread in threads:
            all_ret &= thread.join()
        self.log('...finished ID Parking routine.')
        if not all_ret:
            self.log('ERR:Could not park all IDs')
            return False

        self.log('All IDs parked.')
        return True

    def s06_sofb_fofb_turnoff(self):
        """Turn off orbit feedback loops."""
        self.log('Step 06: Turning off FOFB and SOFB...')

        self.log('Turning off FOFB loop...')
        is_ok = self._devrefs['fofb'].cmd_turn_off_loop_state(timeout=12)
        if not is_ok:
            self.log('ERR:Could not turn off FOFB loop.')
            return False  # TODO: do we want to abort procedure in this case?

        if not self.continue_execution():
            return False

        is_ok = self._devrefs['fofb'].cmd_corr_set_current_zero()
        if not is_ok:
            self.log('WARN:Could not set fast correctors to zero.')
            self.log('WARN:Continuing anyway...')
            # NOTE: we will not return False here because the correctors
            # will be set to zero also in the PS turn off procedure.

        self.log('...done. Turning off SOFB loop...')
        is_ok = self._devrefs['sofb'].cmd_turn_off_autocorr(timeout=5)
        if not is_ok:
            self.log('ERR:Could not turn off SOFB loop.')
            return False  # TODO: do we want to abort procedure in this case?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling SOFB Synchronization...')
        is_ok = self._devrefs['sofb'].cmd_turn_off_synckick(timeout=5)
        if not is_ok:
            self.log('WARN:Could not disable SOFB Synchronization.')
            self.log('WARN:Continuing anyway...')
            # NOTE: we will not return False here because the correctors
            # mode will be controlled also in the PS turn off procedure.

        self.log('...done.')
        return True

    def s07_bbb_turnoff(self):
        """Turn off BbB loops."""
        self.log('Step 07: Turning off BbB...')

        self.log('Disabling BbB loops...')

        devices = [
            self._devrefs[d] for d in ['bbbhfb', 'bbbvfb', 'bbblfb']]

        for dev in devices:
            dev.loop_state = 0

        if not self._wait_devices_propty(devices, 'FBCTRL', 0):
            self.log('WARN:Could not disable BbB loops.')
            self.log('WARN:Continuing anyway...')
        else:
            self.log('...done.')
        return True

    def s08_sirf_lower_voltage(self):
        """Lower SI RF voltage."""
        self.log('Step 08: Turning off SI RF...')

        llrf = self._devrefs['sillrf']

        self.log('Changing voltage increase rate to 2mV/s...')
        incrate = llrf.VoltIncRates.vel_2p0
        if not llrf.set_voltage_incrate(incrate, timeout=5):
            self.log('ERR:Could not set voltage increase rate to 2mV/s.')
            return False

        if not self.continue_execution():
            return False

        ref = self.SIRF_SLREF_STDBY
        self.log(f'...done. Changing loop reference to {ref}mV...')
        llrf.voltage = ref
        t0, timeout_flag = _time.time(), False
        while llrf.voltage_mon > ref:
            if _time.time() - t0 > 180:
                timeout_flag = True
            _time.sleep(0.1)
        if timeout_flag:
            self.log(f'ERR:Could not set loop reference to {ref}mV.')
            return False

        self.log('...done. Check if stored beam was dumped...')
        dcct = self._devrefs['dcct']
        if dcct.current > MachineShutdown.EBEAM_MAX_CURRENT:
            self.log('ERR:DCCT is indicating stored beam.')
            return False

        if not self.continue_execution():
            return False

        self.log('...done.')
        return True

    def s09_sidcct_check_beam_current(self):
        """Check bema current in SI."""

        self.log('Step 09: Check if stored beam was dumped...')
        dcct = self._devrefs['dcct']
        if dcct.current > MachineShutdown.EBEAM_MAX_CURRENT:
            self.log('ERR:DCCT is indicating stored beam.')
            return False

        if not self.continue_execution():
            return False

        self.log('...done.')
        return True

    def s10_sirf_turnoff(self):
        """Turn off SI RF."""
        self.log('Step 10: Turning off SI RF...')

        llrf = self._devrefs['sillrf']
        cavmon = self._devrefs['sicavmon']
        preamp1 = self._devrefs['sillrfpreamp1']
        preamp2 = self._devrefs['sillrfpreamp2']
        dcamp1 = self._devrefs['sirfdcamp1']
        dcamp2 = self._devrefs['sirfdcamp2']
        acamp1 = self._devrefs['sirfacamp1']
        acamp2 = self._devrefs['sirfacamp2']

        self.log('...done. Disabling slow loop control...')
        if not llrf.set_slow_loop_state(0):
            self.log('ERR:Could not disable LLRF slow loop.')
            return False
        _time.sleep(1.0)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling PinSw...')
        if not preamp1.cmd_disable_pinsw(wait_mon=True):
            self.log('ERR:Could not disable SSA1 PinSw.')
            return False
        if not preamp2.cmd_disable_pinsw(wait_mon=True):
            self.log('ERR:Could not disable SSA2 PinSw.')
            return False
        _time.sleep(1.0)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling DC/TDK amplifiers...')
        if not dcamp1.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA1 DC/TDK.')
            return False
        if not dcamp2.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA2 DC/TDK.')
            return False
        _time.sleep(1.0)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling AC/TDK amplifiers...')
        if not acamp1.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA1 AC/TDK.')
            return False
        if not acamp2.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA2 AC/TDK.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Checking if power forward is less than 1W...')
        if not self._wait_devices_propty(
                cavmon, 'PwrFwd-Mon', 1, comp='lt', timeout=10):
            self.log('ERR:Power forward is greater than 1W.')
            return False

        self.log('...done.')
        return True

    def s11_borf_turnoff(self):
        """Turn off BO RF."""
        self.log('Step 11: Turning off BO RF...')

        llrf = self._devrefs['bollrf']
        cavmon = self._devrefs['bocavmon']
        preamp = self._devrefs['bollrfpreamp']
        dcamp = self._devrefs['borfdcamp']
        vdcamp = self._devrefs['borf300vdcamp']

        self.log('Disabling BO RF Rmp...')
        if not llrf.set_rmp_enable(0, timeout=2):
            self.log('ERR:Could not disable BO RF Ramp.')
            return False

        if not self.continue_execution():
            return False

        ref = self.BORF_SLREF_STDBY
        self.log(f'...done. Changing loop reference to {ref}mV...')
        if not llrf.set_voltage(ref, timeout=60, wait_mon=False):
            self.log(f'ERR:Could not set loop reference to {ref}mV.')
            return False

        self.log('...done. Disabling slow loop control...')
        if not llrf.set_slow_loop_state(0):
            self.log('ERR:Could not disable LLRF slow loop.')
            return False
        _time.sleep(1.0)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling PinSw...')
        if not preamp.cmd_disable_pinsw(wait_mon=True):
            self.log('ERR:Could not disable SSA PinSw.')
            return False
        _time.sleep(0.5)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling DC/DC amplifier...')
        if not dcamp.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA DC/DC amplifier.')
            return False
        _time.sleep(0.5)  # is this necessary?

        if not self.continue_execution():
            return False

        self.log('...done. Disabling 300VDC amplifier...')
        if not vdcamp.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA 300VDC amplifier.')
            return False
        _time.sleep(0.5)  # is this necessary?

        self.log('...done. Checking if power forward is less than 1W...')
        if not self._wait_devices_propty(
                cavmon, 'PwrFwd-Mon', 1, comp='lt', timeout=10):
            self.log('ERR:Power forward is greater than 1W.')
            return False

        self.log('...done.')
        return True

    def s12_modulators_turnoff(self):
        """Turn off modulators."""
        self.log('Step 12: Turning off modulators...')

        devs = (self._devrefs['limod1'], self._devrefs['limod2'])

        self.log('Disabling CHARGE...')
        self._set_devices_propty(devs, 'CHARGE', 0)
        if not self._wait_devices_propty(devs, 'CHARGE', 0):
            self.log('ERR:Could not disable Modulators CHARGE.')
            return False

        _time.sleep(1.0)

        self.log('...done. Disabling TRIGOUT...')
        self._set_devices_propty(devs, 'TRIGOUT', 0)
        if not self._wait_devices_propty(devs, 'TRIGOUT', 0):
            self.log('ERR:Could not disable Modulators TRIGOUT.')
            return False

        self.log('...done.')
        return True

    def s13_adjust_egun_bias(self):
        """Adjust Bias Voltage to standby value."""
        self.log('Step 13: Adjusting EGun bias voltage...')

        injctrl = self._devrefs['injctrl']

        volt = self.EG_BIAS_VOLT_STDBY
        self.log(f'Setting bias voltage to {volt}V...')
        if injctrl.injtype_str == 'SingleBunch':
            injctrl.bias_volt_sglbun = volt
        else:
            injctrl.bias_volt_multbun = volt
        injctrl.wait_bias_volt_cmd_finish(timeout=10)
        return True

    def s14_adjust_egun_filament(self):
        """Adjust EGun Bias Filament current to standby value."""
        self.log('Step 14: Adjusting EGun Bias Filament current...')

        injctrl = self._devrefs['injctrl']
        egfila = self._devrefs['egfila']

        curr = self.EG_FILA_CURR_STDBY
        self.log(f'Setting Bias Filament current to {curr:.1}A...')
        injctrl.filacurr_opvalue = curr
        injctrl.wait_filacurr_cmd_finish(timeout=10)
        if not egfila.wait_current(curr, timeout=1):
            self.log('WARN:Could not adjust EGun filament.')
            self.log('WARN:Continuing anyway...')
        else:
            self.log('...done.')
        return True

    def s15_disable_egun_highvoltage(self):
        """Disable egun high voltage."""
        self.log('Step 15: Disabling EGun high voltage...')

        injctrl = self._devrefs['injctrl']
        eghv = self._devrefs['eghvolt']

        self.log('Setting EGun High Voltage to 0V...')
        injctrl.hvolt_opvalue = 0.0
        injctrl.wait_hvolt_cmd_finish(timeout=100)
        if not eghv.wait_voltage(0, timeout=1):
            self.log('ERR:Timed out waiting for egun high voltage.')
            return False

        if not self.continue_execution():
            return False

        self.log('...done. Disabling EGun High Voltage Enable State...')
        if not eghv.cmd_turn_off(timeout=5):
            self.log('ERR:Could not disable egun high voltage.')
            return False

        self.log('...done.')
        return True

    def s16_start_counter(self):
        """Check whether the countdown to tunnel access has started."""
        self.log('Step 16: Checking tunnel access countdown...')

        timeout = 5  # [s]
        dev = self._devrefs['asppsctrl']
        time0 = _time.time()
        value_init = round(dev.tunnel_access_wait_time_left)
        while True:
            value = round(dev.tunnel_access_wait_time_left)
            if value < value_init:
                # countdown is running!
                break
            if _time.time() - time0 > timeout:
                self.log('ERR:PPS Timer has not started countdown.')
                return False

        self.log('...done.')
        return True

    def s17_disable_ps_triggers(self):
        """Disable PS triggers."""
        self.log('Step 17: Disabling PS triggers...')
        return self._disable_ps_triggers('PS')

    def s18_run_ps_turn_off_procedure(self):
        """Do turn off PS procedure."""
        self.log('Step 18: Executing Turn Off PS...')
        return self._exec_ps_turnoff('PS')

    def s19_disable_pu_triggers(self):
        """Disable PU triggers."""
        self.log('Step 19: Disabling PU triggers...')
        return self._disable_ps_triggers('PU')

    def s20_run_pu_turn_off_procedure(self):
        """Do turn off PU procedure."""
        self.log('Step 20: Executing Turn Off PU...')
        return self._exec_ps_turnoff('PU')

    def execute_procedure(self):
        """Execute machine shutdown procedure."""
        # NOTE: true_needed=True for procedures whose fails
        # are impeditive to proceed with the machine shutdown.
        steps = (
            # procedure method name, true_needed
            (self.s01_close_gamma_shutter, False),
            (self.s02_macshift_update, False),
            (self.s03_injmode_update, False),
            (self.s04_injcontrol_disable, True),
            (self.s05_ids_parking, False),
            (self.s06_sofb_fofb_turnoff, True),
            (self.s07_bbb_turnoff, True),
            (self.s08_sirf_lower_voltage, False)
            (self.s09_sidcct_check_beam_current, True),
            (self.s10_sirf_turnoff, True),
            (self.s11_borf_turnoff, True),
            (self.s12_modulators_turnoff, True),
            (self.s13_adjust_egun_bias, True),
            # (self.s14_adjust_egun_filament, True),  # EPP demand
            (self.s15_disable_egun_highvoltage, True),
            (self.s16_start_counter, True),
            (self.s17_disable_ps_triggers, True),
            (self.s18_run_ps_turn_off_procedure, False),
            (self.s19_disable_pu_triggers, False),
            (self.s20_run_pu_turn_off_procedure, False),
        )
        for i, step in enumerate(steps):
            cmd, needs_true = step
            state = cmd()
            if needs_true and state is not True:
                self.log(f'ERR:Could not complete, failed in step {i:02}.')
                return False
            if not self.continue_execution():
                self.log('ERR:Could not complete, abort received.')
                return False
        self.log('Final Step: Wait for tunnel access to be released.')
        return True

    def _create_devices(self):
        """."""
        devices = dict()

        # MachShift
        devices['machshift'] = _MachShift()

        # InjCtrl
        devices['injctrl'] = _InjCtrl(
            props2init=(
                'Mode-Sel', 'Mode-Sts', 'Type-Sts',
                'InjSysTurnOff-Cmd', 'InjSysCmdSts-Mon',
                'InjSysCmdDone-Mon', 'InjSysTurnOffOrder-RB',
                'SglBunBiasVolt-SP', 'SglBunBiasVolt-RB',
                'MultBunBiasVolt-SP', 'MultBunBiasVolt-RB',
                'FilaOpCurr-SP', 'FilaOpCurr-RB',
                'HVOpVolt-SP', 'HVOpVolt-RB',
                'BiasVoltCmdSts-Mon', 'FilaOpCurrCmdSts-Mon',
                'HVOpVoltCmdSts-Mon',
            ))

        # EVG
        devices['evg'] = _EVG(
            props2init=('InjectionEvt-Sel', 'InjectionEvt-Sts'))

        # EGun
        devices['egtriggerps'] = _EGTriggerPS(
            props2init=('enable', 'enablereal'))
        devices['egfila'] = _EGFilament(
            props2init=('currentinsoft', ))
        devices['eghvolt'] = _EGHVPS(
            props2init=(
                'voltinsoft', 'enable', 'enstatus', 'switch', 'swstatus'))

        # Interlock
        devices['asppsctrl'] = _ASPPSCtrl()
        devices['asmpsctrl'] = _ASMPSCtrl(
            props2init=('DsblGamma-Cmd', 'AlarmGammaShutter-Mon'))

        # IDs
        devices['apu22_06SB'] = IDParking(
            _ID.DEVICES.APU.APU22_06SB, log_callback=self._log_callback)
        devices['apu22_07SP'] = IDParking(
            _ID.DEVICES.APU.APU22_07SP, log_callback=self._log_callback)
        devices['apu22_08SB'] = IDParking(
            _ID.DEVICES.APU.APU22_08SB, log_callback=self._log_callback)
        devices['apu22_09SA'] = IDParking(
            _ID.DEVICES.APU.APU22_09SA, log_callback=self._log_callback)
        devices['apu58_11SP'] = IDParking(
            _ID.DEVICES.APU.APU58_11SP, log_callback=self._log_callback)
        devices['delta52_10SB'] = IDParking(
            _ID.DEVICES.DELTA.DELTA52_10SB, log_callback=self._log_callback)
        devices['papu50_17SA'] = IDParking(
            _ID.DEVICES.PAPU.PAPU50_17SA, log_callback=self._log_callback)

        # SOFB
        devices['fofb'] = _HLFOFB(
            props2init=(
                'LoopState-Sel', 'LoopState-Sts',
                'CorrSetCurrZero-Cmd', 'CorrSetCurrZeroDuration-RB',
            ))

        # FOFB
        devices['sofb'] = _SOFB(
            _SOFB.DEVICES.SI,
            props2init=(
                'LoopState-Sel', 'LoopState-Sts',
                'CorrSync-Sel', 'CorrSync-Sts',
            ))

        # BbB
        devices['bbbhfb'] = _BbBFB(
            _BbB.DEVICES.H, props2init=('FBCTRL', ))
        devices['bbbvfb'] = _BbBFB(
            _BbB.DEVICES.V, props2init=('FBCTRL', ))
        devices['bbblfb'] = _BbBFB(
            _BbB.DEVICES.L, props2init=('FBCTRL', ))

        # RF
        devices['sillrf'] = _ASLLRF(
            _ASLLRF.DEVICES.SI,
            props2init=(
                'AMPREF:INCRATE:S', 'AMPREF:INCRATE', 'SL', 'SL:S',
                'SL:INP:AMP', 'SL:REF:AMP', 'mV:AL:REF-SP', 'mV:AL:REF-RB',
            ))
        devices['sicavmon'] = _SIRFCavMonitor()
        devices['sillrfpreamp1'] = _SILLRFPreAmp(_SILLRFPreAmp.DEVICES.SSA1)
        devices['sillrfpreamp2'] = _SILLRFPreAmp(_SILLRFPreAmp.DEVICES.SSA2)
        devices['sirfdcamp1'] = _SIRFDCAmp(_SIRFDCAmp.DEVICES.SSA1)
        devices['sirfdcamp2'] = _SIRFDCAmp(_SIRFDCAmp.DEVICES.SSA2)
        devices['sirfacamp1'] = _SIRFACAmp(_SIRFACAmp.DEVICES.SSA1)
        devices['sirfacamp2'] = _SIRFACAmp(_SIRFACAmp.DEVICES.SSA2)

        devices['bollrf'] = _ASLLRF(
            _ASLLRF.DEVICES.BO,
            props2init=(
                'RmpEnbl-Sel', 'RmpEnbl-Sts', 'RmpReady-Mon', 'SL', 'SL:S',
                'SL:INP:AMP', 'SL:REF:AMP', 'mV:AL:REF-SP', 'mV:AL:REF-RB',

            ))
        devices['bocavmon'] = _BORFCavMonitor()
        devices['bollrfpreamp'] = _BOLLRFPreAmp()
        devices['borfdcamp'] = _BORFDCAmp()
        devices['borf300vdcamp'] = _BORF300VDCAmp()

        # DCCT
        devices['dcct'] = _DCCT(
            _DCCT.DEVICES.SI_14C4, props2init=('StoredEBeam-Mon', ))

        # Linac Modulators
        devices['limod1'] = _LIModltr(
            _LIModltr.DEVICES.LI_MOD1, props2init=('CHARGE', 'TRIGOUT'))
        devices['limod2'] = _LIModltr(
            _LIModltr.DEVICES.LI_MOD2, props2init=('CHARGE', 'TRIGOUT'))

        # PS
        self._pstrigs = _HLTimeSearch.get_hl_triggers(filters={'dev': 'Mags'})
        devices['pstrigs'] = _PSTriggers(self._pstrigs)

        self._psnames = _PSSearch.get_psnames(
            dict(sec='(LI|TB|BO|TS|SI)', dis='PS'))
        self._psnames_fbp = [
            psn for psn in self._psnames if
            _PSSearch.conv_psname_2_psmodel(psn) == 'FBP']
        self._psnames_not_li = [
            psn for psn in self._psnames if 'LI-' not in psn]
        self._psnames_set_manual = [
            psn for psn in self._psnames if _PVName(psn).dev
            in ('FCH', 'FCV')]
        self._psnames_set_slowref = [
            psn for psn in self._psnames if
            _PVName(psn).dev not in ('FCH', 'FCV') and 'LI-' not in psn]
        for psn in self._psnames:
            devices[psn] = _PSTesterFactory.create(psn)

        dclinks_regatron = set()
        dclinks_not_regatron = set()
        for name in self._psnames:
            if 'LI' in name:
                continue
            dclinks = _PSSearch.conv_psname_2_dclink(name)
            if dclinks:
                dclink_model = _PSSearch.conv_psname_2_psmodel(dclinks[0])
                if dclink_model != 'REGATRON_DCLink':
                    dclinks_not_regatron.update(dclinks)
                else:
                    for dcl in dclinks:
                        dcl_typ = _PSSearch.conv_psname_2_pstype(dcl)
                        if dcl_typ == 'as-dclink-regatron-master':
                            dclinks_regatron.add(dcl)
        self._dclinks_regatron = list(dclinks_regatron)
        self._dclinks_not_regatron = list(dclinks_not_regatron)
        self._dclinks = list(dclinks_regatron | dclinks_not_regatron)
        for dcl in self._dclinks:
            devices[dcl] = _PSTesterFactory.create(dcl)

        # PU
        self._putrigs = _HLTimeSearch.get_hl_triggers(
            filters={'dev': '.*(Kckr|Sept).*'})
        devices['putrigs'] = _PSTriggers(self._putrigs)

        self._punames = _PSSearch.get_psnames({
            'sec': '(TB|BO|TS|SI)', 'dis': 'PU', 'dev': '.*(Kckr|Sept)',
            'propty_name': '(?!:CCoil).*'})
        for pun in self._punames:
            devices[pun] = _PSTesterFactory.create(pun)

        return devices

    def _disable_ps_triggers(self, devtype):
        """Desliga os triggers das fontes."""
        self.log(f'Disabling triggers for {devtype}...')

        trigdev = self._devrefs[f'{devtype.lower()}trigs']
        triggers = trigdev.triggers

        # send command to disable
        for trig in triggers.values():
            trig.state = 0

        # check if is disabled
        need_check = set(triggers)
        _t0 = _time.time()
        while _time.time() - _t0 < self.DEFAULT_CHECK_TIMEOUT:
            for trigname, trig in triggers.items():
                if trigname not in need_check:
                    continue
                if not trig.wait_for_connection(self.DEFAULT_CONN_TIMEOUT):
                    continue
                if trig.state == 0:
                    need_check.remove(trigname)
                if self._abort:
                    break
            if (not need_check) or (self._abort):
                break
            _time.sleep(self.DEFAULT_TINYSLEEP)
        if need_check:
            for trig in need_check:
                self.log(f'ERR:Failed to disable trigger {trig}')
            return False
        self.log('...done.')
        return True

    def _ps_command_set(
            self, devnames, method, description,
            conn_timeout=DEFAULT_CONN_TIMEOUT, **kwargs):
        """Set PS property."""
        devnames = set(devnames) - set(self._ps_failed)
        nrdevs = len(devnames)
        strf = 'Executed {} for {}/{}'
        done = 0
        for dev in devnames:
            tester = self._devrefs[dev]
            if not tester.wait_for_connection(conn_timeout):
                self.log(f'ERR:Failed to connect to {dev}')
                self._ps_failed.append(dev)
                continue
            func = getattr(tester, method)
            func(**kwargs)
            done += 1
            if done % 20 == 0:
                self.log(strf.format(description, done, nrdevs))
            if self._abort:
                break
        else:
            self.log(strf.format(description, done, nrdevs))
            return True
        self.log('ERR:Received abort during execution.')
        return False

    def _ps_command_check(
            self, devnames, method, description,
            conn_timeout=DEFAULT_CONN_TIMEOUT,
            check_timeout=DEFAULT_CHECK_TIMEOUT,
            tiny_sleep=DEFAULT_TINYSLEEP, **kwargs):
        """Check PS state."""
        devnames = set(devnames) - set(self._ps_failed)
        nrdevs = len(devnames)
        need_check = list(devnames)
        checked, checked_log = 0, 0

        strf = 'Done {} for {}/{}'

        _t0 = _time.time()
        while _time.time() - _t0 < check_timeout:
            for dev in devnames:
                if dev not in need_check:
                    continue
                tester = self._devrefs[dev]
                if not tester.wait_for_connection(conn_timeout):
                    continue
                func = getattr(tester, method)
                if func(**kwargs):
                    need_check.remove(dev)
                    checked = nrdevs - len(need_check)
                if (checked % 20 == 0 and checked_log < checked) \
                        or checked == nrdevs:
                    self.log(strf.format(description, checked, nrdevs))
                    checked_log = checked
                if self._abort:
                    break
            if (not need_check) or (self._abort):
                break
            _time.sleep(tiny_sleep)
        if self._abort:
            self.log('ERR:Received abort during checks.')
            return False
        if need_check:
            for dev in need_check:
                self._ps_failed.append(dev)
                self.log(f'ERR:Failed to execute {description} for {dev}')
            return False
        return True

    def _exec_ps_turnoff(self, devtype):
        ps_turnoff = {
            'Check communication': [
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames + self._dclinks,
                    'method': 'check_comm',
                    'block': True,
                },
            ],
            'Turn SOFBMode Off': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._psnames_fbp,
                    'method': 'set_sofbmode',
                    'kwargs': {'state': 'off'},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames_fbp,
                    'method': 'check_sofbmode',
                    'kwargs': {'state': 'off'},
                    'block': True,
                },
            ],
            'Set PS and DCLinks OpMode to SlowRef': [
                {
                    'func': self._ps_command_set,
                    'devnames':
                        self._psnames_set_slowref + self._dclinks_not_regatron,
                    'method': 'set_opmode',
                    'kwargs': {'state': _PSC.OpMode.SlowRef},
                },
                {
                    'func': self._ps_command_set,
                    'devnames': self._psnames_set_manual,
                    'method': 'set_opmode',
                    'kwargs': {'state': _PSC.OpModeFOFBSel.manual},
                },
                {
                    'func': self._ps_command_check,
                    'devnames':
                        self._psnames_set_slowref + self._dclinks_not_regatron,
                    'method': 'check_opmode',
                    'kwargs': {'state': [
                        _PSC.States.SlowRef, _PSC.States.Off,
                        _PSC.States.Interlock, _PSC.States.Initializing]},
                    'block': True,
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames_set_manual,
                    'method': 'check_opmode',
                    'kwargs': {'state': _PSC.OpModeFOFBSts.manual},
                    'block': True,
                },
            ],
            'Set PS Current to zero': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._psnames,
                    'method': 'set_current',
                    'kwargs': {'value': 0},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames,
                    'method': 'check_current',
                    'kwargs': {'value': 0, 'check_timeout': 50},
                    'block': True,
                },
            ],
            'Reset PS and DCLinks': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._psnames_not_li + self._dclinks,
                    'method': 'reset',
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames_not_li + self._dclinks,
                    'method': 'check_intlk',
                    'block': False,
                },
            ],
            'Turn PS PwrState Off': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._psnames,
                    'method': 'set_pwrstate',
                    'kwargs': {'state': 'off'},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._psnames,
                    'method': 'check_pwrstate',
                    'kwargs': {'state': 'off', 'check_timeout': 20},
                    'block': True,
                },
            ],
            'Turn DCLinks PwrState Off': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._dclinks,
                    'method': 'set_pwrstate',
                    'kwargs': {'state': 'off'},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._dclinks,
                    'method': 'check_pwrstate',
                    'kwargs': {'state': 'off', 'check_timeout': 20},
                    'block': True,
                },
            ],
        }

        pu_turnoff = {
            'Set PU Voltage to zero': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._punames,
                    'method': 'set_voltage',
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._punames,
                    'method': 'check_voltage',
                    'kwargs': {'check_timeout': 240},
                    'block': True,
                },
            ],
            'Reset PU': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._punames,
                    'method': 'reset',
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._punames,
                    'method': 'check_intlk',
                    'block': False,
                },
            ],
            'Disable PU Pulse': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._punames,
                    'method': 'set_pulse',
                    'kwargs': {'state': 'off'},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._punames,
                    'method': 'check_pulse',
                    'kwargs': {'state': 'off'},
                    'block': True,
                },
            ],
            'Turn PU Off': [
                {
                    'func': self._ps_command_set,
                    'devnames': self._punames,
                    'method': 'set_pwrstate',
                    'kwargs': {'state': 'off'},
                },
                {
                    'func': self._ps_command_check,
                    'devnames': self._punames,
                    'method': 'check_pwrstate',
                    'kwargs': {'state': 'off', 'check_timeout': 20},
                    'block': True,
                },
            ],
        }

        procedure = ps_turnoff if devtype == 'PS' else \
            pu_turnoff if devtype == 'PU' else None
        if procedure is None:
            raise ValueError(f'procedure not defined for devtype {devtype}')

        self._ps_failed = list()
        interrupt = False
        for description, cmdlist in procedure.items():
            for cmd in cmdlist:
                func = cmd['func']
                devnames = cmd['devnames']
                method = cmd['method']
                kwargs = cmd.get('kwargs', dict())
                block = cmd.get('block', None)
                ret = func(devnames, method, description, **kwargs)
                if not ret and block:
                    interrupt = True
                    break
            if interrupt:
                self.log(f'ERR:Turn Off Procedure failed for {devtype}.')
                self.log('ERR:Verify errors before continue.')
                break
            if not self.continue_execution():
                break
        if self._ps_failed:
            for psn in self._ps_failed:
                self.log(f'ERR:Verify {psn}.')
            return False
        return True


if __name__ == '__main__':
    """."""
    ms = MachineShutdown()
    if ms.execute_procedure():
        print('machine shutdown success')
    else:
        print('machine shutdown failed')
