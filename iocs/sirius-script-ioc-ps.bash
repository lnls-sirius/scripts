#!/usr/bin/env bash

# --- global variables ---
fac_passwd=
bbbs = (
  "bbb-tb-correctors"
  "bbb-tb-quadrupoles"
  "bbb-tb-dipoles"
  "bbb-as-dclinks")

# --- aux functions ---

function ioc_cmd {
  bbb=$1
  cmd=$2
  printf "=== $bbb : $cmd ===\n"
  sshpass -p $fac_passwd ssh fac@"$bbb" "sudo systemctl $cmd sirius-bbb-ioc-ps.service"
}

function get_password {
  read -s -r -p "fac user's password @ bbbs: " fac_passwd; echo ""
}

function stop {
  printf "Stopping all power supply IOCs...\n"
  get_password
  bbb="bbb-tb-correctors" && ioc_cmd $bbb stop; printf "\n\n"
  bbb="bbb-tb-quadrupoles" && ioc_cmd $bbb stop; printf "\n\n"
  bbb="bbb-tb-dipoles" && ioc_cmd $bbb stop; printf "\n\n"
  bbb="bbb-as-dclinks" && ioc_cmd $bbb stop; printf "\n\n"
}

function start {
  printf "Starting all power supply IOCs...\n"
  get_password
  bbb="bbb-tb-correctors" && ioc_cmd $bbb $fac_passwd start; printf "\n\n"
  bbb="bbb-tb-quadrupoles" && ioc_cmd $bbb $fac_passwd start; printf "\n\n"
  bbb="bbb-tb-dipoles" && ioc_cmd $bbb $fac_passwd start; printf "\n\n"
  bbb="bbb-as-dclinks" && ioc_cmd $bbb $fac_passwd start; printf "\n\n"
}

function status {
  printf "Status of all power supply IOCs...\n"
  get_password
  for bbb in "${bbbs[@]}"; do
    ioc_cmd $bbb status; printf "\n\n"
  fi
}

function print_help {
  printf "help not implemented!\n"
}

function run {
  if [ -z "$1" ]; then
    print_help
  elif [ "$1" == "stop" ]; then
    stop
  elif [ "$1" == "start" ]; then
    start
  elif [ "$1" == "status" ]; then
    status
  else
    print_help
  fi
}

# --- run scripts ---

run "$@"
