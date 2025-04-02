#!/usr/bin/env python-sirius

from siriushla.widgets import SiriusMainWindow
import subprocess

import sys, time
from pickle import TRUE

from random import randint

from turtle import right
import epics
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

PORT_NUMBER_MKS_SENSOR = 5002
PORT_NUMBER_ION_PUMP = 5004

current_datetime = QDateTime.currentDateTime()

## Lista dos IPs das BBBs referente as eletrônicas de sensores (SENSOR) e fontes de bomba iônica (PUMP)

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


## Lista das PVs dos medidores de pressões do vácuo

PVNAMES_VAC = [
    'SI-01C1:VA-CCG-BG:Pressure-Mon', 'SI-01C3:VA-CCG-BG:Pressure-Mon', 'SI-01SAFE:VA-CCG-MD:Pressure-Mon', 'SI-01C2FE:VA-CCG-MD:Pressure-Mon', 'SI-01BCFE:VA-CCG-MD:Pressure-Mon', 
    'SI-01SA:VA-CCG-BG:Pressure-Mon', 'SI-02SB:VA-CCG-BG:Pressure-Mon', 'SI-02C1:VA-CCG-BG:Pressure-Mon', 'SI-02C3:VA-CCG-BG:Pressure-Mon', 'SI-02SBFE:VA-CCG-MD:Pressure-Mon', 
    'SI-02BCFE:VA-CCG-MD:Pressure-Mon', 'SI-03SP:VA-CCG-BG:Pressure-Mon',  'SI-03C1:VA-CCG-BG:Pressure-Mon','SI-03C3:VA-CCG-BG:Pressure-Mon', 'SI-03SPFE:VA-CCG-MD:Pressure-Mon', 
    'SI-03C2FE:VA-CCG-MD:Pressure-Mon', 'SI-03BCFE:VA-CCG-MD:Pressure-Mon', 'SI-04SB:VA-CCG-BG:Pressure-Mon', 'SI-04C1:VA-CCG-BG:Pressure-Mon', 'SI-04C3:VA-CCG-BG:Pressure-Mon', 
    'SI-04SBFE:VA-CCG-MD:Pressure-Mon', 'SI-04BCFE:VA-CCG-MD:Pressure-Mon', 'SI-05SA:VA-CCG-BG:Pressure-Mon',  'SI-05C1:VA-CCG-BG:Pressure-Mon', 'SI-05C3:VA-CCG-BG:Pressure-Mon', 
    'SI-05SAFE:VA-CCG-MD:Pressure-Mon', 'SI-05BCFE:VA-CCG-MD:Pressure-Mon', 'SI-06SB:VA-CCG-BG:Pressure-Mon', 'SI-06C1:VA-CCG-BG:Pressure-Mon', 'SI-06C3:VA-CCG-BG:Pressure-Mon', 
    'SI-06SBFE:VA-CCG-MD:Pressure-Mon', 'SI-06BCFE:VA-CCG-MD:Pressure-Mon', 'SI-07SP:VA-CCG-BG:Pressure-Mon', 'SI-07C1:VA-CCG-BG:Pressure-Mon', 'SI-07C3:VA-CCG-BG:Pressure-Mon', 
    'SI-07SP:VA-CCG-BG:Pressure-Mon', 'SI-07SPFE:VA-CCG-MD:Pressure-Mon', 'SI-07BCFE:VA-CCG-MD:Pressure-Mon', 'SI-08SB:VA-CCG-BG:Pressure-Mon', 'SI-08C1:VA-CCG-BG:Pressure-Mon', 
    'SI-08C3:VA-CCG-BG:Pressure-Mon', 'SI-08SBFE:VA-CCG-MD:Pressure-Mon', 'SI-08BCFE:VA-CCG-MD:Pressure-Mon', 'SI-09SA:VA-CCG-BG:Pressure-Mon', 'SI-09C1:VA-CCG-BG:Pressure-Mon', 
    'SI-09SAFE:VA-CCG-MD:Pressure-Mon', 'SI-09BCFE:VA-CCG-MD:Pressure-Mon', 'SI-10SB:VA-CCG-BG:Pressure-Mon', 'SI-10C1:VA-CCG-BG:Pressure-Mon', 'SI-10C3:VA-CCG-BG:Pressure-Mon', 
    'SI-10SBFE:VA-CCG-MD:Pressure-Mon', 'SI-10BCFE:VA-CCG-MD:Pressure-Mon', 'SI-11SP:VA-CCG-BG:Pressure-Mon', 'SI-11C1:VA-CCG-BG:Pressure-Mon', 'SI-11C3:VA-CCG-BG:Pressure-Mon', 
    'SI-11SPFE:VA-CCG-MD:Pressure-Mon', 'SI-11C2FE:VA-CCG-MD:Pressure-Mon', 'SI-11BCFE:VA-CCG-MD:Pressure-Mon', 'SI-12SB:VA-CCG-BG:Pressure-Mon', 'SI-12C1:VA-CCG-BG:Pressure-Mon',
    'SI-12C3:VA-CCG-BG:Pressure-Mon', 'SI-12SBFE:VA-CCG-MD:Pressure-Mon', 'SI-12BCFE:VA-CCG-MD:Pressure-Mon', 'SI-13SA:VA-CCG-BG:Pressure-Mon',  'SI-13C1:VA-CCG-BG:Pressure-Mon',
    'SI-13C3:VA-CCG-BG:Pressure-Mon', 'SI-13SAFE:VA-CCG-MD:Pressure-Mon', 'SI-13C2FE:VA-CCG-MD:Pressure-Mon', 'SI-13BCFE:VA-CCG-MD:Pressure-Mon', 'SI-14SB:VA-CCG-BG:Pressure-Mon',
    'SI-14C1:VA-CCG-BG:Pressure-Mon', 'SI-14C3:VA-CCG-BG:Pressure-Mon', 'SI-14SBFE:VA-CCG-MD:Pressure-Mon', 'SI-14BCFE:VA-CCG-MD:Pressure-Mon', 'SI-15SP:VA-CCG-BG:Pressure-Mon',
    'SI-15C1:VA-CCG-BG:Pressure-Mon', 'SI-15C3:VA-CCG-BG:Pressure-Mon', 'SI-15SPFE:VA-CCG-MD:Pressure-Mon', 'SI-15C2FE:VA-CCG-MD:Pressure-Mon', 'SI-15BCFE:VA-CCG-MD:Pressure-Mon',
    'SI-16SB:VA-CCG-BG:Pressure-Mon', 'SI-16C1:VA-CCG-BG:Pressure-Mon', 'SI-16C3:VA-CCG-BG:Pressure-Mon', 'SI-16SBFE:VA-CCG-MD:Pressure-Mon', 'SI-16BCFE:VA-CCG-MD:Pressure-Mon',
    'SI-17SA:VA-CCG-BG:Pressure-Mon', 'SI-17C1:VA-CCG-BG:Pressure-Mon', 'SI-17C3:VA-CCG-BG:Pressure-Mon', 'SI-17SAFE:VA-CCG-MD:Pressure-Mon', 'SI-17BCFE:VA-CCG-MD:Pressure-Mon',
    'SI-18SB:VA-CCG-BG:Pressure-Mon', 'SI-18C1:VA-CCG-BG:Pressure-Mon', 'SI-18C3:VA-CCG-BG:Pressure-Mon', 'SI-18SBFE:VA-CCG-MD:Pressure-Mon', 'SI-18BCFE:VA-CCG-MD:Pressure-Mon',
    'SI-19SP:VA-CCG-BG:Pressure-Mon', 'SI-19C1:VA-CCG-BG:Pressure-Mon', 'SI-19C3:VA-CCG-BG:Pressure-Mon', 'SI-19SPFE:VA-CCG-MD:Pressure-Mon', 'SI-19C2FE:VA-CCG-MD:Pressure-Mon',
    'SI-19BCFE:VA-CCG-MD:Pressure-Mon', 'SI-20SB:VA-CCG-BG:Pressure-Mon', 'SI-20C1:VA-CCG-BG:Pressure-Mon', 'SI-20C3:VA-CCG-BG:Pressure-Mon', 'SI-20SBFE:VA-CCG-MD:Pressure-Mon',
    'SI-20BCFE:VA-CCG-MD:Pressure-Mon',
    ]


