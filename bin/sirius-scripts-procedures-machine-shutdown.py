#!/usr/bin/env python-sirius 
"""."""

import time
import epics


USER_SHIFT = True


def s01_macshift_update():
    """Altera o modo do Turno de operação."""
    if USER_SHIFT:
        return
    print('macshift_update...')  # mensagem a ser impressa na tela com a alteração do Turno

    maintenance = 5
    epics.caput('AS-Glob:AP-MachShift:Mode-Sel', maintenance)  # Executa a PV em questão alterando para o modo maintenance

    return True


def close_gamma_shutter():
    """Mensagem na para fechar o Gama."""
    print('close_gamma_shutter...')
    msg = (
        'por favor, feche o gama e em seguida tecle ENTER'
        )
    input(msg)
    
    return True


def ids_parking(): 
    """."""
    if USER_SHIFT:
        return
    print('ids_parking...')

    stop, start = 1, 3
    p1, p2 = 11, 29
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
    epics.caput('SI-06SB:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-07SP:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-08SB:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-09SA:ID-APU22:DevCtrl-Cmd', start)
    epics.caput('SI-11SP:ID-APU58:DevCtrl-Cmd', start)

    # NOTE: implementar espera!

    return True


def sofb_turnoff():
    """Desliga o SOFB."""
    if USER_SHIFT:
        return
    print('sofb_turnoff...')

    epics.caput('SI-Glob:AP-SOFB:LoopState-Sel', 0)  # desliga correção de órbita automática
    epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBWait-Sel', 0)  # desliga o sinal Wait
    epics.caput('SI-Glob:AP-SOFB:CorrPSSOFBEnbl-Sel', 0)  # desliga o sinal Enable
    epics.caput('SI-Glob:AP-SOFB:CorrSync-Sel', 0)  # altera o estado do sinal de Sync para OFF

    return True


def bbb_turnoff():
    """Desabilita o bbb Hor, Vert e Long."""
    if USER_SHIFT:
        return
    print('bbb_turnoff...')

    epics.caput('SI-Glob:DI-BbBProc-H:FBCTRL', 0)
    epics.caput('SI-Glob:DI-BbBProc-V:FBCTRL', 0)
    epics.caput('SI-Glob:DI-BbBProc-L:FBCTRL', 0)

    return True


def beam_kill():
    """Mata o feixe utilizando o metodo RFKillbeam."""
    if USER_SHIFT:
        return
    print('beam_kill...')

    epics.caput('AS-Glob:AP-InjCtrl:RFKillBeam-Cmd', 1)

    # check beam current is close to zero.
    beam_current = epics.PV('SI-Glob:AP-CurrInfo:Current-Mon')
    curr_tol = 1.0  # [mA]
    timeout = 2  # [s]
    time0 = time.time()
    while beam_current.value > curr_tol:
        if time.time() - time0 > timeout:
            print('não foi possível matar o feixe!')
            return False
        time.sleep(0.5)
    
    return True


def config_timmming():
    """Configura timming."""
    return True


def opmode_to_slowref():
    """Altera o modo das fontes de OpMode para SlowRef."""
    return True


def zero_current():
    """Seleciona e zera a corrente de todas as fontes dos aceleradores."""
    return True


def ps_turnoff():
    """Desliga todas as fontes.#desliga todas as fontes."""
    return True


def dclinks_turnoff():
    """Desliga os DC links das fontes."""
    return True


def modulator_turnoff():
    """Desliga os moduladores do Linac desabilitando os botões TrigOut e Charge."""
    if USER_SHIFT:
        return
    print('modulator_turnoff...')

    epics.caput('LI-01PU:Modltr-1:CHARGE',0) #Desliga o botão Charge do modulador 1.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-1:TRIGOUT',0) #Desliga o botão TrigOut dp modulador 1.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-2:CHARGE',0) #Desliga o botão Charge do modulador 2.
    epics.sleep(1.0)
    epics.caput('LI-01PU:Modltr-2:TRIGOUT',0) #Desliga o botão TrigOut dp modulador 2.
    epics.sleep(1.0)

    return True


def ajust_bias():
    """Ajusta a tensão de Bias do canhão em -100V."""
    if USER_SHIFT:
        return
    print('ajust_bias')
    epics.caput('LI-01:EG-BiasPS:voltoutsoft',-100.0) #Ajusta tensão de Bias em -100V.
    epics.sleep(1.0)

    return True


def ajust_filament():
    """Ajusta a corrente de filamento em 1A."""
    if USER_SHIFT:
        return

    epics.caput('LI-01:EG-FilaPS:currentoutsoft',1.0) #Ajusta corrente de filamento em 1A.
    epics.sleep(1.0)

    return True


def borf_turnoff():
    """Altera no campo 'Command' para Safe Stop e aguarda executar, depois desliga chave Pin SW e amplificadores DC/DC e 300VDC."""
    return True


def sirf_turnoff():
    """Ajusta a potência da cavidade do anel para 60mV( inc. rate) e confirma em Reference Amplitude, desabilita o loop de controle, Chave Pin SW e amplificadores DC/DC e AC TDK."""
    return True


def start_counter():
    """verificar visualmente no supervisório se a contagem regressiva para liberar acesso ao túnel iniciou."""
    print('start_counter')
    msg = ('Clique no botão Sirius PPS do supervisório e confirme se a contagem regressiva para liberar acesso ao túnel iniciou')
    input(msg)

    return True


def free_access():
    """Aguardar o contador chegar em 0, após 6 horas, para liberar acesso ao túnel."""
    print('free_access')
    msg('Aguarde o contador chegar em 0, após 6 horas, para liberar acessoa ao túnel')
    input(msg)

    return True


def execute_procedure(): #executa na sequencia os passos acima.
    """."""
    s01_macshift_update()
    s02_close_gamma_shutter()
    s03_ids_parking()
    s04_sofb_turnoff()
    s05_bbb_turnoff()
    if not s06_beam_kill()
        return
    s07_config_timing()    
    s08_opmode_to_slowref()
    s09_zero_current()
    s10_ps_turnoff
    s11_dclinks_turnoff()
    s12_modulator_turnoff()
    s13_ajust_bias()
    ajust_filament()
    borf_turnoff()
    sirf_turnoff()
    start_counter()
    free_access()


if __name__ == '__main__':
    """."""
    execute_procedure()