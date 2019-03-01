#!/usr/bin/env bash

# --- global variables ---

cmd=$1
linac_passwd=$2
desktop=desktop3
maiocs=("sirius-ioc-tb-ma-dipoles.service"
        "sirius-ioc-tb-ma-quadrupoles.service"
        "sirius-ioc-tb-ma-correctors.service"
        "sirius-ioc-bo-ma-correctors-01.service"
        "sirius-ioc-bo-ma-correctors-02.service"
        "sirius-ioc-bo-ma-correctors-03.service"
        "sirius-ioc-bo-ma-correctors-04.service"
        "sirius-ioc-bo-ma-correctors-05.service"
        "sirius-ioc-bo-ma-correctors-06.service"
        "sirius-ioc-bo-ma-correctors-07.service"
        "sirius-ioc-bo-ma-correctors-08.service"
        "sirius-ioc-bo-ma-correctors-09.service"
        "sirius-ioc-bo-ma-correctors-10.service"
        "sirius-ioc-bo-ma-correctors-11.service"
        "sirius-ioc-bo-ma-correctors-12.service"
        "sirius-ioc-bo-ma-correctors-13.service")


# --- aux functions ---

function get_password {
  if [ -z "$linac_passwd" ]; then
    read -s -r -p "linac user's password @ desktop3: " linac_passwd; echo ""
  fi
}

function contains {
  list=$1
  str=$2
  [[ $1 =~ (^|[[:space:]])$2($|[[:space:]]) ]] && r=0 || r=1
  return $r
}

function ioc_cmd {
  maioc=$1
  cmd=$2
  printf "=== $maioc : $cmd ===\n"
  sshpass -p $linac_passwd ssh linac@"$desktop" "sudo systemctl $cmd $maioc"
}

function list {
  printf "Listing MA iocs...\n"
  for maioc in "${maiocs[@]}"; do
    printf ". $maioc\n"
  done
}

function ping_desktop1 {
  printf "Pinging desktop3...\n"
  printf "\n\n"
  nr_oks=0
  ping -q -c 2 -W 1 $desktop && let "nr_oks++"
  if [ "$nr_oks" != "1" ]; then
    printf "\e[1;31m$desktop is not pinging!\e[0m\n"
  else
    printf "\e[1;32m$desktop is pinging!\e[0m\n"
  fi
}

function stop {
  printf "Stopping all MA IOCs...\n"
  get_password
  for maioc in "${maiocs[@]}"; do
    ioc_cmd $maioc stop; printf "\n\n"
  done
}

function start {
  printf "Starting all MA IOCs...\n"
  get_password
  for maioc in "${maiocs[@]}"; do
    ioc_cmd $maioc start; printf "\n\n"
  done
}

function status {
  printf "Status of all MA IOCs...\n"
  get_password
  for maioc in "${maiocs[@]}"; do
    ioc_cmd $maioc status; printf "\n\n"
  done
}

function print_help {
  printf "\e[1;37mNAME\e[0m\n"
  printf "       sirius-script-ioc-ma.bash - control Sirius MA ioc processes\n"
  printf "\n"
  printf "\e[1;37mSINOPSIS\e[0m\n"
  printf "       \e[1;37msirius-script-ioc-ma.bash\e[0m [OPTION]...\n"
  printf "\n"
  printf "\e[1;37mDESCRIPTION\e[0m\n"
  printf "       Script used to interact and control Sirius magnet ioc processes\n"
  printf "\n"
  printf "       \e[1;37mhelp\e[0m     print this help\n"
  printf "\n"
  printf "       \e[1;37mstop\e[0m     stop all running MA IOCs\n"
  printf "\n"
  printf "       \e[1;37mstart\e[0m    start all MA IOCs\n"
  printf "\n"
  printf "       \e[1;37mstatus\e[0m   print status of all MA IOCs\n"
  printf "\n"
  printf "       \e[1;37mlist\e[0m     list all MA IOC classes\n"
  printf "\n"
  printf "       \e[1;37mping\e[0m     ping desktop1\n"
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
    ping_desktop1
  elif [ "$arg1" == "list" ]; then
    list
  else
    print_help
  fi
}


# --- run script ---

run $cmd
