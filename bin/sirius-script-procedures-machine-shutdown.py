#!/usr/bin/env python-sirius 
"""."""

import time
import epics


from siriuspy.search import PSSearch


DISABLE_SETPOINTS = False


def wait_value(pvname, value_target, value_tol, timeout, sleep=0.1):
    pvd = epics.PV(pvname)
    time0 = time.time()
    while abs(pvd.value - value_target) > value_tol:
        if time.time() - time0 > timeout:
            if sleep != 0:
                print('timeout: não foi possível esperar a PV {} chegar ao seu valor de target!'.format(pvname))
            return False
        time.sleep(sleep)
    return True


def wait_value_set(pvnames, value_targets, value_tols, timeout):
    pvnames_not_ready = [(pvname, idx) for idx, pvname in enumerate(pvnames)]
    time0 = time.time()
    while pvnames_not_ready:
        for pvname, idx in pvnames_not_ready:
            if wait_value(pvname, value_targets[idx], value_tols[idx], timeout=0, sleep=0.0):
                pvnames_not_ready.remove((pvname, idx))
        if time.time() - time0 > timeout:
            print('timeout: não foi possível esperar todas as PVs chegarem aos seus valores de target!')
            return False
        if pvnames_not_ready:
            time.sleep(0.2)
    return True


def s01_macshift_update():
    """Altera o modo do Turno de operação."""
    if DISABLE_SETPOINTS:
        return
    print('macshift_update...')  # mensagem a ser impressa na tela com a alteração do Turno

    maintenance = 5
    epics.caput('AS-Glob:AP-MachShift:Mode-Sel', maintenance)  # Executa a PV em questão alterando para o modo maintenance

    return wait_value('AS-Glob:AP-MachShift:Mode-Sts', maintenance, 0.5, 2.0)


def s02_close_gamma_shutter():
    """Mensagem na para fechar o Gama."""
    print('close_gamma_shutter...')
    msg = (
        'por favor, feche o gama e em seguida tecle ENTER'
        )
    input(msg)
    
    return True


def s03_ids_parking():
    """."""
    if DISABLE_SETPOINTS:
        return
    print('ids_parking...')

    stop, start = 1, 3
    p1, p2 = 11, 29  # [mm]
    epics.caput('SI-06SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')  # desabilita os shutters das linhas.
    epics.caput('SI-07SP:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl') 
    epics.caput('SI-08SB:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
    epics.caput('SI-09SA:ID-APU22:BeamLineCtrlEnbl-Sel', 'Dsbl')
    epics.caput('SI-11SP:ID-APU58:BeamLineCtrlEnbl-Sel', 'Dsbl')
    epics.sleep(1.0)  # aguarda 1 seg.
    epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', stop)  # para a movimentação dos shhutters.
    epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', stop)
    epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', stop)
    epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', stop)
    epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', stop)
    time.sleep(1.0)
    epics.caput('SI-06SB:ID-APU22:Phase-SP', p1)  # seta a phase para 11.
    epics.caput('SI-07SP:ID-APU22:Phase-SP', p1)
    epics.caput('SI-08SB:ID-APU22:Phase-SP', p1)
    epics.caput('SI-09SA:ID-APU22:Phase-SP', p1)
    epics.caput('SI-11SP:ID-APU58:Phase-SP', p2)  # seta a phase para 29.
    time.sleep(1.0)
    epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', start)  # movimenta os Onduladores para a posição escolhida
    epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', start)

    pvnames = [
        'SI-06SB:ID-APU22:Phase-Mon',
        'SI-07SP:ID-APU22:Phase-Mon',
        'SI-08SB:ID-APU22:Phase-Mon',
        'SI-09SA:ID-APU22:Phase-Mon',
        'SI-11SP:ID-APU58:Phase-Mon',
    ]
    value_targets = [p1, p1, p1, p1, p2]
    value_tols = [0.1, 0.1, 0.1, 0.1, 0.1]
    return wait_value_set(pvnames, value_targets, value_tols, timeout=30)


def s04_sofb_turnoff():
    """Desliga o SOFB."""
    if DISABLE_SETPOINTS:
        return
    print('sofb_turnoff...')

    epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)  # desliga correção de órbita automática
    epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBWait-Sel', 0)  # desliga o sinal Wait
    epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sel', 0)  # desliga o sinal Enable
    epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)  # altera o estado do sinal de Sync para OFF

    pvnames = [
        'SI-Glob:AP-SOFB:LoopState-Sts',
        'SI-Glob:AP-SOFB:CorrPSSOFBWait-Sts',
        'SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sts',
        'SI-Glob:AP-SOFB:CorrSync-Sts',
        ]
    value_targets = [0, 0, 0, 0]
    value_tols = [0.5, 0.5, 0.5, 0.5]
    return wait_value_set(pvnames, value_targets, value_tols, 2.0)