## Lista das PVs dos ajustes de tensão das fontes de bomba iônicas

VLT_CHNLL = [
    'SI-01C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-01C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-01SAFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-01C2FE:VA-SIP150-MD:VoltageTarget-SP', 'SI-01BCFE:VA-SIP150-MD:VoltageTarget-SP', 
    'SI-01SA:VA-SIP20-BG:VoltageTarget-SP', 'SI-02SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-02C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-02C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-02SBFE:VA-SIP150-MD:VoltageTarget-SP', 
    'SI-02BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-03SP:VA-SIP20-BG:VoltageTarget-SP', 'SI-03C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-03C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-03SPFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-03C2FE:VA-SIP150-MD:VoltageTarget-SP', 'SI-03BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-04SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-04C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-04C3:VA-SIP20-BG:VoltageTarget-SP', 
    'SI-04SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-04BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-05SA:VA-SIP20-BG:VoltageTarget-SP', 'SI-04C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-04C3:VA-SIP20-BG:VoltageTarget-SP',
    'SI-05SAFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-05BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-06SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-06C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-06C3:VA-SIP20-BG:VoltageTarget-SP', 
    'SI-06SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-06BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-07SP:VA-SIP20-BG:VoltageTarget-SP', 'SI-07C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-07C3:VA-SIP20-BG:VoltageTarget-SP',
    'SI-07SP:VA-SIP20-ED:VoltageTarget-SP', 'SI-07SPFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-07BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-08SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-08C1:VA-SIP20-BG:VoltageTarget-SP',
    'SI-08C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-08SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-08BCFE:VA-SIP150-MD:VoltageTarget-SP',  'SI-09SA:VA-SIP20-BG:VoltageTarget-SP', 'SI-09C1:VA-SIP20-BG:VoltageTarget-SP',
    'SI-09SAFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-09BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-10SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-10C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-10C3:VA-SIP20-BG:VoltageTarget-SP',
    'SI-10SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-10BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-11SP:VA-SIP20-BG:VoltageTarget-SP', 'SI-11C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-11C3:VA-SIP20-BG:VoltageTarget-SP',
    'SI-11SPFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-11C2FE:VA-SIP150-MD:VoltageTarget-SP', 'SI-11BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-12SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-12C1:VA-SIP20-BG:VoltageTarget-SP',
    'SI-12C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-12SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-12BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-13SA:VA-SIP20-BG:VoltageTarget-SP', 'SI-13C1:VA-SIP20-BG:VoltageTarget-SP',
    'SI-13C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-13SAFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-13C2FE:VA-SIP150-MD:VoltageTarget-SP', 'SI-13BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-14SB:VA-SIP20-BG:VoltageTarget-SP',
    'SI-14C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-14C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-14SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-14BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-15SP:VA-SIP20-BG:VoltageTarget-SP',
    'SI-15C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-15C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-15SPFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-15C2FE:VA-SIP150-MD:VoltageTarget-SP', 'SI-15BCFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-16SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-16C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-16C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-16SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-16BCFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-17SA:VA-SIP20-BG:VoltageTarget-SP', 'SI-17C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-17C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-17SAFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-17BCFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-18SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-18C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-18C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-18SBFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-18BCFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-19SP:VA-SIP20-BG:VoltageTarget-SP', 'SI-19C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-19C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-19SPFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-19C2FE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-19BCFE:VA-SIP150-MD:VoltageTarget-SP', 'SI-20SB:VA-SIP20-BG:VoltageTarget-SP', 'SI-20C1:VA-SIP20-BG:VoltageTarget-SP', 'SI-20C3:VA-SIP20-BG:VoltageTarget-SP', 'SI-20SBFE:VA-SIP150-MD:VoltageTarget-SP',
    'SI-20BCFE:VA-SIP150-MD:VoltageTarget-SP',
    ]


