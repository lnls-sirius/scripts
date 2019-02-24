#!/usr/bin/env bash

tmpdir=$(mktemp /tmp/deploy-update-instal-XXXXXX)

timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
tmpdir="/tmp/deploy-update-install-"$timestamp
mkdir $tmpdir

cd $tmpdir
git clone https://github.com/lnls-sirius/scripts.git
cp ./scripts/bin/sirius-script-repos-install.sh /usr/local/bin/
chmod 755 /usr/local/bin/sirius-script-repos-install.sh
