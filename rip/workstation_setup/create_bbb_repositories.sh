#!/bin/bash

set -e
set -x

if [ ! -d /home/sirius/bbb-repositories ]; then
    sudo mkdir /home/sirius/bbb-repositories
fi

cd /home/sirius/bbb-repositories
if [ ! -d ./dev-packages ]; then
    git clone https://github.com/lnls-sirius/dev-packages
fi

if [ ! -d ./machine-applications ]; then
    git clone https://github.com/lnls-sirius/machine-applications
fi
if [ ! -d ./mathphys ]; then 
    git clone https://github.com/lnls-fac/mathphys
fi

sudo chown -R sirius:sirius /home/sirius/bbb-repositories
