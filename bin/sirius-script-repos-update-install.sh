#!/usr/bin/env bash

# This file should be installed in /usr/local/etc manually in prestine desktops

timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
tmpdir="/tmp/deploy-update-install-"$timestamp
mkdir $tmpdir

cd $tmpdir
git clone https://github.com/lnls-sirius/scripts.git
cd scripts
make install-update-install
