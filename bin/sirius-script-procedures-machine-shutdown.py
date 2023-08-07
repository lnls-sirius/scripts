#!/usr/bin/env python-sirius
"""."""

import time
import epics
import numpy as np

from siriuspy.search import PSSearch as _PSSearch


class MachineShutdown:
    """."""

    def __init__(self, dry_run=True):
        """."""
        self._dry_run = dry_run

    def s01_close_gamma_shutter(self):
        """Mensagem para fechar o Gama."""
        # TODO: include interlock PV for gamma signal
        if self._dry_run:
            return True
        print('--- close_gamma_shutter...')

        msg = ('Por favor, feche o gama e em seguida tecle ENTER')
        input(msg)

        return True

    def s02_macshift_update(self):
        """Altera o modo do Turno de operação."""
        if self._dry_run:
            return True
        print('--- macshift_update...')

        # Executa a PV em questão alterando para o modo maintenance
        maintenance = 5
        epics.caput('AS-Glob:AP-MachShift:Mode-Sel', maintenance)

        return MachineShutdown._wait_value('AS-Glob:AP-MachShift:Mode-Sts', maintenance, 0.5, 2.0)

    def s03_injmode_update(self):
        """."""
        if self._dry_run:
            return True
        print('--- injmode_update...')

        print('Alterando o modo de injeção para Decay.')
        # Executa a PV em questão alterando o modo de injeção para Decay.
        decay = 0
        epics.caput('AS-Glob:AP-InjCtrl:Mode-Sel', decay)

        return MachineShutdown._wait_value(
            'AS-Glob:AP-InjCtrl:Mode-Sts', decay, 0.5, 2.0)

    def s04_injcontrol_disable(self):
        """Desabilta o Controle de Injeção."""
        if self._dry_run:
            return True
        print('--- injcontrol_disable...')

        print('Desligando Injection')
        epics.caput('AS-RaMO:TI-EVG:InjectionEvt-Sel', 0)
        if not MachineShutdown._wait_value(
                'AS-RaMO:TI-EVG:InjectionEvt-Sts', 0, 0.5, 2.0):
            return False

        print('Desligando Egun trigger')
        epics.caput('LI-01:EG-TriggerPS:enable', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-TriggerPS:enablereal', 0, 0.5, 2.0):
            return False

        print('Desligando Sistema de Injeção')
        epics.caput('AS-Glob:AP-InjCtrl:InjSysTurnOff-Cmd', 0)
        if not MachineShutdown._wait_value(
                'AS-Glob:AP-InjCtrl:InjSysCmdSts-Mon', 0, 0.5, 30.0):
            return False

        return True

    def s05_ids_parking(self):
        """Altera as condições dos IDs para desligamento da Máquina."""
        if self._dry_run:
            return True
        print('--- ids_parking...')

        # TODO: set also the velocities
        stop, start = 1, 3
        g1 = 36  # [mm]
        p1, p2 = 11, 29  # [mm]

        # Desabilita a movimentação dos IDs pelas linhas.
        epics.caput('SI-06SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-07SP:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-08SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-09SA:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-10SB:ID-EPU50:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-11SP:ID-APU58:BeamLineCtrlEnbl-Sel', 'Dsbl')
        time.sleep(1.0)  # aguarda 1 seg.

        # Para a movimentação dos IDs
        epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', stop)
        time.sleep(1.0)  # aguarda 1 seg.

        # Seta os IDs para config de estacionamento
        epics.caput('SI-06SB:ID-APU22:Phase-SP', p1)
        epics.caput('SI-07SP:ID-APU22:Phase-SP', p1)
        epics.caput('SI-08SB:ID-APU22:Phase-SP', p1)
        epics.caput('SI-09SA:ID-APU22:Phase-SP', p1)
        epics.caput('SI-10SB:ID-EPU50:Gap-SP', g1)
        epics.caput('SI-11SP:ID-APU58:Phase-SP', p2)
        time.sleep(1.0)  # aguarda 1 seg.

        # Seta a Phase Speed
        epics.caput('SI-06SB:ID-APU22:PhaseSpeed-SP', start)
        epics.caput('SI-07SP:ID-APU22:PhaseSpeed-SP', start)
        epics.caput('SI-08SB:ID-APU22:PhaseSpeed-SP', start)
        epics.caput('SI-09SA:ID-APU22:PhaseSpeed-SP', start)
        epics.caput('SI-10SB:ID-EPU50:GapSpeed-SP', start)
        epics.caput('SI-11SP:ID-APU58:PhaseSpeed-SP', start)
        time.sleep(1.0)  # aguarda 1 seg.

        # Movimenta os IDs para a posição escolhida
        epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', start)
        epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', start)
        epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', start)
        epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', start)
        epics.caput('SI-10SB:ID-EPU50:ChangeGap-Cmd', start)
        epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', start)
        time.sleep(1.0)  # aguarda 1 seg.

        pvnames = [
            'SI-06SB:ID-APU22:Phase-Mon',
            'SI-07SP:ID-APU22:Phase-Mon',
            'SI-08SB:ID-APU22:Phase-Mon',
            'SI-09SA:ID-APU22:Phase-Mon',
            'SI-10SB:ID-EPU50:Gap-Mon',
            'SI-11SP:ID-APU58:Phase-Mon',
        ]
        value_targets = [p1, p1, p1, p1, g1, p2]
        value_tols = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1]
        return MachineShutdown._wait_value_set(
            pvnames, value_targets, value_tols, timeout=70)

    def s06_sofb_fofb_turnoff(self):
        """Desliga o FOFB e posteriormente o SOFB."""
        if self._dry_run:
            return True
        print('--- sofb_fofb_turnoff...')

        # Parâmetros do FOFB:
        print('FOFB Turn off...')
        # Desabilita o Loop
        epics.caput('SI-Glob:AP-FOFB:LoopState-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-FOFB:LoopState-Sts', 0, 0.5, 12.0):
            return False

        print('SOFB Turn off...')
        # Desabilita Auto correction State
        epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-SOFB:LoopState-Sts', 0, 0.5, 5.0):
            return False

        # Desabilita Synchronization
        epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)
        if not MachineShutdown._wait_value(
                'SI-Glob:AP-SOFB:CorrSync-Sts', 0, 0.5, 5.0):
            return False

        return True

    def s07_bbb_turnoff(self):
        """Desabilita o bbb Hor, Vert e Long."""
        if self._dry_run:
            return True
        print('--- bbb_turnoff...')

        # desliga os loops H, V e L do bbb.
        epics.caput('SI-Glob:DI-BbBProc-H:FBCTRL', 0)
        epics.caput('SI-Glob:DI-BbBProc-V:FBCTRL', 0)
        epics.caput('SI-Glob:DI-BbBProc-L:FBCTRL', 0)

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

    def s08_beam_kill(self):
        """Encerra o feixe utilizando o metodo RFKillbeam."""
        if self._dry_run:
            return True
        print('--- beam_kill...')

        print('Encerrando o feixe acumulado...')
        epics.caput('AS-Glob:AP-InjCtrl:RFKillBeam-Cmd', 0)
        if not MachineShutdown._wait_value(
                'SI-13C4:DI-DCCT:Current-Mon', 0, 0.5, 4.0):
            return False

        return True

    def s09_disable_ps_triggers(self):
        """Desliga os triggers das fontes."""
        if self._dry_run:
            return True
        print('--- disable_ps_triggers...')

        print('Desabilitando os triggers...')
        # desliga os trigger's das fontes da TB, TS, BO e SI
        epics.caput('BO-Glob:TI-Mags-Corrs:State-Sel', 0)
        epics.caput('BO-Glob:TI-Mags-Fams:State-Sel', 0)
        epics.caput('SI-01:TI-Mags-FFCorrs:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-Bends:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-Corrs:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-QTrims:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-Quads:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-Sexts:State-Sel', 0)
        epics.caput('SI-Glob:TI-Mags-Skews:State-Sel', 0)
        epics.caput('TB-Glob:TI-Mags:State-Sel', 0)
        epics.caput('TS-Glob:TI-Mags:State-Sel', 0)
        time.sleep(0.5)

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

    def s10_turn_off_sofbmode(self):
        """Desabilita o nodo SOFBMode."""
        if self._dry_run:
            return True
        print('--- turn_off_sofbmode...')

        timeout = 50  # [s]
        print('Desligando o modo SOFBMode...')
        for sec in ('LI', 'TB', 'BO', 'TS', 'SI'):
            print(sec)
            if not \
                    MachineShutdown._ps_sofbmode(sec=sec, timeout=timeout):
                return False

        return True

    def s11_set_ps_and_dclinks_to_slowref(self):
        """Altera o modo das fontes e dclinks de OpMode para SlowRef."""
        if self._dry_run:
            return True
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
            epics.caput(pvname, 0)
        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False

        # Altera o modo das fontes de OpMode para SlowRef da TB
        for sec in ('TB', 'TS', 'BO', 'SI'):
            if not MachineShutdown._ps_set_slowref(sec=sec):
                return False

        return True

    def s12_set_ps_current_to_zero(self):
        """Seleciona e zera a corrente de todas as fontes dos aceleradores."""
        if self._dry_run:
            return True
        print('--- set_ps_current_to_zero...')

        # NOTE: timeout waiting for FCH !!!

        timeout = 50  # [s]
        # for sec in ('LI', 'TB', 'TS', 'BO', 'SI'):
        for sec in ('SI', ):
            if not MachineShutdown._ps_zero(sec=sec, timeout=timeout):
                return False

        return True

    def s13_reset_ps_and_dclinks(self):
        """Reseta as fontes e DCLinks e verifica sinais de interlock."""
        if self._dry_run:
            return True
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
            epics.caput(pvname, 1)

        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)

        return MachineShutdown._wait_value_set(pvnames, values, tols, timeout)

    def s14_turn_ps_off(self):
        """Desliga todas as fontes."""
        if self._dry_run:
            return True
        print('--- turn_ps_off...')

        timeout = 50  # [s]
        for sec in ('LI', 'TB', 'TS', 'BO', 'SI'):
            if not MachineShutdown._ps_turn_off(sec=sec, timeout=timeout):
                return False

        return True

    def s15_turn_dclinks_off(self):
        """Desliga os DC links das fontes."""
        if self._dry_run:
            return True
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
            epics.caput(pvname, 0)

        values = [0.0, ] * len(pvnames)
        tols = [0.2] * len(pvnames)

        return MachineShutdown._wait_value_set(pvnames, values, tols, timeout)

    def s08_sirf_turnoff(self):
        """Ajusta os parâmetros da RF do Anel para desligamento."""
        if self._dry_run:
            return True
        print('--- sirf_turnoff...')

        # Alterando a taxa de incremento
        print('Alterando a taxa de incremento para 2mV/s')
        incrate_rate = 6
        epics.caput('SR-RF-DLLRF-01:AMPREF:INCRATE:S', incrate_rate)
        time.sleep(1.0)

        print('Muda referência do loop para 60mV')
        epics.caput('SR-RF-DLLRF-01:mV:AL:REF-SP', 60)
        if not MachineShutdown._wait_value(
               'SR-RF-DLLRF-01:SL:REF:AMP', 60, 0.5, 180.0):
            return False

        print('Checando se o feixe acumulado foi derrubado')
        if not MachineShutdown._wait_value(
                'SI-14C4:DI-DCCT:Current-Mon', 0, 0.5, 5.0):
            return False

        # Desabilitando o loop de controle
        print('Desabilitando o loop de controle')
        epics.caput('SR-RF-DLLRF-01:SL:S', 0)
        time.sleep(1.0)

        # Desligando as Chaves PIN
        print('Desligando as Chaves PIN')
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw1Dsbl-Cmd', 1)
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw2Dsbl-Cmd', 1)
        time.sleep(1.0)
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw1Dsbl-Cmd', 0)
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw2Dsbl-Cmd', 0)
        time.sleep(1.0)

        # Desligando os amplificadores DC/TDK
        print('Desligando os amplificadores DC/TDK')
        epics.caput('RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Sel', 1)
        epics.caput('RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Sel', 1)
        time.sleep(1.0)
        epics.caput('RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Sel', 0)
        epics.caput('RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Sel', 0)
        time.sleep(1.0)

        # Desligando os amplificadores AC/TDK
        print('Desligando os amplificadores AC/TDK')
        epics.caput('RA-ToSIA01:RF-ACPanel:PwrACDsbl-Sel', 1)
        epics.caput('RA-ToSIA02:RF-ACPanel:PwrACDsbl-Sel', 1)
        time.sleep(1.0)
        epics.caput('RA-ToSIA01:RF-ACPanel:PwrACDsbl-Sel', 0)
        epics.caput('RA-ToSIA02:RF-ACPanel:PwrACDsbl-Sel', 0)
        time.sleep(1.0)

        return True

    def s09_borf_turnoff(self):
        """Ajustes dos parâmetros do Booster para desligamento."""
        if self._dry_run:
            return True
        print('--- borf_turnoff...')

        # Desabilitando a rampa do Booster
        ramp = 0
        epics.caput('BR-RF-DLLRF-01:RmpEnbl-Sel', ramp)
        if not MachineShutdown._wait_value(
                'BR-RF-DLLRF-01:RmpEnbl-Sts', ramp, 0, 2.0):
            return False
        time.sleep(2.0)

        print('Desligando o loop de controle...')
        epics.caput('BR-RF-DLLRF-01:SL:S', 0)
        time.sleep(1.0)

        print('Desligando a chave PIN...')
        epics.caput('RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd', 1)
        time.sleep(0.5)
        epics.caput('RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd', 0)
        time.sleep(0.5)

        print('Desligando os Amplificador DC/DC...')
        epics.caput('RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel', 1)
        time.sleep(0.5)
        epics.caput('RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel', 0)
        time.sleep(0.5)

        print('Desligando os Amplificador 300VDC...')
        epics.caput('RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel', 1)
        time.sleep(0.5)
        epics.caput('RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel', 0)
        time.sleep(0.5)

        return True

    def s10_modulators_turnoff(self):
        """."""
        if self._dry_run:
            return True
        print('---modulators_turnoff...')

        # Desliga os botões CHARGE e TRIGOUT dos moduladores
        epics.caput('LI-01:PU-Modltr-1:CHARGE', 0)
        epics.caput('LI-01:PU-Modltr-2:CHARGE', 0)
        time.sleep(1.0)
        epics.caput('LI-01:PU-Modltr-1:TRIGOUT', 0)
        epics.caput('LI-01:PU-Modltr-2:TRIGOUT', 0)

        return True

    def s19_ajust_egun_highvoltage(self):
        """Disable egun high voltage."""
        if self._dry_run:
            return True
        print('---disable_egun_highvoltage...')

        # Ajusta a alta tensão do canhão e checa.
        epics.caput('AS-Glob:AP-InjCtrl:HVOpVolt-SP', 0.000)
        if not MachineShutdown._wait_value(
                'AS-Glob:AP-InjCtrl:HVOpVoltCmdSts-Mon', 0, 0.5, 60.0):
            return False

        # desabilita enable
        epics.caput('LI-01:EG-HVPS:enable', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-HVPS:enstatus', 0, 0.5, 2.0):
            return False

        # checar se alta tensão foi desligada.
        epics.caput('LI-01:EG-HVPS:switch', 0)
        if not MachineShutdown._wait_value(
                'LI-01:EG-HVPS:swstatus', 0, 0.5, 2.0):
            return False

        return True

    def s20_ajust_egunbias(self):
        """Ajusta a tensão de Bias do canhão em -100V."""
        if self._dry_run:
            return True
        print('--- adjust_bias...')

        # Ajusta tensão de Bias em -100V.
        epics.caput('AS-Glob:AP-InjCtrl:MultBunBiasVolt-SP', -100.0)
        # epics.caput('AS-Glob:AP-InjCtrl:SglBunBiasVolt-SP', -100.0)

        return True

    def s21_ajust_egunfilament(self):
        """Ajusta a corrente de filamento em 1A."""
        if self._dry_run:
            return True
        print('--- adjust_egunfilament...')

        # Ajusta corrente de filamento em 1.1A.
        epics.caput('AS-Glob:AP-InjCtrl:FilaOpCurr-SP', 1.1)
        if not MachineShutdown._wait_value(
                'LI-01:EG-FilaPS:currentinsoft', 1.1, 0.2, 10.0):
            return False

        return True

    def s22_start_counter(self):
        """Checa inicio de contagem para liberar túnel."""
        if self._dry_run:
            return True
        print('--- start_counter...')

        # Verificar se a contagem regressiva para liberar acesso
        # ao túnel iniciou."""
        print('start_counter')
        msg = (
            'Confirme se a contagem regressiva para '
            'liberar acesso ao túnel iniciou')
        input(msg)

        return True

    def s23_free_access(self):
        """Aguardar zerar contagem."""
        if self._dry_run:
            return True
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
        if not self.s08_beam_kill():
            return False
        if not self.s09_disable_ps_triggers():
            return False
        if not self.s10_turn_off_sofbmode():
            return False
        if not self.s11_set_ps_and_dclinks_to_slowref():
            return False
        if not self.s12_set_ps_current_to_zero():
            return False
        if not self.s13_reset_ps_and_dclinks():
            return False
        if not self.s14_turn_ps_off():
            return False
        if not self.s15_turn_dclinks_off():
            return False
        if not self.s16_sirf_turnoff():
            return False
        if not self.s17_borf_turnoff():
            return False
        if not self.s18_modulators_turnoff():
            return False
        if not self.s19_ajust_egun_highvoltage():
            return False
        if not self.s20_ajust_egunbias():
            return False
        if not self.s21_ajust_egunfilament():
            return False
        if not self.s22_start_counter():
            return False
        if not self.s23_free_access():
            return False

        return True

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
            epics.caput(pvname, 0)
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
            epics.caput(pvname, 'SlowRef')
        return True

    @staticmethod
    def _ps_zero(sec, timeout):
        psnames = _PSSearch.get_psnames(dict(sec=sec, dis='PS'))
        pvnames = []
        for psname in psnames:
            # print(psname)
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
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
                epics.caput(pvname, 1)
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
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown._wait_value_set(pvnames, values, tols, timeout):
            return False
        return True

    @staticmethod
    def _wait_value(pvname, value_target, value_tol, timeout, sleep=0.1):
        """."""
        pvd = epics.PV(pvname)
        time0 = time.time()
        strf = (
            'timeout: não foi possível esperar a PV {} chegar ao '
            'seu valor de target!')
        while abs(pvd.value - value_target) > value_tol:
            if time.time() - time0 > timeout:
                if sleep != 0:
                    print(strf.format(pvname))
                return False
            time.sleep(sleep)
        return True

    @staticmethod
    def _wait_value_set(pvnames, value_targets, value_tols, timeout):
        """."""
        pvnames_not_ready = [
            (pvname, idx) for idx, pvname in enumerate(pvnames)]
        strf = (
            'timeout: não foi possível esperar todas as PVs '
            'chegarem aos seus valores de target!')
        time0 = time.time()
        while pvnames_not_ready:
            print(len(pvnames_not_ready))
            # print(pvnames_not_ready)
            for pvname, idx in pvnames_not_ready:
                if MachineShutdown._wait_value(
                        pvname, value_targets[idx], value_tols[idx],
                        timeout=0, sleep=0.0):
                    pvnames_not_ready.remove((pvname, idx))
            if time.time() - time0 > timeout:
                print(strf)
                return False
            if pvnames_not_ready:
                time.sleep(0.2)
        return True


if __name__ == '__main__':
    """."""
    ms = MachineShutdown(dry_run=True)
    if ms.execute_procedure():
        print('machine shutdown success')
    else:
        print('machine shutdown failed')