## Lista das PVs dos ajustes de modo (mode), Step ou Fixed das fontes de bomba iônicas

RFRC_CHNLL =[
    'SI-RA01:VA-SIPC-04:Step-SP', 'SI-RA01:VA-SIPC-04:Step-SP', 'SI-RA01:VA-SIPC-06:Step-SP', 'SI-RA01:VA-SIPC-06:Step-SP', 'SI-RA01:VA-SIPC-06:Step-SP', 
    'SI-RA01:VA-SIPC-07:Step-SP', 'SI-RA02:VA-SIPC-04:Step-SP', 'SI-RA02:VA-SIPC-04:Step-SP', 'SI-RA02:VA-SIPC-04:Step-SP', 'SI-RA02:VA-SIPC-05:Step-SP', 
    'SI-RA02:VA-SIPC-05:Step-SP', 'SI-RA03:VA-SIPC-03:Step-SP', 'SI-RA03:VA-SIPC-03:Step-SP', 'SI-RA03:VA-SIPC-03:Step-SP', 'SI-RA03:VA-SIPC-05:Step-SP', 
    'SI-RA03:VA-SIPC-05:Step-SP', 'SI-RA03:VA-SIPC-05:Step-SP', 'SI-RA04:VA-SIPC-03:Step-SP', 'SI-RA04:VA-SIPC-03:Step-SP', 'SI-RA04:VA-SIPC-03:Step-SP', 
    'SI-RA04:VA-SIPC-04:Step-SP', 'SI-RA04:VA-SIPC-04:Step-SP', 'SI-RA05:VA-SIPC-03:Step-SP', 'SI-RA05:VA-SIPC-03:Step-SP', 'SI-RA05:VA-SIPC-03:Step-SP', 
    'SI-RA05:VA-SIPC-05:Step-SP', 'SI-RA05:VA-SIPC-05:Step-SP', 'SI-RA06:VA-SIPC-03:Step-SP', 'SI-RA06:VA-SIPC-03:Step-SP', 'SI-RA06:VA-SIPC-03:Step-SP', 
    'SI-RA06:VA-SIPC-04:Step-SP', 'SI-RA06:VA-SIPC-04:Step-SP', 'SI-RA07:VA-SIPC-03:Step-SP', 'SI-RA07:VA-SIPC-03:Step-SP', 'SI-RA07:VA-SIPC-03:Step-SP', 
    'SI-RA07:VA-SIPC-04:Step-SP', 'SI-RA07:VA-SIPC-05:Step-SP', 'SI-RA07:VA-SIPC-05:Step-SP', 'SI-RA08:VA-SIPC-03:Step-SP', 'SI-RA08:VA-SIPC-03:Step-SP', 
    'SI-RA08:VA-SIPC-03:Step-SP', 'SI-RA08:VA-SIPC-04:Step-SP', 'SI-RA08:VA-SIPC-04:Step-SP', 'SI-RA09:VA-SIPC-03:Step-SP', 'SI-RA09:VA-SIPC-03:Step-SP', 
    'SI-RA09:VA-SIPC-05:Step-SP', 'SI-RA09:VA-SIPC-05:Step-SP', 'SI-RA10:VA-SIPC-03:Step-SP', 'SI-RA10:VA-SIPC-03:Step-SP', 'SI-RA10:VA-SIPC-03:Step-SP', 
    'SI-RA10:VA-SIPC-04:Step-SP', 'SI-RA10:VA-SIPC-04:Step-SP', 'SI-RA11:VA-SIPC-03:Step-SP', 'SI-RA11:VA-SIPC-03:Step-SP', 'SI-RA11:VA-SIPC-03:Step-SP',  
    'SI-RA11:VA-SIPC-05:Step-SP', 'SI-RA11:VA-SIPC-05:Step-SP', 'SI-RA11:VA-SIPC-05:Step-SP', 'SI-RA12:VA-SIPC-03:Step-SP', 'SI-RA12:VA-SIPC-03:Step-SP', 
    'SI-RA12:VA-SIPC-03:Step-SP', 'SI-RA12:VA-SIPC-04:Step-SP', 'SI-RA12:VA-SIPC-04:Step-SP', 'SI-RA13:VA-SIPC-03:Step-SP', 'SI-RA13:VA-SIPC-03:Step-SP', 
    'SI-RA13:VA-SIPC-03:Step-SP', 'SI-RA13:VA-SIPC-05:Step-SP', 'SI-RA13:VA-SIPC-05:Step-SP', 'SI-RA13:VA-SIPC-05:Step-SP', 'SI-RA14:VA-SIPC-03:Step-SP', 
    'SI-RA14:VA-SIPC-03:Step-SP', 'SI-RA14:VA-SIPC-03:Step-SP', 'SI-RA14:VA-SIPC-04:Step-SP', 'SI-RA14:VA-SIPC-04:Step-SP', 'SI-RA15:VA-SIPC-03:Step-SP', 
    'SI-RA15:VA-SIPC-03:Step-SP', 'SI-RA15:VA-SIPC-03:Step-SP', 'SI-RA15:VA-SIPC-05:Step-SP', 'SI-RA15:VA-SIPC-05:Step-SP', 'SI-RA15:VA-SIPC-05:Step-SP', 
    'SI-RA16:VA-SIPC-03:Step-SP', 'SI-RA16:VA-SIPC-03:Step-SP', 'SI-RA16:VA-SIPC-03:Step-SP', 'SI-RA16:VA-SIPC-04:Step-SP', 'SI-RA16:VA-SIPC-04:Step-SP', 
    'SI-RA17:VA-SIPC-03:Step-SP', 'SI-RA17:VA-SIPC-03:Step-SP', 'SI-RA17:VA-SIPC-03:Step-SP', 'SI-RA17:VA-SIPC-05:Step-SP', 'SI-RA17:VA-SIPC-05:Step-SP', 
    'SI-RA18:VA-SIPC-03:Step-SP', 'SI-RA18:VA-SIPC-03:Step-SP', 'SI-RA18:VA-SIPC-03:Step-SP', 'SI-RA18:VA-SIPC-04:Step-SP', 'SI-RA18:VA-SIPC-04:Step-SP', 
    'SI-RA19:VA-SIPC-03:Step-SP', 'SI-RA19:VA-SIPC-03:Step-SP', 'SI-RA19:VA-SIPC-03:Step-SP', 'SI-RA19:VA-SIPC-05:Step-SP', 'SI-RA19:VA-SIPC-05:Step-SP', 
    'SI-RA19:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-05:Step-SP', 'SI-RA20:VA-SIPC-06:Step-SP', 
    'SI-RA20:VA-SIPC-06:Step-SP', 
    ]