def s05_bbb_turnoff():
    """Desabilita o bbb Hor, Vert e Long."""
    if DISABLE_SETPOINTS:
        return
    print('bbb_turnoff...')

    epics.caput('SI-Glob:DI-BbBProc-H:FBCTRL', 0)
    epics.caput('SI-Glob:DI-BbBProc-V:FBCTRL', 0)
    epics.caput('SI-Glob:DI-BbBProc-L:FBCTRL', 0)

    if not wait_value('SI-Glob:DI-BbBProc-H:FBCTRL', 0, 0.5, 2.0):
        return False
    if not wait_value('SI-Glob:DI-BbBProc-V:FBCTRL', 0, 0.5, 2.0):
        return False
    if not wait_value('SI-Glob:DI-BbBProc-L:FBCTRL', 0, 0.5, 2.0):
        return False

    return True


def s06_beam_kill():
    """Mata o feixe utilizando o metodo RFKillbeam."""
    if DISABLE_SETPOINTS:
        return
    print('beam_kill...')

    epics.caput('AS-Glob:AP-InjCtrl:RFKillBeam-Cmd', 1)

    # check beam current is close to zero.
    wait_value('SI-Glob:AP-CurrInfo:Current-Mon', 0.0, 1.0, 2.0)
    
    return True


def s07_config_timing():
    """."""
    if DISABLE_SETPOINTS:
        return False
    print('config timing...')

    return True


def s08_opmode_to_slowref():
    """Altera o modo das fontes de OpMode para SlowRef."""
    if DISABLE_SETPOINTS:
        return False
    print('opmode_to_slowref...')

    # Altera o modo das fontes de OpMode para SlowRef
    psnames = PSSearch.get_psnames(dict(sec='TB'))
    for psname in psnames:
        pvname = psname + ':' + 'OpMode-Sel'
        epics.caput(pvname, 'SlowRef')
        return True


def s09_zero_current():
    """Seleciona e zera a corrente de todas as fontes dos aceleradores."""
    if DISABLE_SETPOINTS:
        return False
    print('s09_zero_current...')

    # zero LI ps currents
    psnames = PSSearch.get_psnames(dict(sec='LI'))
    pvnames = []
    for psname in psnames:
        pvname = psname + ':' + 'Current-SP'
        pvnames.append(psname + ':' + 'Current-RB')
        epics.caput(pvname, 0.0)
    if not wait_value_set(pvnames, [0.0, ] * len(pvnames), [0.2] * len(pvnames)):
        return False

    # zero TB ps currents
    psnames = PSSearch.get_psnames(dict(sec='TB'))
    pvnames = []
    for psname in psnames:
        pvname = psname + ':' + 'Current-SP'
        pvnames.append(psname + ':' + 'Current-RB')
        epics.caput(pvname, 0.0)
    if not wait_value_set(pvnames, [0.0, ] * len(pvnames), [0.2] * len(pvnames)):
        return False

    # zero TS ps currents
    psnames = PSSearch.get_psnames(dict(sec='TS'))
    for psname in psnames:
        pvname = psname + ':' + 'Current-SP'
        pvnames.append(psname + ':' + 'Current-RB')
        epics.caput(pvname, 0.0)
    if not wait_value_set(pvnames, [0.0, ] * len(pvnames), [0.2] * len(pvnames)):
        return False

    # zero BO ps current
    psnames = PSSearch.get_psnames(dict(sec='BO'))
    for psname in psnames:
        pvname = psname + ':' + 'Current-SP'
        pvnames.append(psname + ':' + 'Current-RB')
        epics.caput(pvname, 0.0)
    if not wait_value_set(pvnames, [0.0, ] * len(pvnames), [0.2] * len(pvnames)):
        return False

    # zero SI ps current
    psnames = PSSearch.get_psnames(dict(sec='SI'))
    for psname in psnames:
        pvname = psname + ':' + 'Current-SP'
        pvnames.append(psname + ':' + 'Current-RB')
        epics.caput(pvname, 0,0)
    if not wait_value_set(pvnames, [0.0, ] * len(pvnames), [0.2] * len(pvnames)):
        return False

    return True


