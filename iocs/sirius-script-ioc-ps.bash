#!/usr/bin/env bash

# --- global variables ---
fac_passwd=
bbbs=("bbb-tb-correctors"
      "bbb-tb-quadrupoles"
      "bbb-tb-dipoles"
      "bbb-as-dclinks")

# --- aux functions ---

function get_password {
  read -s -r -p "fac user's password @ bbbs: " fac_passwd; echo ""
}

function contains {
  list=$1
  str=$2
  [[ $1 =~ (^|[[:space:]])$2($|[[:space:]]) ]] && r=0 || r=1
  return $r
}

function ioc_cmd {
  bbb=$1
  cmd=$2
  printf "=== $bbb : $cmd ===\n"
  sshpass -p $fac_passwd ssh fac@"$bbb" "sudo systemctl $cmd sirius-bbb-ioc-ps.service"
}

function list {
  printf "Listing beaglebones...\n"
  for bbb in "${bbbs[@]}"; do
    ip=`getent hosts $bbb | awk '{ print $1 }'`
    printf ". $ip : $bbb\n"
  done
}

function ping_bbb {
  printf "Pinging beaglebones...\n"
  printf "\n\n"
  nr_oks=0
  for bbb in "${bbbs[@]}"; do
    printf "=== $bbb ===\n"
    ping -q -c 2 -W 1 $bbb && let "nr_oks++"
    printf "\n"
  done
  if [ "$nr_oks" != "${#bbbs[@]}" ]; then
    printf "\e[1;31mAt least one beaglebone is not pinging!\e[0m\n"
  else
    printf "\e[1;32mAll beaglebones are pinging!\e[0m\n"
  fi
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
  printf "\e[1;37mNAME\e[0m\n"
  printf "       sirius-script-ioc-ps.bash - control Sirius power supply ioc processes\n"
  printf "\n"
  printf "\e[1;37mSINOPSIS\e[0m\n"
  printf "       \e[1;37msirius-script-ioc-ps.bash\e[0m [OPTION]...\n"
  printf "\n"
  printf "\e[1;37mDESCRIPTION\e[0m\n"
  printf "       Script used to interact and control Sirius power supply ioc processes\n"
  printf "\n"
  printf "       \e[1;37mhelp\e[0m     print this help\n"
  printf "\n"
  printf "       \e[1;37mstop\e[0m     stop all running power supply IOCs\n"
  printf "\n"
  printf "       \e[1;37mstart\e[0m    start all power supply IOCs\n"
  printf "\n"
  printf "       \e[1;37mstatus\e[0m   print status of all power supply IOCs\n"
  printf "\n"
  printf "       \e[1;37mlist\e[0m     list all beaglebones with corresponding IPs\n"
  printf "\n"
  printf "       \e[1;37mping\e[0m     ping all beaglebones\n"
  printf "\n"
  printf "\e[1;37mAUTHOR\e[0m\n"
  printf "       Written by X. Resende, FACS-LNLS.\n"
}

function run {
  arg1=$1
  arg1=${arg1/--/}
  arg1=${arg1/-/}
  if [ -z "$arg1" ]; then
    print_help
  elif [ "$arg1" == "stop" ]; then
    stop
  elif [ "$arg1" == "start" ]; then
    start
  elif [ "$arg1" == "status" ]; then
    status
  elif [ "$arg1" == "ping" ]; then
    ping_bbb
  elif [ "$arg1" == "list" ]; then
    list
  else
    print_help
  fi
}

# --- run script ---

run "$@"
