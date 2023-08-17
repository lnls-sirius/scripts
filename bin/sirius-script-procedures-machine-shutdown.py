#!/usr/bin/env python-sirius
"""Machine shutdown script."""

import time as _time
import logging as _log

import epics as _epics

from siriuspy.callbacks import Callback as _Callback
from siriuspy.namesys import SiriusPVName as _PVName
from siriuspy.search import PSSearch as _PSSearch, \
    HLTimeSearch as _HLTimeSearch
from siriuspy.pwrsupply.csdev import Const as _PSC
from siriuspy.devices import Devices as _Devices, \
    ASMPSCtrl as _ASMPSCtrl, ASPPSCtrl as _ASPPSCtrl, \
    APU as _APU, EPU as _EPU, PAPU as _PAPU, \
    MachShift as _MachShift, InjCtrl as _InjCtrl, \
    EVG as _EVG, EGTriggerPS as _EGTriggerPS
from siriuspy.devices.pstesters import \
    Triggers as _PSTriggers, PSTesterFactory as _PSTesterFactory



# Configure Logging
_log.basicConfig(
    format='%(levelname)7s | %(asctime)s ::: %(message)s',
    datefmt='%F %T', level=_log.INFO, filemode='a')


class IDParking(_Devices):
    """ID."""

    TIMEOUT_WAIT_FOR_CONNECTION = 5.0  # [s]

    def __init__(self, devname):
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

        super().__init__(devname, [device, ])

    @property
    def park_device(self):
        """Park ID."""
        # check connections
        # print('check connections...')
        if not self._device.wait_for_connection(
                timeout=IDParking.TIMEOUT_WAIT_FOR_CONNECTION):
            return False

        # Desabilita a movimentação dos IDs pelas linhas.
        # print('disable beamline controls...')
        if not self._device.cmd_beamline_ctrl_disable():
            return False

        # Para a movimentação dos IDs
        # print('cmd move stop...')
        if not self._device.cmd_move_stop():
            return False

        # Seta as velocidades de Phase e Gap
        # print('cmd set speeds...')
        value = self._device.phase_speed_max
        if not self._device.set_phase_speed(value):
            return False
        if isinstance(self._device, _EPU):
            value = self._device.gap_speed_max
            if not self._device.set_gap_speed(value):
                return False

        # Seta os IDs para config de estacionamento
        # print('cmd set phase and gap for parking...')
        value = self._device.phase_parked
        if not self._device.set_phase(value):
            return False
        if isinstance(self._device, _EPU):
            value = self._device.gap_parked
        if not self._device.set_gap(value):
            return False

        # Movimenta os IDs para a posição escolhida
        # print('cmd move to parking...')
        if not self._device.cmd_move_start():
            return False
        _time.sleep(2.0)  # aguarda 2 seg.

        # wait for end of movement of timeout
        # print('wait end of movement...')
        timeout, sleep = 70, 0.2  # [s]
        t0 = _time.time()
        while self._device.is_moving:
            if _time.time() - t0 > timeout:
                return False
            _time.sleep(sleep)

        return True


