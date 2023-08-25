#!/usr/bin/env python-sirius
"""Machine shutdown script."""

import time as _time
import logging as _log
from threading import Thread as _Thread

from siriuspy.callbacks import Callback as _Callback
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch as _PSSearch, \
    HLTimeSearch as _HLTimeSearch
from siriuspy.pwrsupply.csdev import Const as _PSC
from siriuspy.devices import Devices as _Devices, \
    ASMPSCtrl as _ASMPSCtrl, ASPPSCtrl as _ASPPSCtrl, \
    APU as _APU, EPU as _EPU, PAPU as _PAPU, \
    MachShift as _MachShift, InjCtrl as _InjCtrl, \
    EVG as _EVG, EGTriggerPS as _EGTriggerPS, \
    EGFilament as _EGFilament, EGHVPS as _EGHVPS, \
    HLFOFB as _HLFOFB, SOFB as _SOFB, \
    ASLLRF as _ASLLRF, \
    SILLRFPreAmp as _SILLRFPreAmp, BOLLRFPreAmp as _BOLLRFPreAmp, \
    SIRFDCAmp as _SIRFDCAmp, BORFDCAmp as _BORFDCAmp, \
    SIRFACAmp as _SIRFACAmp, BORF300VDCAmp as _BORF300VDCAmp, \
    DCCT as _DCCT, LIModltr as _LIModltr
from siriuspy.devices.pstesters import \
    Triggers as _PSTriggers, PSTesterFactory as _PSTesterFactory
from siriuspy.devices.bbb import Feedback as _BbBFB, \
    BunchbyBunch as _BbB


# Configure Logging
_log.basicConfig(
    format='%(levelname)7s | %(asctime)s ::: %(message)s',
    datefmt='%F %T', level=_log.INFO, filemode='a')


class LogCallback(_Callback):
    """Base class for logging using callbacks."""

    def __init__(self, log_callback=None):
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


class IDParking(_Devices, LogCallback):
    """ID."""

    TIMEOUT_WAIT_FOR_CONNECTION = 5.0  # [s]

    def __init__(self, devname, log_callback=None):
        """Init."""
        if 'EPU' in devname:
            device = _EPU(devname)
        elif 'PAPU' in devname:
            device = _PAPU(devname)
        elif 'APU' in devname:
            device = _APU(devname)
        else:
            raise ValueError('Invalid ID device type')
        self._device = device

        _Devices.__init__(self, devname, [device, ])
        LogCallback.__init__(self, log_callback)

    def cmd_park_device(self):
        """Park ID."""
        # check connections
        self.log('check connections...')
        if not self._device.wait_for_connection(
                timeout=IDParking.TIMEOUT_WAIT_FOR_CONNECTION):
            return False

        # Desabilita a movimentação dos IDs pelas linhas.
        self.log('disable beamline controls...')
        if not self._device.cmd_beamline_ctrl_disable():
            return False

        # Para a movimentação dos IDs
        self.log('cmd move stop...')
        if not self._device.cmd_move_stop():
            return False

        # Seta as velocidades de Phase e Gap
        self.log('cmd set speeds...')
        value = self._device.phase_speed_max
        if not self._device.set_phase_speed(value):
            return False
        if isinstance(self._device, _EPU):
            value = self._device.gap_speed_max
            if not self._device.set_gap_speed(value):
                return False

        # Seta os IDs para config de estacionamento
        self.log('cmd set phase and gap for parking...')
        value = self._device.phase_parked
        if not self._device.set_phase(value):
            return False
        if isinstance(self._device, _EPU):
            value = self._device.gap_parked
        if not self._device.set_gap(value):
            return False

        # Movimenta os IDs para a posição escolhida
        self.log('cmd move to parking...')
        if not self._device.cmd_move_start():
            return False
        _time.sleep(2.0)  # aguarda 2 seg.

        # wait for end of movement of timeout
        self.log('wait end of movement...')
        timeout, sleep = 70, 0.2  # [s]
        t0 = _time.time()
        while self._device.is_moving:
            if _time.time() - t0 > timeout:
                return False
            _time.sleep(sleep)

        return True


