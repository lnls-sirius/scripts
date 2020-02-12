#!/bin/bash

# Install Pcaspy and PyEpics

# Run with sudo -HE

set -e
set -x

sudo apt-get install -y swig

export EPICS_BASE=/opt/epics/base
export EPICS_HOST_ARCH=linux-x86_64

sudo -HE pip-sirius install pyepics==3.3.1
sudo -HE pip-sirius install pcaspy==0.7.1
exit 0
