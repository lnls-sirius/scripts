#!/usr/bin/env bash

# This script installs other admin scripts.
# It should be manually installed and executed as sudo.

function get_timestamp {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo $timestamp
}

function get_tmpdir {
  timestamp=$(get_timestamp)
  prefix=$1
  if [[ -z "$prefix" ]]; then
    tmpdir="/tmp/sirius-script-"$timestamp
  else
    tmpdir="/tmp/sirius-script-"$prefix"-"$timestamp
  fi
  echo $tmpdir
}

function run {
  tmpdir=$(get_tmpdir repos-install-pristine)
  mkdir -p $tmpdir
  cd $tmpdir
  git clone https://github.com/lnls-sirius/scripts.git
  cd scripts
  make install-pristine
}


run
