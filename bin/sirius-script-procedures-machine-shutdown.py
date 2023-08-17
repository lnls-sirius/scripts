#!/usr/bin/env python-sirius
"""Machine shutdown script."""

import time as _time
import logging as _log

import epics as _epics

from siriuspy.callbacks import Callback as _Callback
from siriuspy.devices import Devices as _Devices, \
    ASMPSCtrl as _ASMPSCtrl, ASPPSCtrl as _ASPPSCtrl, \
    APU as _APU, EPU as _EPU, PAPU as _PAPU, \
    MachShift as _MachShift, InjCtrl as _InjCtrl, \
    EVG as _EVG, EGTriggerPS as _EGTriggerPS
from siriuspy.search import PSSearch as _PSSearch


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
        """Desliga os triggers das fontes."""
        print('--- disable_ps_triggers...')

        print('Desabilitando os triggers...')
        # desliga os trigger's das fontes da TB, TS, BO e SI
        _epics.caput('BO-Glob:TI-Mags-Corrs:State-Sel', 0)
        _epics.caput('BO-Glob:TI-Mags-Fams:State-Sel', 0)
        _epics.caput('SI-01:TI-Mags-FFCorrs:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-Bends:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-Corrs:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-QTrims:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-Quads:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-Sexts:State-Sel', 0)
        _epics.caput('SI-Glob:TI-Mags-Skews:State-Sel', 0)
        _epics.caput('TB-Glob:TI-Mags:State-Sel', 0)
        _epics.caput('TS-Glob:TI-Mags:State-Sel', 0)
        _time.sleep(0.5)

        pvnames = [
            'BO-Glob:TI-Mags-Corrs:State-Sel',
            'BO-Glob:TI-Mags-Fams:State-Sel',
            'SI-01:TI-Mags-FFCorrs:State-Sel',
            'SI-Glob:TI-Mags-Bends:State-Sel',
            'SI-Glob:TI-Mags-Corrs:State-Sel',
            'SI-Glob:TI-Mags-QTrims:State-Sel',
            'SI-Glob:TI-Mags-Quads:State-Sel',
            'SI-Glob:TI-Mags-Sexts:State-Sel',
            'SI-Glob:TI-Mags-Skews:State-Sel',
            'TB-Glob:TI-Mags:State-Sel',
            'TS-Glob:TI-Mags:State-Sel',
        ]
        value_targets = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        value_tols = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
        return MachineShutdown._wait_value_set(
            pvnames, value_targets, value_tols, 2.0)

    def s16_turn_off_sofbmode(self):
        """Desabilita o nodo SOFBMode."""
        print('--- turn_off_sofbmode...')

        timeout = 50  # [s]
        print('Desligando o modo SOFBMode...')
        for sec in ('LI', 'TB', 'BO', 'TS', 'SI'):
            print(sec)
            if not \
                    MachineShutdown._ps_sofbmode(sec=sec, timeout=timeout):
                return False

        return True

    def s17_set_ps_and_dclinks_to_slowref(self):
        """Altera o modo das fontes e dclinks de OpMode para SlowRef."""
        print('--- set_ps_and_dclinks_to_slowref...')

        print('DCLinks_Opmode_to_Slowref...')
        timeout = 50  # [s]

        dclinks = set()
        psnames = list()
        psnames = psnames + _PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        for psname in psnames:
            dclinks_ = _PSSearch.conv_psname_2_dclink(psname)
            if not dclinks_:
                continue
            for dclink in dclinks_:
                psmodel = _PSSearch.conv_psname_2_psmodel(dclink)
                if 'REGATRON' not in psmodel:
                    dclinks.add(dclink)

        pvnames = []
        for dclink in dclinks:
            print(dclink)
            pvname = dclink + ':' + 'OpMode-Sel'
            pvnames.append(psname + ':' + 'CtrlMode-Mon')
            _epics.caput(pvname, 0)
        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False

        # Altera o modo das fontes de OpMode para SlowRef da TB
        for sec in ('TB', 'TS', 'BO', 'SI'):
            if not MachineShutdown._ps_set_slowref(sec=sec):
                return False

        return True

    def s18_set_ps_current_to_zero(self):
        """Seleciona e zera a corrente de todas as fontes dos aceleradores."""
        print('--- set_ps_current_to_zero...')

        # NOTE: timeout waiting for FCH !!!

        timeout = 50  # [s]
        # for sec in ('LI', 'TB', 'TS', 'BO', 'SI'):
        for sec in ('SI', ):
            if not MachineShutdown._ps_zero(sec=sec, timeout=timeout):
                return False

        return True

    def s19_reset_ps_and_dclinks(self):
        """Reseta as fontes e DCLinks e verifica sinais de interlock."""
        print('--- reset_ps_and_dclinks...')

        timeout = 50  # [s]
        # Reset PS
        for sec in ('TB', 'TS', 'BO', 'SI'):
            if not MachineShutdown._ps_interlocks(sec=sec, timeout=timeout):
                return False

        # Reset dos DCLinks
        dclinks = set()
        psnames = list()
        psnames = psnames + _PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        for psname in psnames:
            dclinks_ = _PSSearch.conv_psname_2_dclink(psname)
            if not dclinks_:
                continue
            for dclink in dclinks_:
                psmodel = _PSSearch.conv_psname_2_psmodel(dclink)
                if 'REGATRON' not in psmodel:
                    dclinks.add(dclink)

        pvnames = []
        for dclink in dclinks:
            pvnames.append(dclink + ':' + 'IntlkSoft-Mon')
            pvnames.append(dclink + ':' + 'IntlKHard-Mon')
            pvname = dclink + ':' + 'Reset-Cmd'
            _epics.caput(pvname, 1)

        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)

        return MachineShutdown._wait_value_set(pvnames, values, tols, timeout)

    def s20_turn_ps_off(self):
        """Desliga todas as fontes."""
        print('--- turn_ps_off...')

        timeout = 50  # [s]
        for sec in ('LI', 'TB', 'TS', 'BO', 'SI'):
            if not MachineShutdown._ps_turn_off(sec=sec, timeout=timeout):
                return False

        return True

    def s21_turn_dclinks_off(self):
        """Desliga os DC links das fontes."""
        print('--- turn_dclinks_off...')

        timeout = 50  # [s]
        dclinks = set()
        psnames = list()
        psnames = psnames + _PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        psnames = psnames + _PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        for psname in psnames:
            dclinks_ = _PSSearch.conv_psname_2_dclink(psname)
            if not dclinks_:
                continue
            for dclink in dclinks_:
                psmodel = _PSSearch.conv_psname_2_psmodel(dclink)
                if 'REGATRON' not in psmodel:
                    dclinks.add(dclink)

        pvnames = []
        for dclink in dclinks:
            print(dclink)
            pvname = dclink + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            _epics.caput(pvname, 0)

        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)

        return MachineShutdown._wait_value_set(pvnames, values, tols, timeout)

    def s22_free_access(self):
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
        if not self.s16_turn_off_sofbmode():
            return False
        if not self.s17_set_ps_and_dclinks_to_slowref():
            return False
        if not self.s18_set_ps_current_to_zero():
            return False
        if not self.s19_reset_ps_and_dclinks():
            return False
        if not self.s20_turn_ps_off():
            return False
        if not self.s21_turn_dclinks_off():
            return False
        # TODO desligar pulsados
        if not self.s22_free_access():
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

        return devices

    @staticmethod
    def _ps_sofbmode(sec, timeout):
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        pvnames = []
        for psname in psnames:
            psmodel = _PSSearch.conv_psname_2_psmodel(psname)
            if psmodel != 'FBP':
                continue
            pvname = psname + ':' + 'SOFBMode-Sel'
            pvnames.append(psname + ':' + 'SOFBMode-Sts')
            _epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(
                pvnames, values, tols, timeout):
            return False
        return True

    @staticmethod
    def _ps_set_slowref(sec):
        # Altera o modo das fontes de OpMode para SlowRef
        # NOTE: implementar checagem do OpMode-Sts
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        for psname in psnames:
            if 'FCH' in psname or 'FCV' in psname:
                continue
            pvname = psname + ':' + 'OpMode-Sel'
            _epics.caput(pvname, 'SlowRef')
        return True

    @staticmethod
    def _ps_zero(sec, timeout):
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        pvnames = []
        for psname in psnames:
            # print(psname)
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            _epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False
        return True

    @staticmethod
    def _ps_interlocks(sec, timeout):
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        pvnames = []
        for psname in psnames:
            pvnames.append(psname + ':' + 'IntlkSoft-Mon')
            pvnames.append(psname + ':' + 'IntlkHard-Mon')
            pvname = psname + ':' + 'Reset-Cmd'
            if sec != 'LI':
                _epics.caput(pvname, 1)
        values, tols = [1, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False
        return True

    @staticmethod
    def _ps_turn_off(sec, timeout):
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            _epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False
        return True

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


if __name__ == '__main__':
    """."""
    ms = MachineShutdown()
    if ms.execute_procedure():
        print('machine shutdown success')
    else:
        print('machine shutdown failed')