def s10_ps_turnoff():
    """Desliga todas as fontes."""
    return True


def s11_dclinks_turnoff():
    """Desliga os DC links das fontes."""
    return True


def s12_modulator_turnoff():
    """Desliga os moduladores do Linac desabilitando os botões TrigOut e Charge."""
    if DISABLE_SETPOINTS:
        return
    print('modulator_turnoff...')

    epics.caput('LI-01PU:Modltr-1:CHARGE', 0)  # Desliga o botão Charge do modulador 1.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-1:TRIGOUT', 0)  # Desliga o botão TrigOut dp modulador 1.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-2:CHARGE', 0)  # Desliga o botão Charge do modulador 2.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-2:TRIGOUT', 0)  # Desliga o botão TrigOut dp modulador 2.

    return True


def s13_ajust_bias():
    """Ajusta a tensão de Bias do canhão em -100V."""
    if DISABLE_SETPOINTS:
        return
    print('ajust_bias')
    epics.caput('LI-01:EG-BiasPS:voltoutsoft',-100.0) #Ajusta tensão de Bias em -100V.
    epics.sleep(1.0)

    return True


def s14_ajust_filament():
    """Ajusta a corrente de filamento em 1A."""
    if DISABLE_SETPOINTS:
        return

    epics.caput('LI-01:EG-FilaPS:currentoutsoft',1.0) #Ajusta corrente de filamento em 1A.
    epics.sleep(1.0)

    return True


def s15_borf_turnoff():
    """Altera no campo 'Command' para Safe Stop e aguarda executar, depois desliga chave Pin SW e amplificadores DC/DC e 300VDC."""
    return True


def s16_sirf_turnoff():
    """Ajusta a potência da cavidade do anel para 60mV( inc. rate) e confirma em Reference Amplitude, desabilita o loop de controle, Chave Pin SW e amplificadores DC/DC e AC TDK."""
    return True


def s17_start_counter():
    """verificar visualmente no supervisório se a contagem regressiva para liberar acesso ao túnel iniciou."""
    print('start_counter')
    msg = ('Clique no botão Sirius PPS do supervisório e confirme se a contagem regressiva para liberar acesso ao túnel iniciou')
    input(msg)

    return True


def s18_free_access():
    """Aguardar o contador chegar em 0, após 6 horas, para liberar acesso ao túnel."""
    print('free_access')
    msg = ('Aguarde o contador chegar em 0, após 6 horas, para liberar acessoa ao túnel')
    input(msg)

    return True


def execute_procedure():
    """Executa na sequencia os passos a seguir."""
    s01_macshift_update()
    s02_close_gamma_shutter()
    s03_ids_parking()
    s04_sofb_turnoff()
    s05_bbb_turnoff()
    if not s06_beam_kill():
        return
    s07_config_timing()    
    s08_opmode_to_slowref()
    s09_zero_current()
    s10_ps_turnoff()
    s11_dclinks_turnoff()
    s12_modulator_turnoff()
    s13_ajust_bias()
    s14_ajust_filament()
    s15_borf_turnoff()
    s16_sirf_turnoff()
    s17_start_counter()
    s18_free_access()


if __name__ == '__main__':
    """."""
    execute_procedure()