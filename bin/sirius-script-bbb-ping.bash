#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;

function run {
  if [ $# -eq 0 ]; then
    lbbbs=${bbbs[@]}
  else
    lbbbs=$@
  fi
  # echo ${lbbbs[@]}
  cmd_bbb_ping ${lbbbs[@]}
}

run $@