class MachineShutdown(_Devices, LogCallback):
    """Machine Shutdown device."""

    # TODO: verify which steps we want to keep bloking procedure execution

    DEFAULT_CHECK_TIMEOUT = 10
    DEFAULT_CONN_TIMEOUT = 5
    DEFAULT_TINYSLEEP = 0.1

    def __init__(self, log_callback=None):
        self._abort = False

        self._devrefs = self._create_devices()
        devices = list(self._devrefs.values())
        _Devices.__init__(self, 'AS-Glob:AP-MachShutdown', devices)

        self._log_callback = log_callback
        LogCallback.__init__(self, log_callback)

    def continue_execution(self):
        """Check whether to continue execution based on abort flag state."""
        if self._abort:
            self._abort = False
            return False
        return True

    def s01_close_gamma_shutter(self):
        """Try to close gamma shutter."""
        self.log('Step 01: Closing gamma shutter...')

        dev = self._devrefs['asmpsctrl']
        is_ok = dev.cmd_gamma_disable()
        if not is_ok:
            self.log('WARN:Could not close gamma shutter.')
        else:
            self.log('Gamma Shutter closed.')
        # NOTE: we will return True here once this is not
        # impeditive to dump the beam and proceed with the
        # machine shutdown.
        return True

    def s02_macshift_update(self):
        """Change Machine Shift to Maintenance."""
        self.log('Step 02: Updating Machine Shift...')

        new_mode = 'Maintenance'

        machshift = self._devrefs['machshift']
        machshift.mode = new_mode

        is_ok = machshift.wait_mode(new_mode)
        if not is_ok:
            self.log('WARN:Could not change MachShift to Maintenance.')
        else:
            self.log('Machine Shift updated.')
        # NOTE: we will return True here once this is not
        # impeditive to dump the beam and proceed with the
        # machine shutdown.
        return True

    def s03_injmode_update(self):
        """Change Injection Mode to Decay."""
        self.log('Step 03: Changing Injection Mode to Decay...')

        injctrl = self._devrefs['injctrl']

        new_injmode = 'Decay'

        injctrl.injmode = new_injmode
        is_ok = injctrl.wait_injmode(new_injmode)
        if not is_ok:
            self.log('WARN:Could not change InjMode to Decay.')
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

        self.log('...done. Turning off Egun trigger...')
        is_ok = self._devrefs['egtriggerps'].cmd_disable_trigger()
        if not is_ok:
            self.log('ERR:Could not turn off EGun trigger.')
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

        ids = [
            'apu22_06SB', 'apu22_07SP', 'apu22_08SB', 'apu22_09SA',
            'apu58_11SP', 'epu50_10SB', 'papu50_17SA',
        ]
        self.log('Sending park command for IDs...')
        threads = list()
        for idref in ids:
            dev = self._devrefs[idref]
            thread = _Thread(target=dev.cmd_park_device, daemon=True)
            thread.start()
            threads.append(thread)
        self.log('...waiting for parking...')
        for thread in threads:
            thread.join()
        self.log('...finished ID Parking routine.')

        # NOTE: once we do not want this step block the machine shutdown
        # script in case of problems, we do not need to return False in
        # case of any False return.
        return True

    def s06_sofb_fofb_turnoff(self):
        """Turn off orbit feedback loops."""
        self.log('Step 06: Turning off FOFB and SOFB...')

        self.log('Turning off FOFB loop...')
        is_ok = self._devrefs['fofb'].cmd_turn_off_loop_state(timeout=12)
        if not is_ok:
            self.log('ERR:Could not turn off FOFB loop.')
            return False

        self.log('...done. Turning off SOFB loop...')
        is_ok = self._devrefs['sofb'].cmd_turn_off_autocorr(timeout=5)
        if not is_ok:
            self.log('ERR:Could not turn off SOFB loop.')
            return False

        self.log('...done. Disabling SOFB Synchronization...')
        is_ok = self._devrefs['sofb'].cmd_turn_off_synckick(timeout=5)
        if not is_ok:
            self.log('ERR:Could not disable SOFB Synchronization.')
            # NOTE: we will not return False here because the correctors
            # mode will be controlled also in the PS turn of procedure.

        return True

    def s07_bbb_turnoff(self):
        """Turn off BbB loops."""
        self.log('Step 07: Turning off BbB...')

        self.log('Disabling BbB loops...')

        self._defrefs['bbbhfb'].loop_state = 0
        self._defrefs['bbbvfb'].loop_state = 0
        self._defrefs['bbblfb'].loop_state = 0

        is_ok = \
            self._defrefs['bbbhfb'].loop_state == 0 and \
            self._defrefs['bbbvfb'].loop_state == 0 and \
            self._defrefs['bbblfb'].loop_state == 0
        if not is_ok:
            self.log('ERR:Could not disable BbB loops.')
            return False
        self.log('...done.')
        return True

    def s08_sirf_turnoff(self):
        """Turn off SI RF."""
        self.log('Step 08: Turning off SI RF...')

        llrf = self._devrefs['sillrf']
        preamp = self._devrefs['sillrfpreamp']
        dcamp1 = self._devrefs['sirfdcamp1']
        dcamp2 = self._devrefs['sirfdcamp2']
        acamp1 = self._devrefs['sirfacamp1']
        acamp2 = self._devrefs['sirfacamp2']

        self.log('Changing voltage increase rate to 2mV/s...')
        incrate = llrf.VoltIncRates.vel_2p0
        llrf.voltage_incrate = incrate
        if not self.wait_voltage_incrate(incrate, timeout=5):
            self.log('ERR:Could not set voltage increase rate to 2mV/s.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Changing loop reference to 60mV...')
        if not llrf.set_voltage(60, timeout=180, wait_mon=False):
            self.log('ERR:Could not set loop reference to 60mV.')
            return False

        self.log('...done. Check if stored beam was dumped...')
        dcct = self._devrefs['dcct']
        if dcct.is_beam_stored:
            self.log('ERR:DCCT is indicating stored beam.')
            return False

        self.log('...done. Disabling slow loop control...')
        if not llrf.set_slow_loop_state(0):
            self.log('ERR:Could not disable LLRF slow loop.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Disabling PinSw...')
        if not preamp.cmd_disable_pinsw_1(wait_mon=True):
            self.log('ERR:Could not disable SSA1 PinSw.')
            return False
        if not preamp.cmd_disable_pinsw_2(wait_mon=True):
            self.log('ERR:Could not disable SSA2 PinSw.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Disabling DC/TDK amplifiers...')
        if not dcamp1.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA1 DC/TDK.')
            return False
        if not dcamp2.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA2 DC/TDK.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Disabling AC/TDK amplifiers...')
        if not acamp1.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA1 AC/TDK.')
            return False
        if not acamp2.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA2 AC/TDK.')
            return False
        _time.sleep(1.0)  # is this necessary?

        return True

    def s09_borf_turnoff(self):
        """Turn off BO RF."""
        self.log('Step 09: Turning off BO RF...')

        llrf = self._devrefs['bollrf']
        preamp = self._devrefs['bollrfpreamp']
        dcamp = self._devrefs['borfdcamp']
        vdcamp = self._devrefs['borf300vdcamp']

        self.log('Disabling BO RF Rmp...')
        if not llrf.set_rmp_enable(0, timeout=2):
            self.log('ERR:Could not disable BO RF Ramp.')
            return False
        _time.sleep(2.0)  # is this necessary?

        self.log('...done. Disabling slow loop control...')
        if not llrf.set_slow_loop_state(0):
            self.log('ERR:Could not disable LLRF slow loop.')
            return False
        _time.sleep(1.0)  # is this necessary?

        self.log('...done. Disabling PinSw...')
        if not preamp.cmd_disable_pinsw(wait_mon=True):
            self.log('ERR:Could not disable SSA PinSw.')
            return False
        _time.sleep(0.5)  # is this necessary?

        self.log('...done. Disabling DC/DC amplifier...')
        if not dcamp.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA DC/DC amplifier.')
            return False
        _time.sleep(0.5)  # is this necessary?

        self.log('...done. Disabling 300VDC amplifier...')
        if not vdcamp.cmd_disable(wait_mon=True):
            self.log('ERR:Could not disable SSA 300VDC amplifier.')
            return False
        _time.sleep(0.5)  # is this necessary?

        return True

    def s10_modulators_turnoff(self):
        """Turn off modulators."""
        self.log('Step 10: Turning off modulators...')

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

    def s11_adjust_egunbias(self):
        """Adjust Bias Voltage to -100V."""
        self.log('Step 11: Adjusting EGun bias voltage...')

        injctrl = self._devrefs['injctrl']

        self.log('Setting bias voltage to -100V...')
        if injctrl.injtype_str == 'SingleBunch':
            injctrl.bias_volt_sglbun = -100.0
        else:
            injctrl.bias_volt_multbun = -100.0
        injctrl.wait_bias_volt_cmd_finish(timeout=10)
        return True

    def s12_adjust_egunfilament(self):
        """Adjust EGun Bias Filament current."""
        self.log('Step 12: Adjusting EGun Bias Filament current...')

        injctrl = self._devrefs['injctrl']
        egfila = self._devrefs['egfila']

        self.log('Setting Bias Filament current to 1.1A...')
        injctrl.filacurr_opvalue = 1.1
        injctrl.wait_filacurr_cmd_finish(timeout=10)
        if not egfila.wait_current(1.1, timeout=1):
            self.log('ERR:Could not adjust EGun filament.')
            return False

        self.log('...done.')
        return True

    def s13_disable_egun_highvoltage(self):
        """Disable egun high voltage."""
        self.log('Step 13: Disabling EGun high voltage...')

        injctrl = self._devrefs['injctrl']
        eghv = self._devrefs['eghvolt']

        self.log('Setting EGun High Voltage to 0V...')
        injctrl.hvolt_opvalue = 0.0
        injctrl.wait_hvolt_cmd_finish(timoeut=100)
        if not eghv.wait_voltage(0, timeout=1):
            self.log('ERR:Timed out waiting for egun high voltage.')
            return False

        self.log('...done. Disabling EGun High Voltage Enable State...')
        if not eghv.cmd_turn_off(timoeut=5):
            self.log('ERR:Could not disable egun high voltage')
            return False

        self.log('...done.')
        return True

    def s14_start_counter(self):
        """Check whether the countdown to tunnel access has started."""
        self.log('Step 14: Checking tunnel access countdown...')

        msg = (
            'Check whether the countdown to tunnel access has started.')
        input(msg)
        # dev = self._devrefs['asppsctrl']
        # if dev.time_left_to_tunnel_access() == 360:
        #     return False

        return True

    def s15_disable_ps_triggers(self):
        """Disable PS triggers."""
        self.log('Step 15: Disabling PS triggers...')
        return self._disable_ps_triggers('PS')

    def s16_run_ps_turn_off_procedure(self):
        """Do turn off PS procedure."""
        self.log('Step 16: Executing Turn Off PS...')
        return self._exec_ps_turnoff('PS')

    def s17_disable_pu_triggers(self):
        """Disable PU triggers."""
        self.log('Step 17: Disabling PU triggers...')
        return self._disable_ps_triggers('PU')

    def s18_run_pu_turn_off_procedure(self):
        """Do turn off PU procedure."""
        self.log('Step 18: Executing Turn Off PU...')
        return self._exec_ps_turnoff('PU')

    def s19_free_access(self):
        """Wait for tunnel access to be allowed."""
        self.log('Final Step: Wait for tunnel access to be released...')
        input()

    def execute_procedure(self):
        """Executa na sequência os passos a seguir."""
        if not self.s01_close_gamma_shutter():
            return False
        if not self.s02_macshift_update():
            return False
        if not self.s03_injmode_update():
            return False
        if not self.s04_injcontrol_disable():
            return False
        if not self.s05_ids_parking():
            return False
        if not self.s06_sofb_fofb_turnoff():
            return False
        if not self.s07_bbb_turnoff():
            return False
        if not self.s08_sirf_turnoff():
            return False
        if not self.s09_borf_turnoff():
            return False
        if not self.s10_modulators_turnoff():
            return False
        if not self.s11_adjust_egunbias():
            return False
        if not self.s12_adjust_egunfilament():
            return False
        if not self.s13_disable_egun_highvoltage():
            return False
        if not self.s14_start_counter():
            return False
        if not self.s15_disable_ps_triggers():
            return False
        if not self.s16_run_ps_turn_off_procedure():
            return False
        if not self.s17_disable_pu_triggers():
            return False
        if not self.s18_run_pu_turn_off_procedure():
            return False
        self.s19_free_access()
        return True

    def _create_devices(self):
        """."""
        devices = dict()

        # MachShift
        devices['machshift'] = _MachShift()

        # InjCtrl
        devices['injctrl'] = _InjCtrl()

        # EVG
        devices['evg'] = _EVG()

        # EGun
        devices['egtriggerps'] = _EGTriggerPS()
        devices['egfila'] = _EGFilament()
        devices['eghvolt'] = _EGHVPS()

        # Interlock
        devices['asppsctrl'] = _ASPPSCtrl()
        devices['asmpsctrl'] = _ASMPSCtrl()

        # IDs
        devices['apu22_06SB'] = IDParking(
            _APU.DEVICES.APU22_06SB, log_callback=self._log_callback)
        devices['apu22_07SP'] = IDParking(
            _APU.DEVICES.APU22_07SP, log_callback=self._log_callback)
        devices['apu22_08SB'] = IDParking(
            _APU.DEVICES.APU22_08SB, log_callback=self._log_callback)
        devices['apu22_09SA'] = IDParking(
            _APU.DEVICES.APU22_09SA, log_callback=self._log_callback)
        devices['apu58_11SP'] = IDParking(
            _APU.DEVICES.APU58_11SP, log_callback=self._log_callback)
        devices['epu50_10SB'] = IDParking(
            _EPU.DEVICES.EPU50_10SB, log_callback=self._log_callback)
        devices['papu50_17SA'] = IDParking(
            _PAPU.DEVICES.PAPU50_17SA, log_callback=self._log_callback)

        # SOFB
        devices['fofb'] = _HLFOFB()

        # FOFB
        devices['sofb'] = _SOFB(_SOFB.DEVICES.SI)

        # BbB
        devices['bbbhfb'] = _BbBFB(_BbB.DEVICES.H)
        devices['bbbvfb'] = _BbBFB(_BbB.DEVICES.V)
        devices['bbblfb'] = _BbBFB(_BbB.DEVICES.L)

        # RF
        devices['sillrf'] = _ASLLRF(_ASLLRF.DEVICES.SI)
        devices['sillrfpreamp'] = _SILLRFPreAmp(_SILLRFPreAmp.DEVICES.SSA)
        devices['sirfdcamp1'] = _SIRFDCAmp(_SIRFDCAmp.DEVICES.SSA1)
        devices['sirfdcamp2'] = _SIRFDCAmp(_SIRFDCAmp.DEVICES.SSA2)
        devices['sirfacamp1'] = _SIRFACAmp(_SIRFACAmp.DEVICES.SSA1)
        devices['sirfacamp2'] = _SIRFACAmp(_SIRFACAmp.DEVICES.SSA2)
        devices['bollrf'] = _ASLLRF(_ASLLRF.DEVICES.BO)
        devices['bollrfpreamp'] = _BOLLRFPreAmp(_BOLLRFPreAmp.DEVICES.SSA)
        devices['borfdcamp'] = _BORFDCAmp(_BORFDCAmp.DEVICES.SSA)
        devices['borf300vdcamp'] = _BORF300VDCAmp(_BORF300VDCAmp.DEVICES.SSA)

        # DCCT
        devices['dcct'] = _DCCT(_DCCT.DEVICES.SI_14C4)

        # Linac Modulators
        devices['limod1'] = _LIModltr(_LIModltr.DEVICES.LI_MOD1)
        devices['limod2'] = _LIModltr(_LIModltr.DEVICES.LI_MOD2)

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
            for trig in triggers.values():
                if trig not in need_check:
                    continue
                if not trig.wait_for_connection(self.DEFAULT_CONN_TIMEOUT):
                    continue
                if trig.state == 0:
                    need_check.remove(trig)
                if self._abort:
                    break
            if (not need_check) or (self._abort):
                break
            _time.sleep(self.DEFAULT_TINYSLEEP)
        if need_check:
            for trig in need_check:
                self.log(f'ERR:Failed to disable trigger {trig}')
            return False
        return True

    def _ps_command_set(
            self, devnames, method, description,
            conn_timeout=DEFAULT_CONN_TIMEOUT, **kwargs):
        """Set PS property."""
        nrdevs = len(devnames)
        strf = 'Executed {} for {}/{}'
        done = 0
        for dev in devnames:
            if dev in self._ps_failed:
                continue
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
        self.log(strf.format(description, done, nrdevs))
        return True

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
                    'kwargs': {'check_timeout': 60},
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
                self.log('ERR:Turn Off Procedure failed for {devtype}.')
                self.log('ERR:Verify errors before continue.')
                break
            if not self.continue_execution():
                self.log('ERR:Abort received, interrupting.')
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
