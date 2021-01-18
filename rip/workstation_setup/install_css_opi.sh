#!/bin/bash

set -e

opi=$1

if [ $opi = pulsed ]; then
    GCO=/home/sirius/.con
    ESS=/home/sirius/.ess-studio-con-SPIxCONV/CSS

    if [ ! -d $GCO/SPIxCONV ]; then
        sudo -u sirius mkdir -p $GCO
        cd $GCO
        sudo -u sirius git clone https://github.com/lnls-sirius/SPIxCONV
    else
        echo 'SPIxCONV already cloned.'
    fi

    sudo -u sirius mkdir -p $ESS
    sudo ln -sf $GCO/SPIxCONV/software/CSS $ESS/con-epp-opi

    echo 'OPI for pulsed power supplies installed.'
else
    echo "Instructions for $opi not found."
fi
