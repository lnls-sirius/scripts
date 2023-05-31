#!/usr/bin/env python-sirius

import numpy as np
import matplotlib.pyplot as plt
from siriuspy.clientarch import PVData, PVDataSet, Time
from siriushla.sirius_application import SiriusApplication
from siriushla.widgets import SiriusMainWindow
import subprocess
import socket
import os
import sys, time
from pickle import TRUE
from datetime import datetime, timedelta
from optparse import Values
from random import randint
from datetime import date
from turtle import right
import epics
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

PORT_NUMBER_MKS_SENSOR = 5002
PORT_NUMBER_ION_PUMP = 5004


MD_STR = [ 
    '01BCFE', '01C2FE', '01SAFE', '02BCFE', '02SBFE',
    '03BCFE', '03C2FE', '03SPFE', '04BCFE', '04SBFE',
    '05BCFE', '05C2FE', '05SAFE', '06BCFE', '06SBFE',
    '07BCFE', '07C2FE', '07SPFE', '08BCFE', '08SBFE',
    '09BCFE', '09C2FE', '09SAFE', '10BCFE', '10SBFE',
    '11BCFE', '11C2FE', '11SPFE', '12BCFE', '12SBFE',
    '13BCFE', '13C2FE', '13SAFE', '14BCFE', '14SBFE',
    '15BCFE', '15C2FE', '15SPFE', '16BCFE', '16SBFE',
    '17BCFE', '17C2FE', '17SAFE', '18BCFE', '18SBFE',
    '19BCFE', '19C2FE', '19SPFE', '20BCFE', '20SBFE',
    ]

BG_STR = [
    '01C1', '01C3', '01SA', '02C1', '02C3',
    '02SB', '03C1', '03C3', '03SP', '04C1',
    '04C3', '04SB', '05C1', '05C3', '05SA',
    '06C1', '06C3', '06SB', '07C1', '07C3',
    '07SP', '08C1', '08C3', '08SB', '09C1',
    '09C3', '09SA', '10C1', '10C3', '10SB',
    '11C1', '11C3', '11SP', '12C1', '12C3',
    '12SB', '13C1', '13C3', '13SA', '14C1',
    '14C3', '14SB', '15C1', '15C3', '15SP',
    '16C1', '16C3', '16SB', '17C1', '17C3',
    '17SA', '18C1', '18C3', '18SB', '19C1',
    '19C3', '19SP', '20C1', '20C3', '20SB',
     ]



    # Listas das PVs de pressão do vácuo

PVNAMES_VAC = \
    ['SI-' + item + ':VA-CCG-MD:Pressure-Mon' for item in MD_STR] + \
    ['SI-' + item + ':VA-CCG-BG:Pressure-Mon' for item in BG_STR]


IP_LIST_MKS_SENSOR = [
         '10.128.101.101', '10.128.102.101', '10.128.103.101', '10.128.104.101', '10.128.105.101',
         '10.128.106.101', '10.128.107.101', '10.128.108.101', '10.128.109.101', '10.128.110.101', 
         '10.128.111.101', '10.128.112.101', '10.128.113.101', '10.128.114.101', '10.128.115.101', 
         '10.128.116.101', '10.128.117.101', '10.128.118.101', '10.128.119.101', '10.128.120.101', 
         ]

IP_LIST_ION_PUMP = [
        '10.128.101.102', '10.128.101.103', '10.128.102.102', '10.128.102.103', '10.128.103.102', 
        '10.128.103.103', '10.128.104.102', '10.128.105.102', '10.128.105.103', '10.128.106.102', 
        '10.128.106.103', '10.128.108.102', '10.128.108.103', '10.128.109.102', '10.128.109.103', 
        '10.128.110.102', '10.128.111.102', '10.128.111.103', '10.128.112.102', '10.128.113.102',
        '10.128.113.103', '10.128.114.102', '10.128.115.102', '10.128.115.103', '10.128.116.102', 
        '10.128.116.103', '10.128.117.102', '10.128.117.103', '10.128.118.102', '10.128.119.102', 
        '10.128.119.103', '10.128.120.102', '10.128.120.103', 
        ]

