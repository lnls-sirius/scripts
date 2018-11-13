#!/usr/bin/env bash

function ioc_cmd {
  bbb=$1
  fac_passwd=$2
  cmd=$3
  sshpass -p $fac_passwd ssh fac@"$bbb" "sudo systemctl $cmd sirius-bbb-ioc-ps.service"
}


function stop {
  printf "Stopping all power supply IOCs...\n"
  read -s -r -p "fac user's password @ bbbs: " fac_passwd; echo ""
  bbb="bbb-tb-correctors" && printf "$bbb" && ioc_cmd $bbb $fac_passwd stop && printf "\n"
  bbb="bbb-tb-quadrupoles" && printf "$bbb" && ioc_cmd $bbb $fac_passwd stop && printf "\n"
  bbb="bbb-tb-dipoles" && printf "$bbb" && ioc_cmd $bbb $fac_passwd stop && printf "\n"
  bbb="bbb-tb-dclinks" && printf "$bbb" && ioc_cmd $bbb $fac_passwd stop && printf "\n"
}

function print_help {
  printf "help...\n"
}

if [ -z "$1" ]; then
  print_help
elif [ "$1" == "stop" ]; then
  stop
else
  print_help
fi