## Lista das referências dos ajustes de dos canais das fontes de bomba iônicas

FNT_CHNLL_INDC = [
    'SI-RA01:VA-SIPC-04-2', 'SI-RA01:VA-SIPC-04-4', 'SI-RA01:VA-SIPC-06-1', 'SI-RA01:VA-SIPC-06-2', 'SI-RA01:VA-SIPC-06-3', 
    'SI-RA01:VA-SIPC-07-1', 'SI-RA02:VA-SIPC-04-1', 'SI-RA02:VA-SIPC-04-2', 'SI-RA02:VA-SIPC-04-4', 'SI-RA02:VA-SIPC-05-3', 
    'SI-RA02:VA-SIPC-05-4', 'SI-RA03:VA-SIPC-03-1', 'SI-RA03:VA-SIPC-03-2', 'SI-RA03:VA-SIPC-03-4', 'SI-RA03:VA-SIPC-05-1', 
    'SI-RA03:VA-SIPC-05-2', 'SI-RA03:VA-SIPC-05-3', 'SI-RA04:VA-SIPC-03-1', 'SI-RA04:VA-SIPC-03-2', 'SI-RA04:VA-SIPC-03-4', 
    'SI-RA04:VA-SIPC-04-3', 'SI-RA04:VA-SIPC-04-4', 'SI-RA05:VA-SIPC-03-1', 'SI-RA05:VA-SIPC-03-2', 'SI-RA05:VA-SIPC-03-4', 
    'SI-RA05:VA-SIPC-05-1', 'SI-RA05:VA-SIPC-05-3', 'SI-RA06:VA-SIPC-03-1', 'SI-RA06:VA-SIPC-03-2', 'SI-RA06:VA-SIPC-03-4', 
    'SI-RA06:VA-SIPC-04-3', 'SI-RA06:VA-SIPC-04-4', 'SI-RA07:VA-SIPC-03-1', 'SI-RA07:VA-SIPC-03-2', 'SI-RA07:VA-SIPC-03-4', 
    'SI-RA07:VA-SIPC-04-3', 'SI-RA07:VA-SIPC-05-1', 'SI-RA07:VA-SIPC-05-3', 'SI-RA08:VA-SIPC-03-1', 'SI-RA08:VA-SIPC-03-2', 
    'SI-RA08:VA-SIPC-03-4', 'SI-RA08:VA-SIPC-04-3', 'SI-RA08:VA-SIPC-04-4', 'SI-RA09:VA-SIPC-03-1', 'SI-RA09:VA-SIPC-03-2', 
    'SI-RA09:VA-SIPC-05-1', 'SI-RA09:VA-SIPC-05-3', 'SI-RA10:VA-SIPC-03-1', 'SI-RA10:VA-SIPC-03-2', 'SI-RA10:VA-SIPC-03-4', 
    'SI-RA10:VA-SIPC-04-3', 'SI-RA10:VA-SIPC-04-4', 'SI-RA11:VA-SIPC-03-1', 'SI-RA11:VA-SIPC-03-2', 'SI-RA11:VA-SIPC-03-4',  
    'SI-RA11:VA-SIPC-05-1', 'SI-RA11:VA-SIPC-05-2', 'SI-RA11:VA-SIPC-05-3', 'SI-RA12:VA-SIPC-03-1', 'SI-RA12:VA-SIPC-03-2', 
    'SI-RA12:VA-SIPC-03-4', 'SI-RA12:VA-SIPC-04-3', 'SI-RA12:VA-SIPC-04-4', 'SI-RA13:VA-SIPC-03-1', 'SI-RA13:VA-SIPC-03-2', 
    'SI-RA13:VA-SIPC-03-4', 'SI-RA13:VA-SIPC-05-1', 'SI-RA13:VA-SIPC-05-2', 'SI-RA13:VA-SIPC-05-3', 'SI-RA14:VA-SIPC-03-1', 
    'SI-RA14:VA-SIPC-03-2', 'SI-RA14:VA-SIPC-03-4', 'SI-RA14:VA-SIPC-04-3', 'SI-RA14:VA-SIPC-04-4', 'SI-RA15:VA-SIPC-03-1', 
    'SI-RA15:VA-SIPC-03-2', 'SI-RA15:VA-SIPC-03-4', 'SI-RA15:VA-SIPC-05-1', 'SI-RA15:VA-SIPC-05-2', 'SI-RA15:VA-SIPC-05-3', 
    'SI-RA16:VA-SIPC-03-1', 'SI-RA16:VA-SIPC-03-2', 'SI-RA16:VA-SIPC-03-4', 'SI-RA16:VA-SIPC-04-3', 'SI-RA16:VA-SIPC-04-4', 
    'SI-RA17:VA-SIPC-03-1', 'SI-RA17:VA-SIPC-03-2', 'SI-RA17:VA-SIPC-03-4', 'SI-RA17:VA-SIPC-05-1', 'SI-RA17:VA-SIPC-05-3', 
    'SI-RA18:VA-SIPC-03-1', 'SI-RA18:VA-SIPC-03-2', 'SI-RA18:VA-SIPC-03-4', 'SI-RA18:VA-SIPC-04-3', 'SI-RA18:VA-SIPC-04-4', 
    'SI-RA19:VA-SIPC-03-1', 'SI-RA19:VA-SIPC-03-2', 'SI-RA19:VA-SIPC-03-4', 'SI-RA19:VA-SIPC-05-1', 'SI-RA19:VA-SIPC-05-2', 
    'SI-RA19:VA-SIPC-05-3', 'SI-RA20:VA-SIPC-05-1', 'SI-RA20:VA-SIPC-05-2', 'SI-RA20:VA-SIPC-05-4', 'SI-RA20:VA-SIPC-06-3', 
    'SI-RA20:VA-SIPC-06-4', 
    ]