VLT_FE_STR = [
     '01BCFE', '01C2FE', '01SAFE', '02BCFE', '02SBFE',
     '03BCFE', '03C2FE', '03SPFE', '04BCFE', '04SBFE',
     '05BCFE', '05C2FE', '05SAFE', '06BCFE', '06SBFE',
     '07BCFE', '07C2FE', '07SPFE', '08BCFE', '08SBFE',
     '09BCFE', '09C2FE', '09SAFE', '10BCFE', '10SBFE',
     '11BCFE', '11C2FE', '11SPFE', '12BCFE', '12SBFE',
     '13BCFE', '13C2FE', '13SAFE', '14BCFE', '14SBFE',
     '15BCFE', '15C2FE', '15SPFE', '16BCFE', '16SBFE',
     '17BCFE', '17C2FE', '17SAFE', '18BCFE', '18SBFE',
     '19BCFE', '19C2FE', '19SPFE', '20BCFE', '20SBFE',
     ]

VLT_STR = [
     '01C1', '01C2', '01C3', '01C4', '01M1',
     '01SA', '02C1', '02C2', '02C3', '02C4',
     '02M1', '02SB', '03C1', '03C2', '03C3',
     '03C4', '03M1', '03SP', '04C1', '04C2',
     '04C3', '04C4', '04M1', '04SB', '05C1',
     '05C2', '05C3', '05C4', '05M1', '05SA',
     '06C1', '06C2', '06C3', '06C4', '06M1',
     '06SB', '07C1', '07C2', '07C3', '07C4',
     '07M1', '07SP', '08C1', '08C2', '08C3',
     '08C4', '08M1', '08SB', '09C1', '09C2',
     '09C3', '09C4', '09M1', '09SA', '10C1',
     '10C2', '10C3', '10C4', '10M1', '10SB',
     '11C1', '11C2', '11C3', '11C4', '11M1',
     '11SP', '12C1', '12C2', '12C3', '12C4',
     '12M1', '12SB', '13C1', '13C2', '13C3',
     '13C4', '13M1', '13SA', '14C1', '14C2',
     '14C3', '14C4', '14M1', '14SB', '15C1',
     '15C2', '15C3', '15C4', '15M1', '15SP',
     '16C1', '16C2', '16C3', '16C4', '16M1',
     '16SB', '17C1', '17C2', '17C3', '17C4',
     '17M1', '17SA', '18C1', '18C2', '18C3',
     '18C4', '18M1', '18SB', '19C1', '19C2',
     '19C3', '19C4', '19M1', '19SP', '20C1',
     '20C2', '20C3', '20C4', '20M1', '20SB',
]

VLT_CHNLL = [
    'SI-RA01:VA-SIPC-04:Step-SP', 'SI-RA01:VA-SIPC-05:Step-SP', 'SI-RA01:VA-SIPC-06:Step-SP', 'SI-RA01:VA-SIPC-07:Step-SP', 'SI-RA02:VA-SIPC-04:Step-SP', 
    'SI-RA02:VA-SIPC-05:Step-SP', 'SI-RA02:VA-SIPC-06:Step-SP', 'SI-RA03:VA-SIPC-03:Step-SP', 'SI-RA03:VA-SIPC-04:Step-SP', 'SI-RA03:VA-SIPC-05:Step-SP', 
    'SI-RA04:VA-SIPC-03:Step-SP', 'SI-RA04:VA-SIPC-04:Step-SP', 'SI-RA05:VA-SIPC-03:Step-SP', 'SI-RA05:VA-SIPC-04:Step-SP', 'SI-RA05:VA-SIPC-05:Step-SP',
    'SI-RA06:VA-SIPC-03:Step-SP', 'SI-RA06:VA-SIPC-04:Step-SP', 'SI-RA06:VA-SIPC-05:Step-SP', 'SI-RA07:VA-SIPC-03:Step-SP', 'SI-RA07:VA-SIPC-04:Step-SP',
    'SI-RA07:VA-SIPC-05:Step-SP', 'SI-RA08:VA-SIPC-03:Step-SP', 'SI-RA08:VA-SIPC-04:Step-SP', 'SI-RA08:VA-SIPC-05:Step-SP', 'SI-RA09:VA-SIPC-03:Step-SP',
    'SI-RA09:VA-SIPC-04:Step-SP', 'SI-RA09:VA-SIPC-05:Step-SP', 'SI-RA10:VA-SIPC-03:Step-SP', 'SI-RA10:VA-SIPC-04:Step-SP', 'SI-RA10:VA-SIPC-05:Step-SP',
    'SI-RA11:VA-SIPC-03:Step-SP', 'SI-RA11:VA-SIPC-04:Step-SP', 'SI-RA11:VA-SIPC-05:Step-SP', 'SI-RA12:VA-SIPC-03:Step-SP', 'SI-RA12:VA-SIPC-04:Step-SP',
    'SI-RA13:VA-SIPC-03:Step-SP', 'SI-RA13:VA-SIPC-04:Step-SP', 'SI-RA13:VA-SIPC-05:Step-SP', 'SI-RA14:VA-SIPC-03:Step-SP', 'SI-RA14:VA-SIPC-04:Step-SP',
    'SI-RA15:VA-SIPC-03:Step-SP', 'SI-RA15:VA-SIPC-04:Step-SP', 'SI-RA15:VA-SIPC-05:Step-SP', 'SI-RA16:VA-SIPC-03:Step-SP', 'SI-RA16:VA-SIPC-04:Step-SP', 
    'SI-RA17:VA-SIPC-03:Step-SP', 'SI-RA17:VA-SIPC-04:Step-SP', 'SI-RA17:VA-SIPC-05:Step-SP', 'SI-RA18:VA-SIPC-03:Step-SP', 'SI-RA18:VA-SIPC-04:Step-SP',
    'SI-RA19:VA-SIPC-03:Step-SP', 'SI-RA19:VA-SIPC-04:Step-SP', 'SI-RA19:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-06:Step-SP',
    ]

