#!/usr/bin/env bash

# --- global variables ---
fac_passwd=
bbbs=("bbb-tb-correctors"
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
  for bbb in "${bbbs[@]}"; do
    ioc_cmd $bbb stop; printf "\n\n"
  done
}

function start {
  printf "Starting all power supply IOCs...\n"
  get_password
  for bbb in "${bbbs[@]}"; do
    ioc_cmd $bbb start; printf "\n\n"
  done
}

function status {
  printf "Status of all power supply IOCs...\n"
  get_password
  for bbb in "${bbbs[@]}"; do
    ioc_cmd $bbb status; printf "\n\n"
  done
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