class MachineShutdown(_Devices, _Callback):
    """Machine Shutdown device."""

    DEFAULT_CHECK_TIMEOUT = 10
    DEFAULT_CONN_TIMEOUT = 5
    DEFAULT_TINYSLEEP = 0.1

    def __init__(self, log_callback=None):
        self._abort = False

        self._devrefs = self._create_devices()
        devices = list(self._devrefs.values())

        _Devices.__init__(self, 'AS-Glob:AP-MachShutdown', devices)

        _Callback.__init__(self, log_callback)

    def continue_execution(self):
        """Check whether to continue execution based on abort flag state."""
        if self._abort:
            self._abort = False
            return False
        return True

    def log(self, message):
        """Update execution logs."""
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

    def s01_close_gamma_shutter(self):
        """Try to close gamma shutter."""
        print('--- close_gamma_shutter...')

        dev = self._devrefs['asmpsctrl']
        is_ok = dev.cmd_gamma_disable()
        if not is_ok:
            print('WARN:Could not close gamma shutter.')
        else:
            print('Gamma Shutter closed.')
        return is_ok

    def s02_macshift_update(self):
        """Altera o modo do Turno de operação."""
        print('--- macshift_update...')

        # Executa a PV em questão alterando para o modo maintenance
        maintenance = 5
        _epics.caput('AS-Glob:AP-MachShift:Mode-Sel', maintenance)

        return MachineShutdown._wait_value(
            'AS-Glob:AP-MachShift:Mode-Sts', maintenance, 0.5, 2.0)

    def s03_injmode_update(self):
        """."""
        print('--- injmode_update...')

        print('Alterando o modo de injeção para Decay.')
        # Executa a PV em questão alterando o modo de injeção para Decay.
        decay = 0
        _epics.caput('AS-Glob:AP-InjCtrl:Mode-Sel', decay)

        return MachineShutdown._wait_value(
            'AS-Glob:AP-InjCtrl:Mode-Sts', decay, 0.5, 2.0)

    def s04_injcontrol_disable(self):
        """Desabilta o Controle de Injeção."""
        print('--- injcontrol_disable...')

        print('Desligando Injection')
        _epics.caput('AS-RaMO:TI-EVG:InjectionEvt-Sel', 0)
        if not MachineShutdown._wait_value(
                'AS-RaMO:TI-EVG:InjectionEvt-Sts', 0, 0.5, 2.0):
            return False

        print('Desligando Egun trigger')
        _epics.caput('LI-01:EG-TriggerPS:enable', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-TriggerPS:enablereal', 0, 0.5, 2.0):
            return False

        print('Desligando Sistema de Injeção')
        _epics.caput('AS-Glob:AP-InjCtrl:InjSysTurnOff-Cmd', 0)
        if not MachineShutdown._wait_value(
                'AS-Glob:AP-InjCtrl:InjSysCmdSts-Mon', 0, 0.5, 30.0):
            return False

        return True

    def s05_ids_parking(self):
        """Altera as condições dos IDs para desligamento da Máquina."""
        print('--- ids_parking...')

        # NOTE: parallelize this!
        if not self._devrefs['epu50_10SB'].park_device():
            return False
        if not self._devrefs['apu22_06SB'].park_device():
            return False
        if not self._devrefs['apu22_07SP'].park_device():
            return False
        if not self._devrefs['apu22_08SB'].park_device():
            return False
        if not self._devrefs['apu22_09SA'].park_device():
            return False
        if not self._devrefs['apu58_11SP'].park_device():
            return False
        if not self._devrefs['papu50_17SA'].park_device():
            return False

        return True

    def s06_sofb_fofb_turnoff(self):
        """Desliga o FOFB e posteriormente o SOFB."""
        print('--- sofb_fofb_turnoff...')

        # Parâmetros do FOFB:
        print('FOFB Turn off...')
        # Desabilita o Loop
        _epics.caput('SI-Glob:AP-FOFB:LoopState-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-FOFB:LoopState-Sts', 0, 0.5, 12.0):
            return False

        print('SOFB Turn off...')
        # Desabilita Auto correction State
        _epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-SOFB:LoopState-Sts', 0, 0.5, 5.0):
            return False

        # Desabilita Synchronization
        _epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-SOFB:CorrSync-Sts', 0, 0.5, 5.0):
            return False

        return True

    def s07_bbb_turnoff(self):
        """Desabilita o bbb Hor, Vert e Long."""
        print('--- bbb_turnoff...')

        # desliga os loops H, V e L do bbb.
        _epics.caput('SI-Glob:DI-BbBProc-H:FBCTRL', 0)
        _epics.caput('SI-Glob:DI-BbBProc-V:FBCTRL', 0)
        _epics.caput('SI-Glob:DI-BbBProc-L:FBCTRL', 0)

        pvnames = [
            'SI-Glob:DI-BbBProc-H:FBCTRL',
            'SI-Glob:DI-BbBProc-V:FBCTRL',
            'SI-Glob:DI-BbBProc-L:FBCTRL',
        ]
        values = [0, 0, 0]
        tols = [0.5, 0.5, 0.5]
        if not MachineShutdown._wait_value_set(
                pvnames, values, tols, 2.0):
            return False
        return True

    def s08_sirf_turnoff(self):
        """Ajusta os parâmetros da RF do Anel para desligamento."""
        print('--- sirf_turnoff...')

        # Alterando a taxa de incremento
        print('Alterando a taxa de incremento para 2mV/s')
        incrate_rate = 6
        _epics.caput('SR-RF-DLLRF-01:AMPREF:INCRATE:S', incrate_rate)
        _time.sleep(1.0)

        print('Muda referência do loop para 60mV')
        _epics.caput('SR-RF-DLLRF-01:mV:AL:REF-SP', 60)
        if not MachineShutdown._wait_value(
               'SR-RF-DLLRF-01:SL:REF:AMP', 60, 0.5, 180.0):
            return False

        print('Checando se o feixe acumulado foi derrubado')
        if not MachineShutdown._wait_value(
                'SI-14C4:DI-DCCT:Current-Mon', 0, 0.5, 5.0):
            return False

        # Desabilitando o loop de controle
        print('Desabilitando o loop de controle')
        _epics.caput('SR-RF-DLLRF-01:SL:S', 0)
        _time.sleep(1.0)

        # Desligando as Chaves PIN
        print('Desligando as Chaves PIN')
        _epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw1Dsbl-Cmd', 1)
        _epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw2Dsbl-Cmd', 1)
        _time.sleep(1.0)
        _epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw1Dsbl-Cmd', 0)
        _epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw2Dsbl-Cmd', 0)
        _time.sleep(1.0)

        # Desligando os amplificadores DC/TDK
        print('Desligando os amplificadores DC/TDK')
        _epics.caput('RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Sel', 1)
        _epics.caput('RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Sel', 1)
        _time.sleep(1.0)
        _epics.caput('RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Sel', 0)
        _epics.caput('RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Sel', 0)
        _time.sleep(1.0)

        # Desligando os amplificadores AC/TDK
        print('Desligando os amplificadores AC/TDK')
        _epics.caput('RA-ToSIA01:RF-ACPanel:PwrACDsbl-Sel', 1)
        _epics.caput('RA-ToSIA02:RF-ACPanel:PwrACDsbl-Sel', 1)
        _time.sleep(1.0)
        _epics.caput('RA-ToSIA01:RF-ACPanel:PwrACDsbl-Sel', 0)
        _epics.caput('RA-ToSIA02:RF-ACPanel:PwrACDsbl-Sel', 0)
        _time.sleep(1.0)

        return True

    def s09_borf_turnoff(self):
        """Ajustes dos parâmetros do Booster para desligamento."""
        print('--- borf_turnoff...')

        # Desabilitando a rampa do Booster
        ramp = 0
        _epics.caput('BR-RF-DLLRF-01:RmpEnbl-Sel', ramp)
        if not MachineShutdown._wait_value(
                'BR-RF-DLLRF-01:RmpEnbl-Sts', ramp, 0, 2.0):
            return False
        _time.sleep(2.0)

        print('Desligando o loop de controle...')
        _epics.caput('BR-RF-DLLRF-01:SL:S', 0)
        _time.sleep(1.0)

        print('Desligando a chave PIN...')
        _epics.caput('RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd', 1)
        _time.sleep(0.5)
        _epics.caput('RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd', 0)
        _time.sleep(0.5)

        print('Desligando os Amplificador DC/DC...')
        _epics.caput('RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel', 1)
        _time.sleep(0.5)
        _epics.caput('RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel', 0)
        _time.sleep(0.5)

        print('Desligando os Amplificador 300VDC...')
        _epics.caput('RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel', 1)
        _time.sleep(0.5)
        _epics.caput('RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel', 0)
        _time.sleep(0.5)

        return True

    def s10_modulators_turnoff(self):
        """."""
        print('---modulators_turnoff...')

        # Desliga os botões CHARGE e TRIGOUT dos moduladores
        _epics.caput('LI-01:PU-Modltr-1:CHARGE', 0)
        _epics.caput('LI-01:PU-Modltr-2:CHARGE', 0)
        _time.sleep(1.0)
        _epics.caput('LI-01:PU-Modltr-1:TRIGOUT', 0)
        _epics.caput('LI-01:PU-Modltr-2:TRIGOUT', 0)

        return True

    def s11_adjust_egunbias(self):
        """Ajusta a tensão de Bias do canhão em -100V."""
        print('--- adjust_bias...')

        # Ajusta tensão de Bias em -100V.
        _epics.caput('AS-Glob:AP-InjCtrl:MultBunBiasVolt-SP', -100.0)
        # _epics.caput('AS-Glob:AP-InjCtrl:SglBunBiasVolt-SP', -100.0)

        return True

    def s12_adjust_egunfilament(self):
        """Ajusta a corrente de filamento em 1A."""
        print('--- adjust_egunfilament...')

        # Ajusta corrente de filamento em 1.1A.
        _epics.caput('AS-Glob:AP-InjCtrl:FilaOpCurr-SP', 1.1)
        if not MachineShutdown._wait_value(
                'LI-01:EG-FilaPS:currentinsoft', 1.1, 0.2, 10.0):
            return False

        return True

    def s13_disable_egun_highvoltage(self):
        """Disable egun high voltage."""
        print('---disable_egun_highvoltage...')

        # Ajusta a alta tensão do canhão e checa.
        _epics.caput('AS-Glob:AP-InjCtrl:HVOpVolt-SP', 0.000)
        if not MachineShutdown._wait_value(
                'AS-Glob:AP-InjCtrl:HVOpVoltCmdSts-Mon', 0, 0.5, 100.0):
            return False

        # desabilita enable
        _epics.caput('LI-01:EG-HVPS:enable', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-HVPS:enstatus', 0, 0.5, 2.0):
            return False

        # checar se alta tensão foi desligada.
        _epics.caput('LI-01:EG-HVPS:switch', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-HVPS:swstatus', 0, 0.5, 2.0):
            return False

        return True

    def s14_start_counter(self):
        """Checa inicio de contagem para liberar túnel."""
        print('--- start_counter...')

        # Verificar se a contagem regressiva para liberar acesso
        # ao túnel iniciou."""
        # dev = self._devrefs['asppsctrl']
        # if dev.time_left_for_tunnel_access() == 360:
        #     return False
        msg = (
            'Confirme se a contagem regressiva para '
            'liberar acesso ao túnel iniciou')
        input(msg)

        return True

    def s15_disable_ps_triggers(self):
        """Disable PS triggers."""
        self.log('Disabling PS triggers...')
        return self._disable_ps_triggers('PS')

    def s16_run_ps_turn_off_procedure(self):
        """Do turn off PS procedure."""
        self.log('Executing Turn Off PS...')
        return self._exec_ps_turnoff('PS')

    def s17_disable_pu_triggers(self):
        """Disable PU triggers."""
        self.log('Disabling PU triggers...')
        return self._disable_ps_triggers('PU')

    def s18_run_pu_turn_off_procedure(self):
        """Do turn off PU procedure."""
        self.log('Executing Turn Off PU...')
        return self._exec_ps_turnoff('PU')

    def s19_free_access(self):
        """Aguardar zerar contagem."""
        print('--- free_access...')

        # Aguardar o contador chegar em 0, após 6 horas, para
        # liberar acesso ao túnel."""
        print('free_access')
        msg = (
            'Aguarde o contador chegar em 0, após 6 horas, '
            'para liberar acessoa ao túnel')
        input(msg)

        return True

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
        if not self.s19_free_access():
            return False
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

        # Interlock
        devices['asppsctrl'] = _ASPPSCtrl()
        devices['asmpsctrl'] = _ASMPSCtrl()

        # IDs
        devices['apu22_06SB'] = IDParking(_APU.DEVICES.APU22_06SB)
        devices['apu22_07SP'] = IDParking(_APU.DEVICES.APU22_07SP)
        devices['apu22_08SB'] = IDParking(_APU.DEVICES.APU22_08SB)
        devices['apu22_09SA'] = IDParking(_APU.DEVICES.APU22_09SA)
        devices['apu58_11SP'] = IDParking(_APU.DEVICES.APU58_11SP)
        devices['epu50_10SB'] = IDParking(_EPU.DEVICES.EPU50_10SB)
        devices['papu50_17SA'] = IDParking(_PAPU.DEVICES.PAPU50_17SA)

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

    @staticmethod
    def _wait_value(pvname, value_target, value_tol, timeout, sleep=0.1):
        """."""
        pvd = _epics.PV(pvname)
        time0 = _time.time()
        strf = (
            'timeout: não foi possível esperar a PV {} chegar ao '
            'seu valor de target!')
        while abs(pvd.value - value_target) > value_tol:
            if _time.time() - time0 > timeout:
                if sleep != 0:
                    print(strf.format(pvname))
                return False
            _time.sleep(sleep)
        return True

    @staticmethod
    def _wait_value_set(pvnames, value_targets, value_tols, timeout):
        """."""
        pvnames_not_ready = [
            (pvname, idx) for idx, pvname in enumerate(pvnames)]
        strf = (
            'timeout: não foi possível esperar todas as PVs '
            'chegarem aos seus valores de target!')
        time0 = _time.time()
        while pvnames_not_ready:
            print(len(pvnames_not_ready))
            # print(pvnames_not_ready)
            for pvname, idx in pvnames_not_ready:
                if MachineShutdown._wait_value(
                        pvname, value_targets[idx], value_tols[idx],
                        timeout=0, sleep=0.0):
                    pvnames_not_ready.remove((pvname, idx))
            if _time.time() - time0 > timeout:
                print(strf)
                return False
            if pvnames_not_ready:
                _time.sleep(0.2)
        return True

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
