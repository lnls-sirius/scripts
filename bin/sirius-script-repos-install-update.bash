#!/usr/bin/env bash

# This script is used either in 'sirius-script-repos-installfile should be installed in /usr/local/etc manually in prestine desktops

source ./sirius-script-bbb-utils.bash
trap _abort SIGINT;

function run {
  tmpdir=$(get_tmpdir repos-install-update)
  mkdir -p $tmpdir
  cd $tmpdir
  git clone https://github.com/lnls-sirius/scripts.git
  cd scripts
  make install-repos-install
}

run
