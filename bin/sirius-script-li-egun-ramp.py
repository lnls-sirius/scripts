#!/usr/bin/env python-sirius
"""."""

import time as _time
from datetime import timedelta as _timedelta
from threading import Thread as _Thread
import numpy as _np
from epics import PV as _PV


class Egun:
    MULTIBUNCH = 0
    SINGLEBUNCH = 1

    def __init__(self):
        self.pv_hv_volt_sp = _PV('LI-01:EG-HVPS:voltoutsoft')
        self.pv_hv_volt_rb = _PV('LI-01:EG-HVPS:voltinsoft')
        self.pv_hv_curlim_sp = _PV('LI-01:EG-HVPS:currentoutsoft')
        self.pv_hv_curleak_mon = _PV('LI-01:EG-HVPS:currentinsoft')
        self.pv_hv_enbl_sp = _PV('LI-01:EG-HVPS:enable')
        self.pv_hv_enbl_rb = _PV('LI-01:EG-HVPS:enstatus')
        self.pv_hv_switch_sp = _PV('LI-01:EG-HVPS:switch')
        self.pv_hv_switch_rb = _PV('LI-01:EG-HVPS:swstatus')

        self.pv_fila_cur_sp = _PV('LI-01:EG-FilaPS:currentoutsoft')
        self.pv_fila_cur_rb = _PV('LI-01:EG-FilaPS:currentinsoft')
        self.pv_fila_volt_mon = _PV('LI-01:EG-FilaPS:voltinsoft')
        self.pv_fila_switch_sp = _PV('LI-01:EG-FilaPS:switch')
        self.pv_fila_switch_rb = _PV('LI-01:EG-FilaPS:swstatus')

        self.pv_bias_volt_sp = _PV('LI-01:EG-BiasPS:voltoutsoft')
        self.pv_bias_volt_rb = _PV('LI-01:EG-BiasPS:voltinsoft')
        self.pv_bias_cur_mon = _PV('LI-01:EG-BiasPS:currentinsoft')
        self.pv_bias_switch_sp = _PV('LI-01:EG-BiasPS:switch')
        self.pv_bias_switch_rb = _PV('LI-01:EG-BiasPS:swstatus')

        self.pv_pulse_power_sp = _PV('LI-01:EG-PulsePS:poweroutsoft')
        self.pv_pulse_power_rb = _PV('LI-01:EG-PulsePS:powerinsoft')

        self.pv_mult_sel_sp = _PV('LI-01:EG-PulsePS:multiselect')
        self.pv_mult_sel_rb = _PV('LI-01:EG-PulsePS:multiselstatus')
        self.pv_mult_swt_sp = _PV('LI-01:EG-PulsePS:multiswitch')
        self.pv_mult_swt_rb = _PV('LI-01:EG-PulsePS:multiswstatus')

        self.pv_sngl_sel_sp = _PV('LI-01:EG-PulsePS:singleselect')
        self.pv_sngl_sel_rb = _PV('LI-01:EG-PulsePS:singleselstatus')
        self.pv_sngl_swt_sp = _PV('LI-01:EG-PulsePS:singleswitch')
        self.pv_sngl_swt_rb = _PV('LI-01:EG-PulsePS:singleswstatus')

        self.pv_sys_start_sp = _PV('LI-01:EG-System:start')
        self.pv_sys_valve_mon = _PV('LI-01:EG-Valve:status')
        self.pv_sys_gate_mon = _PV('LI-01:EG-Gate:status')
        self.pv_sys_vacuum_mon = _PV('LI-01:EG-Vacuum:status')

        self.pv_trig_state_sp = _PV('LI-01:EG-TriggerPS:enable')
        self.pv_trig_state_rb = _PV('LI-01:EG-TriggerPS:status')
        self.pv_trig_allow_mon = _PV('LI-01:EG-TriggerPS:allow')

        self.pv_mps_permit = _PV('LA-CN:H1MPS-1:GunPermit')
        self.pv_vacuum_ccg1 = _PV('LA-VA:H1VGC-01:RdPrs-1')

        self.names = ['LA-CN:H1MPS-1:CCG1', 'LA-CN:H1MPS-1:CCG2']
        self.pvs_mps_resets = []
        self.pvs_mps_status_raw = []
        self.pvs_mps_status_proc = []
        for name in self.names:
            self.pvs_mps_resets.append(_PV(name + 'Warn_R'))
            self.pvs_mps_status_raw.append(_PV(name + 'Warn_I'))
            self.pvs_mps_status_proc.append(_PV(name + 'Warn_L'))

        self.opmode = self.MULTIBUNCH
        self.goal_volt = 0.0
        self.goal_pressure = 1.0e-9
        self.fila_curr = 0.0
        self._fila_ramp_dur = 10  # min
        self.bias_volt = -60
        self.leak_curr = 0.0
        self.beam_pulse = True

        self.fila_ishot = False

        self.total_duration = -1
        self._stop_running = False
        self._thread = _Thread(target=self._set_stop, daemon=True)
        self._thread.start()

    def _set_stop(self):
        t0 = _time.time()
        while not (0 < self.total_duration < ((_time.time()-t0)/60)):
            _time.sleep(2)
        self._stop_running = True

    def test_egun(self):
        """."""
        time_off = [
            1, 5, 10, 20, 30, 60, 120, 180, 240, 300, 360, 16*60]  # in minutes
        time_on = len(time_off) * [20, ]  # in minutes

        for ton, toff in zip(time_on, time_off):
            if self._stop_running:
                print("Time's up!!")
                return
            print('Turning Egun OFF!')
            self.control_egun(turn_on=False)

            print('Waiting {0:.1f} minutes'.format(toff))
            for i in range((toff*60)):  # convert to seconds
                dur = str(_timedelta(minutes=toff-i/60)).split('.')[0]
                print('Remaining Time {0:s}'.format(dur), end='\r')
                _time.sleep(1)
            print(90*' ')

            if not self._check_ok():
                print('Error, some problem happened.')
                self.quit()
                return

            print('Turning Egun ON!')
            if self.keep_egun_on(period=ton):
                self.quit()
                return
            print('\n')

    def keep_egun_on(self, nrattempts=100, period=-1):
        """."""
        for i in range(nrattempts):
            print('ATTEMPT {0:04d}'.format(i))

            for _ in range(3):
                self._reset_interlocks()
                if self._check_ok():
                    break
                print('Error, I will try again!')
            else:
                print('Error, could not reset all interlocks.')
                return 1

            self.control_egun()

            max_hv = 0
            tini = _time.time()
            while self._check_ok():
                if self._stop_running:
                    print("Time's up!!")
                    return 0
                max_hv = max(max_hv, self.pv_hv_volt_rb.value)
                _time.sleep(0.1)
                tfin = _time.time()
                dur = (tfin-tini)/60
                if 0 < period < dur:
                    print(
                        'Success! No vacuum breakdown in the last ' +
                        '{0:.1f} minutes'.format(period))
                    return 0
                else:
                    if period >= 0:
                        dur = str(_timedelta(minutes=period - dur))
                        dur = dur.split('.')[0]
                        print('Remaining Time: {0:s}'.format(dur), end='\r')
                    else:
                        dur = str(_timedelta(minutes=dur)).split('.')[0]
                        print('Elapsed Time: {0:s}'.format(dur), end='\r')
            print()

            strtime = _time.strftime('%Y-%m-%d %H:%M:%S', _time.localtime())
            print('{0:s} --> Vacuum Interlock!'.format(strtime))
            print('Max HV was {0:.4f}\n'.format(max_hv))
        print('Problem! Too many vacuum breakdowns.')
        return 1

    def control_egun(self, turn_on=True):
        """."""
        print('Preparing Egun')
        self.pv_bias_volt_sp.value = self.bias_volt  # 3nC

        self.pv_trig_state_sp.value = self.beam_pulse if turn_on else False
        if self.pv_hv_enbl_rb.value == 0:
            self.pv_hv_enbl_sp.value = 1
        self.pv_hv_curlim_sp.value = self.leak_curr

        cnt = 0
        std = '    '
        while self.pv_vacuum_ccg1.value > self.goal_pressure:
            if not cnt:
                print('Waiting for vacuum recovery. Over pressure: ')
            cnt += 1
            std += '{0:.3f} '.format(
                self.pv_vacuum_ccg1.value/self.goal_pressure)
            print(std, end='\r')
            if not cnt % 10:
                std = '    '
                print()
            _time.sleep(2)
        print()
        volt = self.goal_volt if turn_on else 0.0
        print('Setting HV from {0:.2f} to {1:.2f} kV'.format(
            self.pv_hv_volt_rb.value, volt))

        self.set_fila_current(self.fila_curr)
        self.set_hv_volt(volt)

    def set_hv_volt(self, val):
        npts = 20
        duration = 60 * 10
        ini_val = 0  # self.pv_hv_volt_rb.value
        npts = int(npts * abs(val-ini_val)/90)
        if npts <= 0:
            return
        if npts < 2:
            self.pv_hv_volt_sp.value = val
            return
        duration = duration * abs(val-ini_val)/90
        x = _np.linspace(0, 1, npts)
        y = self._get_ramp(x, val, False)
        # y = _np.linspace(ini_val, val, npts)

        t_inter = duration / (npts-1)
        print('Starting HV ramp to {0:.3f} kV.'.format(val))
        self.pv_hv_volt_sp.value = y[0]
        for i, cur in enumerate(y[1:]):
            dur = str(_timedelta(seconds=duration - i*t_inter)).split('.')[0]
            print('RemTime: {0:s}  HV: {1:.3f} kV'.format(dur, cur), end='\r')
            self.pv_hv_volt_sp.value = cur
            _time.sleep(t_inter)
            if not self._check_ok():
                return
        print('HV Ready!' + 40*' ')

    def set_fila_current(self, val):
        cond = abs(self.pv_fila_cur_rb.value - val) < 0.07
        cond &= abs(self.pv_fila_cur_sp.value - val) < 1e-4
        if cond:
            print('Filament is already at {0:.3f}'.format(val))
            self.pv_fila_cur_sp.value = val
            self.fila_ishot = True
            return

        isfast = val < 0.7 or self.fila_ishot
        if isfast:
            duration = 5
            npts = 10
        else:
            duration = self._fila_ramp_dur * 60
            npts = 100
        x = _np.linspace(0, 1, npts)
        y = self._get_ramp(x, val, isfast)

        t_inter = duration / (npts-1)

        strg = 'fast' if isfast else 'slow'
        print('Starting {0:s} filament ramp to {1:.3f}.'.format(strg, val))
        self.pv_fila_cur_sp.value = y[0]
        for i, cur in enumerate(y[1:]):
            dur = str(_timedelta(seconds=duration - i*t_inter)).split('.')[0]
            print('RemTime: {0:s}  Curr: {1:.3f} A'.format(dur, cur), end='\r')
            _time.sleep(t_inter)
            self.pv_fila_cur_sp.value = cur
        print('Filament Ready!' + 40*' ')
        self.fila_ishot = True

    def _get_ramp(self, x, val, isfast):
        if isfast:
            y = x.copy()
        else:
            y = 1 - (1-x)**3
            # y = 1 - (1-x)**2
            # y = _np.sqrt(1 - (1-x)**2)
            # y = _np.sin(2*np.pi * x/4)
        return y*val

    def quit(self):
        """."""
        t0 = _time.time()
        while True:
            print('\a', end='\r')  # make a sound
            if _time.time()-t0 > 10:
                break
        print('I quit!')

    def turn_system_off(self):
        print('Turning System off!')
        print('  Disable Pulses')
        self.pv_trig_state_sp.value = 0

        self.pv_mult_swt_sp.value = 0
        self.pv_sngl_swt_sp.value = 0
        self._wait(
            [self.pv_mult_swt_rb, self.pv_sngl_swt_rb],
            [0, 0], ['equal', 'equal'])
        self.pv_mult_sel_sp.value = 0
        self.pv_sngl_sel_sp.value = 0
        self._wait(
            [self.pv_mult_sel_rb, self.pv_sngl_sel_rb],
            [0, 0], ['equal', 'equal'])

        print('  Zero HV and filament')
        self.pv_hv_volt_sp.value = 0.0
        self.set_fila_current(0.0)
        self._wait(
            [self.pv_hv_volt_rb, self.pv_fila_cur_rb],
            [5, 0.2], ['less', 'less'])
        self.pv_bias_volt_sp.value = 0.0
        self._wait([self.pv_bias_volt_rb, ], [-3, ], ['more', ])

        print('  Turn off HV')
        self.pv_hv_enbl_sp.value = 0
        self._wait([self.pv_hv_enbl_rb, ], [0, ], ['equal', ])
        self.pv_hv_switch_sp.value = 0
        self._wait([self.pv_hv_switch_rb, ], [0, ], ['equal', ])

        print('  Turn off Filament')
        self.pv_fila_switch_sp.value = 0
        self._wait([self.pv_fila_switch_rb, ], [0, ], ['equal', ])
        print('  Turn off Bias')
        self.pv_bias_switch_sp.value = 0
        self._wait([self.pv_bias_switch_rb, ], [0, ], ['equal', ])

        print('  Turn off System')
        self.pv_sys_start_sp.value = 0
        _time.sleep(1)
        print('System Off!')

    def turn_system_on(self):
        if self.pv_sys_start_sp.value == 1:
            print('System is Already On')
            return
        print('Turning System on!')
        print('  Start System')
        self.pv_sys_start_sp.value = 1
        _time.sleep(3)
        print('  Turn on Bias')
        self.pv_bias_switch_sp.value = 1
        self._wait([self.pv_bias_switch_rb, ], [1, ], ['equal', ])
        print('  Turn on Filament')
        self.pv_fila_switch_sp.value = 1
        self._wait([self.pv_fila_switch_rb, ], [1, ], ['equal', ])

        print('  Set Bias Voltage')
        self.pv_bias_volt_sp.value = self.bias_volt
        self._wait(
            [self.pv_bias_volt_rb, ], [self.bias_volt*0.9, ], ['less', ])
        print('  Set Filament')
        self.set_fila_current(self.fila_curr)
        self._wait(
            [self.pv_fila_cur_rb, ], [self.fila_curr*0.9, ], ['more', ])
        print('  Turn on HV')
        self.pv_hv_switch_sp.value = 1
        self._wait([self.pv_hv_switch_rb, ], [1, ], ['equal', ])
        self.pv_hv_enbl_sp.value = 1
        self._wait([self.pv_hv_enbl_rb, ], [1, ], ['equal', ])
        print('  Set HV')
        self.pv_hv_curlim_sp.value = self.leak_curr
        self.set_hv_volt(self.goal_volt)
        # self._wait(
        #     [self.pv_hv_volt_rb, ], [self.goal_volt*0.9, ], ['more', ])

        st = '  Turn on Pulse PS for '
        st += 'MultiBunch' if self.opmode == self.MULTIBUNCH else 'SingleBunch'
        print(st)
        val = 1 if self.opmode == self.MULTIBUNCH else 0
        self.pv_mult_sel_sp.value = val
        self.pv_sngl_sel_sp.value = not val
        self._wait(
            [self.pv_mult_sel_rb, self.pv_sngl_sel_rb, ],
            [val, not val, ], ['equal', 'equal'])
        self.pv_mult_swt_sp.value = val
        self.pv_sngl_swt_sp.value = not val
        self._wait(
            [self.pv_mult_swt_rb, self.pv_sngl_swt_rb, ],
            [val, not val, ], ['equal', 'equal'])
        print('System On!')

    def put_system_standby(self):
        print('Putting System in Standby!')
        self.pv_sys_start_sp.value = 1
        self.pv_trig_state_sp.value = 0
        self.pv_mult_swt_sp.value = 0
        self.pv_sngl_swt_sp.value = 0
        self._wait(
            [self.pv_mult_swt_rb, self.pv_sngl_swt_rb, ],
            [0, 0], ['equal', 'equal'])
        self.pv_mult_sel_sp.value = 0
        self.pv_sngl_sel_sp.value = 0
        self._wait(
            [self.pv_mult_sel_rb, self.pv_sngl_sel_rb, ],
            [0, 0], ['equal', 'equal'])

        print('  Turning off HV')
        self.pv_hv_volt_sp.value = 0.0
        self._wait([self.pv_hv_volt_rb, ], [5, ], ['less', ])
        self.pv_hv_enbl_sp.value = 0
        self._wait([self.pv_hv_enbl_rb, ], [0, ], ['equal', ])
        self.pv_hv_switch_sp.value = 0
        self._wait([self.pv_hv_switch_rb, ], [0, ], ['equal', ])

        print('  Turning on Bias and Filament')
        self.pv_bias_switch_sp.value = 1
        self.pv_fila_switch_sp.value = 1
        self._wait(
            [self.pv_bias_switch_rb, self.pv_fila_switch_rb],
            [1, 1], ['equal', 'equal'])
        self.pv_bias_volt_sp.value = -60.0
        self._wait([self.pv_bias_volt_rb, ], [-55, ], ['less', ])
        self.set_fila_current(1.1)
        self._wait([self.pv_fila_cur_rb, ], [1, ], ['more', ])

    def _wait(self, pvlist, vallist, oprlist):
        oprdic = {
            'equal': lambda x, y: x.value is not None and x.value == y,
            'less': lambda x, y: x.value is not None and x.value < y,
            'more': lambda x, y: x.value is not None and x.value > y}
        while True:
            allok = True
            for pv, val, opr in zip(pvlist, vallist, oprlist):
                allok &= oprdic[opr](pv, val)
            if allok:
                break
            _time.sleep(0.1)

    def _reset_interlocks(self):
        """."""
        print('Reseting interlocks...')
        _time.sleep(1)
        for i in range(len(self.pvs_mps_resets)):
            rst = self.pvs_mps_resets[i]
            inn = self.pvs_mps_status_raw[i]
            out = self.pvs_mps_status_proc[i]
            while inn.value != 0:
                _time.sleep(0.5)
            for _ in range(20):
                rst.value = 1
                _time.sleep(0.5)
                rst.value = 0
                if out.value == 0:
                    break

    def _check_ok(self):
        """."""
        isok = [out.value == 0 for out in self.pvs_mps_status_proc]
        allok = all(isok)
        allok &= self.pv_mps_permit.value == 1
        if self.beam_pulse:
            allok &= self.pv_trig_allow_mon.value == 1
        allok &= self.pv_sys_valve_mon.value == 1
        allok &= self.pv_sys_gate_mon.value == 1
        allok &= self.pv_sys_vacuum_mon.value == 1
        return allok