# Listas das PVs das fontes de bombas iônicas
PVNAMES_VAC_VLT_RB = \
    ['SI-' + item + ':VA-SIP20-BG:VoltageTarget-RB' for item in VLT_STR] + \
    ['SI-' + item + ':VA-SIP150-MD:VoltageTarget-RB' for item in VLT_FE_STR]

PVNAMES_VAC_VLT_SP = \
    ['SI-' + item + ':VA-SIP20-BG:VoltageTarget-SP' for item in VLT_STR] + \
    ['SI-' + item + ':VA-SIP150-MD:VoltageTarget-SP' for item in VLT_FE_STR]


# Função que verifica as medidas de pressões e ajusta as fontes de BI
class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        # Criando o QTextEdit
        self.log_window = QTextEdit()
        self.setCentralWidget(self.log_window)

        # Criando o QStatusBar
        self.statusBar().showMessage('Pronto')
        self.log('--- check ION_PUMP ---')
        check1 = MainWindow._check_ping_connection_all_sensors(IP_LIST_ION_PUMP)
        self.log(check1)
        self.log('--- check MKS_SENSOR ---')
        check2 = MainWindow._check_ping_connection_all_sensors(IP_LIST_MKS_SENSOR)
        self.log(check2)
        self.log('--- check on_pv_change ---')
        check3 = MainWindow._on_pv_change(PVNAMES_VAC)
        self.log(check3)
        
    def log(self, message):
        """ Adiciona uma mensagem ao log e atualiza a barra de status """
        self.log_window.append(message)
        self.statusBar().showMessage(message)
    
    # --- private methods ---

    @staticmethod
    def _on_pv_set_fx(vlt_chnll):
        for pv_name_vac_ in vlt_chnll:
            epics.caput(pv_name_vac_, 0)

    @staticmethod
    def _on_pv_set(pvnames_vac_vlt_sp):
        for pvname_vac_ in pvnames_vac_vlt_sp:
            epics.caput(pvname_vac_, 3000)

    @staticmethod
    def _on_pv_change(pvnames_vac):
        status_messages = []
        for pvname_vac in pvnames_vac:
            value = epics.caget(pvname_vac) 
            if value < 1e-08:
                # on_pv_set_fx(vlt_chnll)
                print(f"PV '{pvname_vac}' mudou para '{value}'")
                status_messages.append(f"PV '{pvname_vac}' mudou para '{value}'")
        return '\n'.join(status_messages)

    @staticmethod
    def _check_ping_connection(hostname):
        try:
            _ = subprocess.check_output('ping -c 1 ' + hostname, stderr=subprocess.STDOUT, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    @staticmethod
    def _check_ping_connection_all_sensors(ip_list):
        status_messages = []
        for address in ip_list:
            if MainWindow._check_ping_connection(address) is False:
                status_messages.append('no connection with {}'.format(address))
            else:
                status_messages.append('{} ok'.format(address))
        return '\n'.join(status_messages)

            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


