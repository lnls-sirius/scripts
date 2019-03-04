#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
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
