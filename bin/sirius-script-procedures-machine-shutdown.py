#!/usr/bin/env python-sirius
"""."""

import time
import epics
import numpy as np

from siriuspy.search import PSSearch


class MachineShutdown:
    """."""

    def __init__(self, dry_run=True):
        """."""
        self._dry_run = dry_run

    def s01_close_gamma_shutter(self):
        """Mensagem para fechar o Gama."""

        print('close_gamma_shutter...')
        msg = (
            'por favor, feche o gama e em seguida tecle ENTER'
            )
        input(msg)

        return True

    def s02_macshift_update(self):
        """Altera o modo do Turno de operação."""
        if self._dry_run:
            return

        # mensagem a ser impressa na tela com a alteração do Turno
        print('macshift_update...')

        # Executa a PV em questão alterando para o modo maintenance
        maintenance = 5
        epics.caput('AS-Glob:AP-MachShift:Mode-Sel', maintenance)

        res = MachineShutdown.wait_value(
            'AS-Glob:AP-MachShift:Mode-Sts', maintenance, 0.5, 2.0)
        return res

        # Conferir inclusão do EPU-50

    def s03_ids_parking(self):
        """."""
        if self._dry_run:
            return

        print('ids_parking...')

        stop, start = 1, 3
        g1 = 36  # [mm]
        p1, p2 = 11, 29  # [mm]

        # desabilita a movimentação dos IDs pelas linhas.
        epics.caput('SI-06SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-07SP:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-08SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-09SA:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-10SB:ID-EPU50:BeamLineCtrlEnbl-Sel', 'Dsbl')
        epics.caput('SI-11SP:ID-APU58:BeamLineCtrlEnbl-Sel', 'Dsbl')
        time.sleep(1.0)  # aguarda 1 seg.

        # para a movimentação dos IDs
        epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', stop)
        epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', stop)
        time.sleep(1.0)  # aguarda 1 seg.

        # seta os IDs para config de estacionamento
        epics.caput('SI-06SB:ID-APU22:Phase-SP', p1)
        epics.caput('SI-07SP:ID-APU22:Phase-SP', p1)
        epics.caput('SI-08SB:ID-APU22:Phase-SP', p1)
        epics.caput('SI-09SA:ID-APU22:Phase-SP', p1)
        epics.caput('SI-10SB:ID-EPU50:Gap-SP', g1)
        epics.caput('SI-11SP:ID-APU58:Phase-SP', p2)
        time.sleep(1.0)  # aguarda 1 seg.

        # movimenta os IDs para a posição escolhida
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
        return MachineShutdown.wait_value_set(
            pvnames, value_targets, value_tols, timeout=70)

    def s04_sofb_fofb_turnoff(self):
        """Desliga inicialmente o FOFB e depois o SOFB."""
        if self._dry_run:
           return

        # Parâmetros do FOFB:
        print('fofb_turnoff...')
        # desliga Orbit Distortion Detect
        epics.caput('SI-Glob:AP-FOFB:LoopMaxOrbDistortionEnbl-Sel', 0)
        # desliga o loop do fofb(ENABLE)
        epics.caput('SI-Glob:AP-FOFB:LoopState-Sel', 0)

        # --- Versão nova SOFB:
        print('sofb_turnoff...')
        # desliga Auto correction State
        epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)
        # desliga Synchronization
        epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)
        # desliga PSSOFB Enable
        epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sel', 0)

        pvnames = [
           'SI-Glob:AP-SOFB:LoopState-Sts',
           'SI-Glob:AP-SOFB:CorrSync-Sts',
           'SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sts',
            ]

        value_targets = [0, 0, 0]
        value_tols = [0.5, 0.5, 0.5]
        return MachineShutdown.wait_value_set(
           pvnames, value_targets, value_tols, 2.0)

    def s04_sofb_fofb_turnoff_orig(self):
        """Desliga inicialmente o FOFB e depois o SOFB."""
        if self._dry_run:
           return

        # Parâmetros do FOFB:
        print('fofb_turnoff...')
        # desliga Orbit Distortion Detect
        epics.caput('SI-Glob:AP-FOFB:LoopMaxOrbDistortionEnbl-Sel', 0)
        # desliga o loop do fofb(ENABLE)
        epics.caput('SI-Glob:AP-FOFB:LoopState-Sel', 0)

        # --- Versão antiga SOFB:
        print('sofb_turnoff...')
        # desliga correção de órbita automática
        epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)
        # desliga o sinal Wait
        epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBWait-Sel', 0)
        # desliga o sinal Enable
        epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sel', 0)
        # altera o estado do sinal de Sync para OFF
        epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)

        pvnames = [
           'SI-Glob:AP-SOFB:LoopState-Sts',
           'SI-Glob:AP-SOFB:CorrSync-Sts',
           'SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sts',
           # NOTE: add PV
            ]

        value_targets = [0, 0, 0]
        value_tols = [0.5, 0.5, 0.5]
        return MachineShutdown.wait_value_set(
           pvnames, value_targets, value_tols, 2.0)

    def s05_bbb_turnoff(self):
        """Desabilita o bbb Hor, Vert e Long."""
        if self._dry_run:
            return

        print('bbb_turnoff...')
        # desliga os loops H, V e L do bbb.
        epics.caput('SI-Glob:DI-BbBProc-H:FBCTRL', 0)
        epics.caput('SI-Glob:DI-BbBProc-V:FBCTRL', 0)
        epics.caput('SI-Glob:DI-BbBProc-L:FBCTRL', 0)

        if not MachineShutdown.wait_value(
                'SI-Glob:DI-BbBProc-H:FBCTRL', 0, 0.5, 2.0):
            return False
        if not MachineShutdown.wait_value(
                'SI-Glob:DI-BbBProc-V:FBCTRL', 0, 0.5, 2.0):
            return False
        if not MachineShutdown.wait_value(
                'SI-Glob:DI-BbBProc-L:FBCTRL', 0, 0.5, 2.0):
            return False

        return True

    def s06_beam_kill(self):
        """Mata o feixe utilizando o metodo RFKillbeam."""
        if self._dry_run:
            return

        print('beam_kill...')

        epics.caput('AS-Glob:AP-InjCtrl:RFKillBeam-Cmd', 1)

        # check beam current is close to zero.
        MachineShutdown.wait_value(
            'SI-Glob:AP-CurrInfo:Current-Mon', 0.0, 1.0, 2.0)

        return True

    def s07_disable_ps_triggers(self):
       """Inicialmente desliga os triggers das fontes"""
       if self._dry_run:
           return

       print('disable triggers...')
       # NOTE: need implementation
       return True

    def s08_turn_off_sofbmode(self):
       """Desabilita o modo sofbmode das fontes"""
       if self._dry_run:
           return

       print('turn_off_sofbmode')
       # NOTE: need implementation
       return True

    def s09_set_ps_and_dclinks_to_slowref(self):
    #   Fontes finalizadas, falta implementar os DCLinks.
        """Altera o modo das fontes e dclinks de OpMode para SlowRef."""
        if self._dry_run:
            return

        print('opmode_to_slowref...')

        # Altera o modo das fontes de OpMode para SlowRef
        psnames = PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'OpMode-Sel'
            epics.caput(pvname, 'SlowRef')

        psnames = PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'OpMode-Sel'
            epics.caput(pvname, 'SlowRef')

        psnames = PSSearch.get_psnames(dict(sec='BO', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'OpMode-Sel'
            epics.caput(pvname, 'SlowRef')

        psnames = PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        for psname in psnames:
            if 'FCH' in psname or 'FCV' in psname:
                continue
            pvname = psname + ':' + 'OpMode-Sel'
            epics.caput(pvname, 'SlowRef')

        return True

    def s10_set_ps_current_to_zero(self):
        """Seleciona e zera a corrente de todas as fontes dos aceleradores."""
        if self._dry_run:
            return
        print('s09_set_ps_current_to_zero...')

        timeout = 50  # [s]

        # zero LI ps currents
        psnames = PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero TB ps currents
        psnames = PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero TS ps currents
        psnames = PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero BO ps current
        psnames = PSSearch.get_psnames(dict(sec='BO', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero SI ps current
        psnames = PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'Current-SP'
            pvnames.append(psname + ':' + 'Current-RB')
            epics.caput(pvname, 0.0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_(pvnames, values, tols, timeout):
            return False

        return True

    def s11_reset_ps_and_dclinks(self):
        """Reseta todas as fontes e seus DCLinks."""
        print('s11_reset_ps_and_dclinks')

        # NOTE: Need implementation

        return True

    def s12_turn_ps_off(self):
        """Desliga todas as fontes."""
        timeout = 50  # [s]

        # zero LI ps currents
        psnames = PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero TB ps currents
        psnames = PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero TS ps currents
        psnames = PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero BO ps current
        psnames = PSSearch.get_psnames(dict(sec='BO', dis='PS'))
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        # zero SI ps current
        psnames = PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        pvnames = []
        for psname in psnames:
            pvname = psname + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        return True

    def s13_turn_dclinks_off(self):
        """Desliga os DC links das fontes."""
        timeout = 50  # [s]

        dclinks = set()
        psnames = list()
        psnames = psnames + PSSearch.get_psnames(dict(sec='LI', dis='PS'))
        psnames = psnames + PSSearch.get_psnames(dict(sec='TB', dis='PS'))
        psnames = psnames + PSSearch.get_psnames(dict(sec='TS', dis='PS'))
        psnames = psnames + PSSearch.get_psnames(dict(sec='SI', dis='PS'))
        for psname in psnames:
            dclinks_ = PSSearch.conv_psname_2_dclink(psname)
            if not dclinks_:
                continue
            for dclink in dclinks_:
                psmodel = PSSearch.conv_psname_2_psmodel(dclink)
                if 'REGATRON' not in psmodel:
                    dclinks.add(dclink)

        pvnames = []
        for dclink in dclinks:
            print(dclink)
            pvname = dclink + ':' + 'PwrState-Sel'
            pvnames.append(psname + ':' + 'PwrState-Sts')
            epics.caput(pvname, 0)
        values, tols = [0.0, ] * len(pvnames), [0.2] * len(pvnames)
        if not MachineShutdown.wait_value_set(pvnames, values, tols, timeout):
            return False

        return True

    def s14_modulator_turnoff(self):
        """Desliga os moduladores do Linac desabilitando os botões TrigOut e Charge."""
        if self._dry_run:
            return

        print('modulator_turnoff...')

        # Desliga o botão Charge do modulador 1.
        epics.caput('LI-01:PU-Modltr-1:CHARGE', 0)
        time.sleep(1.0)
        # Desliga o botão TrigOut dp modulador 1.
        epics.caput('LI-01:PU-Modltr-1:TRIGOUT', 0)
        time.sleep(1.0)
        # Desliga o botão Charge do modulador 2.
        epics.caput('LI-01:PU-Modltr-2:CHARGE', 0)
        time.sleep(1.0)
        # Desliga o botão TrigOut dp modulador 2.
        epics.caput('LI-01:PU-Modltr-2:TRIGOUT', 0)

        return True

    def s15_ajust_bias(self):
        """Ajusta a tensão de Bias do canhão em -100V."""
        if self._dry_run:
            return

        print('ajust_bias')

        # Ajusta tensão de Bias em -100V.
        epics.caput('LI-01:EG-BiasPS:voltoutsoft', -100.0)

        return True

    def s16_ajust_filament(self):
        """Ajusta a corrente de filamento em 1A."""
        if self._dry_run:
            return

        # Ajusta corrente de filamento em 1A.
        epics.caput('LI-01:EG-FilaPS:currentoutsoft', 1.0)

        return True

    def s17_borf_turnoff(self):
        """Altera no campo 'Command' para Safe Stop e aguarda executar, depois desliga chave Pin SW e amplificadores DC/DC e 300VDC."""
        if self._dry_run:
            return

        # mensagem a ser impressa na tela para o desligamento da RF do Booster
        print('borf_turnoff...')
        Command = 'Safe Stop'
        # Altera o campo Command para Safe Stop
        epics.caput('BR-RF-DLLRF-01:COMMSTART:S', Command)
        # Aguarda 1s
        time.sleep(1.0)

        print('Desligando a chave PIN...')
        epics.caput('RA-RaBO01:RF-LLRFPreAmp:PinSwDsbl-Cmd', 1)
        time.sleep(1.0)

        print('Desligando os Amplificador DC/DC...')
        epics.caput('RA-ToBO:RF-SSAmpTower:PwrCnvDsbl-Sel', 1)
        time.sleep(1.0)

        print('Desligando os Amplificador 300VDC...')
        epics.caput('RA-ToBO:RF-ACDCPanel:300VdcDsbl-Sel', 1)
        time.sleep(1.0)

    def s18_sirf_turnoff(self):
        """Ajusta a potência da cavidade do anel para 60 mV( inc. rate) e confirma em Reference Amplitude, desabilita o loop de controle, Chave Pin SW e amplificadores DC/TDK e AC TDK."""
        if self._dry_run:
            return True

        print('sirf_turnoff...')
        print('Ajustando a potência da cavidade em 60 mV...')
        #    'SI-Glob:AP-SOFB:CorrPSSOFBWait-Sts',

        init_value = epics.caget('SR-RF-DLLRF-01:mV:AL:REF-SP')
        nrpoints = int(abs(60 - init_value)/10.0)
        values = np.linspace(init_value, 60, nrpoints)
        for value in values:
            print('Amplitude de referẽncia [mV]: ', value)
            epics.caput('SR-RF-DLLRF-01:mV:AL:REF-SP', value)
            time.sleep(0.2)

        print('Desabilitando o loop de controle...')
        epics.caput('SR-RF-DLLRF-01:SL:S', 1)
        time.sleep(1.0)

        print('Desligando a Chave PIN...')
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw1Dsbl-Cmd', 1)
        time.sleep(1.0)
        epics.caput('RA-RaSIA01:RF-LLRFPreAmp-1:PINSw2Dsbl-Cmd', 1)
        time.sleep(1.0)
        print('Desligando os amplificadores DC/TDK...')
        epics.caput('RA-ToSIA01:RF-TDKSource:PwrDCDsbl-Sel', 1)
        time.sleep(1.0)
        epics.caput('RA-ToSIA02:RF-TDKSource:PwrDCDsbl-Sel', 1)
        time.sleep(1.0)
        epics.caput('RA-ToSIA01:RF-ACPanel:PwrACDsbl-Sel', 1)
        time.sleep(1.0)
        epics.caput('RA-ToSIA02:RF-ACPanel:PwrACDsbl-Sel', 1)
        time.sleep(1.0)

    def s19_start_counter(self):
        """verificar visualmente no supervisório se a contagem regressiva para liberar acesso ao túnel iniciou."""
        print('start_counter')
        msg = ('Clique no botão Sirius PPS do supervisório e confirme se a contagem regressiva para liberar acesso ao túnel iniciou')
        input(msg)

        return True
        #    'SI-Glob:AP-SOFB:CorrPSSOFBWait-Sts',

    def s20_free_access(self):
        """Aguardar o contador chegar em 0, após 6 horas, para liberar acesso ao túnel."""
        print('free_access')
        msg = ('Aguarde o contador chegar em 0, após 6 horas, para liberar acessoa ao túnel')
        input(msg)

        return True

    def execute_procedure(self):
        """Executa na sequencia os passos a seguir."""
        if not self.s01_close_gamma_shutter():
            return False
        if not self.s02_macshift_update():
            return False
        if self.s03_ids_parking():
            return False
        if self.s04_sofb_fofb_turnoff():
            return False
        if self.s05_bbb_turnoff():
            return False
        if self.s06_beam_kill():
            return False
        if not self.s06_beam_kill():
            return False
        if not self.s07_disable_ps_triggers():
            return False
        if not self.s08_turn_off_sofbmode():
            return False
        if not self.s09_set_ps_and_dclinks_to_slowref():
            return False
        if not self.s10_set_ps_current_to_zero():
            return False
        if not self.s11_reset_ps_and_dclinks():
            return False
        if not self.s12_turn_ps_off():
            return False
        if not self.s13_turn_dclinks_off():
            return False
        if not self.s14_modulator_turnoff():
            return False
        if not self.s15_ajust_bias():
            return False
        if not self.s16_ajust_filament():
            return False
        if not self.s17_borf_turnoff():
            return False
        if not self.s18_sirf_turnoff():
            return False
        if not self.s19_start_counter():
            return False
        if not self.s20_free_access():
            return False

        return True

    @staticmethod
    def wait_value(pvname, value_target, value_tol, timeout, sleep=0.1):
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
    def wait_value_set(pvnames, value_targets, value_tols, timeout):
        """."""
        pvnames_not_ready = [
            (pvname, idx) for idx, pvname in enumerate(pvnames)]
        strf = (
            'timeout: não foi possível esperar todas as PVs '
            'chegarem aos seus valores de target!')
        time0 = time.time()
        while pvnames_not_ready:
            print(len(pvnames_not_ready))
            for pvname, idx in pvnames_not_ready:
                if MachineShutdown.wait_value(
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
