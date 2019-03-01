#!/usr/bin/env bash

source ./sirius-script-bbb-utils.bash
trap _abort SIGINT;

function run {
  if [ $# -eq 0 ]; then
    lbbbs=${bbbs[@]}
  else
    lbbbs=$@
  fi
  # echo ${lbbbs[@]}
  cmd_reboot ${lbbbs[@]}
}

run $@