if __name__ == '__main__':
    import argparse as _argparse

    parser = _argparse.ArgumentParser(description="Egun control script.")

    opts = ['filaramp', 'keepon', 'test', 'sysoff', 'syson', 'standby']

    parser.add_argument(
        'dowhat', type=str, help="Choose what to do.", choices=opts)
    parser.add_argument(
        '-c', '--current', type=float, default=1.35,
        help='Which current to put in the filament in A. (1.35 A)')
    parser.add_argument(
        '-v', '--volt', type=float, default=90,
        help='Which Voltage to put in the HV in kV. (90 A)')
    parser.add_argument(
        '-b', '--bias', type=float, default=-33,
        help='Which Voltage to put in Bias in V. (-38 A)')
    parser.add_argument(
        '-l', '--leak', type=float, default=20,
        help='Maximum Leak current allowed in uA. (8 uA)')
    parser.add_argument(
        '-p', '--pressure', type=float, default=8e-9,
        help='Pressure bellow which HV is set, in mBar. (8e-9 mBar)')
    parser.add_argument(
        '-d', '--duration', type=float, default=-1,
        help='How long should it last in minutes.' +
        'Put negative for infinity (-1)')
    parser.add_argument(
        '-n', '--nrattempts', type=int, default=100,
        help='Number of times to try to reset Egun when in keepon mode' +
        ' (100 attempts).')
    parser.add_argument(
        '-f', '--filahot', action='store_true', default=False,
        help="Whether egun's filament is hot (Default = False).")
    parser.add_argument(
        '--nobeam', action='store_true', default=False,
        help="pass this argument if you don't want beam.")

    args = parser.parse_args()
    egun = Egun()
    egun.fila_curr = max(min(args.current, 1.54), 0.0)
    egun.total_duration = args.duration
    egun.goal_volt = args.volt  # [kV]
    egun.goal_pressure = min(max(3.0e-9, args.pressure), 10e-9)  # in mBar
    egun.bias_volt = max(min(args.bias, -20), -110)  # -38 V --> 3 nC
    egun.leak_curr = min(max(0, args.leak), 20) * 1e-3  # mA
    egun.fila_ishot = args.filahot
    egun.beam_pulse = not args.nobeam
    if args.dowhat == opts[0]:
        egun.set_fila_current(egun.fila_curr)
    elif args.dowhat == opts[1]:
        nrtimes = max(min(1000, args.nrattempts), 1)
        if egun.keep_egun_on(nrattempts=nrtimes, period=-1):
            egun.quit()
        # egun.turn_system_off()
    elif args.dowhat == opts[2]:
        egun.test_egun()
    elif args.dowhat == opts[3]:
        egun.turn_system_off()
    elif args.dowhat == opts[4]:
        egun.turn_system_on()
    elif args.dowhat == opts[5]:
        egun.put_system_standby()