## Classe de execução e ajustes

class MainWindow(QMainWindow):
    """."""
    stopThread = pyqtSignal()
    def __init__(self):
        super().__init__()

        # Criando a janela
        self.setWindowTitle(" - Monitoramento do vácuo (sys) - ")
        self.setGeometry(200, 200, 600, 400)

        # Criando o QTextEdit
        self.log_window = QTextEdit(self)
        self.log_window.setGeometry(10, 10, 500, 300)

        #  Criação dos botões
        self.start_button = QPushButton ('Start', self)
        self.start_button.setGeometry(100, 330, 80, 60)
        self.start_button.clicked.connect(self._launch_monitor_thread)
        
        self.execute_button = QPushButton('Execute!', self)
        self.execute_button.setEnabled(False)
        self.execute_button.setGeometry(200, 330, 80, 60)
        self.execute_button.clicked.connect(self._fix_bi)
        
        self.stop_button = QPushButton('Stop', self)
        self.stop_button.setGeometry(300, 330, 80, 60)
        self.stop_button.clicked.connect(self._stop_monitoring_)
        self._sensors_nok = list()

    #  Função auxiliar para thread de leituras
    def _launch_monitor_thread(self):
        self.start_button.setEnabled(False)
        self._thread = MonitorThread(self)
        self._thread.log_signal.connect(self.log)
        self._thread.nok_signal.connect(self._set_nok_sensors)
        self.stopThread.connect(self._thread.stop_task)
        self._thread.start()
   
    #  Função auxiliar para status dos botões
    def _set_nok_sensors(self, sensors_list):
        self._sensors_nok = sensors_list 
        self.start_button.setEnabled(True)
        self.execute_button.setEnabled(True)
        self.log("Foram encontrados sensores com problemas.")
        current_datetime = QDateTime.currentDateTime()
        formatted_datetime = current_datetime.toString("yyyy-MM-dd - HH:mm:ss")
        self.log(f'Data e hora atuais: {formatted_datetime} hrs')
    
    #  Função para execução do botão de STOP
    def _stop_monitoring_(self):
        self.stopThread.emit()
        self.start_button.setEnabled(True)
        self.log("Monitoramento parado")

    #  Função de ajustes de canais e tensões dos canais das fontes de BI
    def _fix_bi(self):
        if not self._sensors_nok:
            self.log('Não há ajustes a serem feitos.')
            return
        self.execute_button.setEnabled(False)
        self.log('Ajustes iniciados...')
        for sensor in self._sensors_nok:
            value, pvname_vac, fnt_chnll_indc, rfrc_chnll, vlt_chnll = sensor
            self.log('Ajustando canal da fonte referente ao sensor ' + pvname_vac + '...')
            value_fnt = epics.caget(rfrc_chnll)
            print(value_fnt)
            time.sleep(1)
            epics.caput(rfrc_chnll, 0)
            time.sleep(5)
            MainWindow._on_pv_set_(vlt_chnll, 5000)
            time.sleep(15)
            if value <= 5e-9:
                time.sleep(5)
                MainWindow._on_pv_set_(vlt_chnll, 3000)
                time.sleep(5)
                epics.caput(rfrc_chnll, value_fnt)
            self.log(f"PV '{pvname_vac}' atual é '{value}' ")
        self._sensors_nok = list()
        self.log('Ajustes finalizados.')
        self.log('')    

    ### Função para preencher o formulário            
    def initialize_log(self):
        self.log('--- check ION_PUMP ---')
        check1 = MainWindow._check_ping_connection_all_sensors(IP_LIST_ION_PUMP)
        self.log(check1)
        self.log('\n--- check MKS_SENSOR ---')
        check2 = MainWindow._check_ping_connection_all_sensors(IP_LIST_MKS_SENSOR)
        self.log(check2)

    ### Adiciona uma mensagem ao log e atualiza a barra de status
    def log(self, message):
        self.log_window.append(message)
        self.log_window.repaint()

    #  Função para teste de conexão das BBBs por PING
    @staticmethod
    def _check_ping_connection(hostname):
        try:
            _ = subprocess.check_output('ping -c 1 ' + hostname, stderr=subprocess.STDOUT, shell=True)
            return True
        except subprocess.CalledProcessError:
            return False

    # #  Função para teste de conexão dos sensores por PING
    @staticmethod
    def _check_ping_connection_all_sensors(ip_list):
        status_messages = []
        for address in ip_list:
            if MainWindow._check_ping_connection(address) is False:
                status_messages.append('no connection with {}'.format(address))
            else:
                status_messages.append('{} ok'.format(address))
        return '\n'.join(status_messages)

    ## Função para selecionar o canal da fonte
    @staticmethod
    def _cndc_fnt_sp_(fnt_chnll_indc, rfrc_chnll):
        chn = MainWindow._cndc_fnt_(fnt_chnll_indc)
        if chn == '1':
            epics.caput(rfrc_chnll, 1)
        elif chn == '2':
            epics.caput(rfrc_chnll, 2)
        elif chn == '3':
            epics.caput(rfrc_chnll, 4)
        elif chn == '4':
            epics.caput(rfrc_chnll, 8)
        elif chn == '1' and '2':
            epics.caput(rfrc_chnll, 3)
        elif chn == '1' and '3':
            epics.caput(rfrc_chnll, 5)
        elif chn == '2' and '3':
            epics.caput(rfrc_chnll, 6)
        elif chn == '1' and '2' and '3':
            epics.caput(rfrc_chnll, 7)
        elif chn == '1' and '4':
            epics.caput(rfrc_chnll, 9)
        elif chn == '2' and '4':
            epics.caput(rfrc_chnll, 10)
        elif chn == '1' and '2' and '4':
            epics.caput(rfrc_chnll, 11)
        elif chn == '3' and '4':
            epics.caput(rfrc_chnll, 12)
        elif chn == '1' and '3' and '4':
            epics.caput(rfrc_chnll, 13)
        elif chn == '2' and '3' and '4':
            epics.caput(rfrc_chnll, 14)
        elif chn == '1' and '2' and '3' and '4':
            epics.caput(rfrc_chnll, 15)
        else:
            raise Exception('Wrong pv_name_vac')

    ## Função para ajustar as tensões das fontes
    @staticmethod
    def _on_pv_set_(vlt_chnll, value):
        epics.caput(vlt_chnll, value)

    ## Função que retorna o modo (Mode) das fontes para Fixed
    @staticmethod
    def _on_pv_set_fx_rtrn_(rfrc_chnll, value):
            epics.caput(rfrc_chnll, value)


#  Classe de leituras e preenchimento do GUI
class MonitorThread(QThread):
    SENSOR_THRESHOLD = 8e-9  # [mbar]
    log_signal = pyqtSignal(str)
    nok_signal = pyqtSignal(list)


    #  Função auxiliar do status stop, condição falsa
    def __init__(self, parent=None):
        super().__init__(parent)
        self._stop = False

    #  Função auxiliar do status stop, condição verdadeira
    def stop_task(self):
        self._stop = True

    #  Função auxiliar do status do loop de monitoramento (ON)
    def run(self):
        self.monitoring_loop()

    #  Função para execução do loop WHILE
    def monitoring_loop(self):
        cont=0
        self.log_signal.emit("\n--- check ON PV CHANGE ---")
        self.log_signal.emit("Monitoramento iniciado")
        while not self._stop:
            is_ok = self._on_pv_change_()
            if not is_ok:
                self.nok_signal.emit(self._sensors_nok)
                break
            cont +=1
            print('contador', cont)
            time.sleep(2)
    
    ## Função para verificar as pressões e atuar nas fontes de bomba iônica
    def _on_pv_change_(self):
        self._sensors_nok = list()
        for pvname_vac, fnt_chnll_indc, rfrc_chnll, vlt_chnll in zip(PVNAMES_VAC, FNT_CHNLL_INDC, RFRC_CHNLL, VLT_CHNLL):
            value = epics.caget(pvname_vac)
            if value >= MonitorThread.SENSOR_THRESHOLD: ## or pvname_vac in ('SI-20SBFE:VA-CCG-MD:Pressure-Mon'): ##'SI-12C1:VA-CCG-BG:Pressure-Mon', 'SI-13C3:VA-CCG-BG:Pressure-Mon'):
                self.log_signal.emit(f"PV '{pvname_vac}' mudou para '{value}'")
                self._sensors_nok.append((value, pvname_vac, fnt_chnll_indc, rfrc_chnll, vlt_chnll))
        if not self._sensors_nok:
            self.log_signal.emit('As pressões estão OK!')
            return True
        self.log_signal.emit('Deseja executar os ajustes? [botão execute]')

        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    QTimer.singleShot(0, main_window.initialize_log)
    sys.exit(app.exec_())




