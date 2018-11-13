#!/usr/bin/env bash

function ioc_cmd {
  bbb=$1
  fac_passwd=$2
  cmd=$3
  printf "<$bbb:$cmd>\n"
  sshpass -p $fac_passwd ssh fac@"$bbb" "sudo systemctl $cmd sirius-bbb-ioc-ps.service"
}


function stop {
  printf "Stopping all power supply IOCs...\n"
  read -s -r -p "fac user's password @ bbbs: " fac_passwd; echo ""
  bbb="bbb-tb-correctors" && ioc_cmd $bbb $fac_passwd stop;
  printf "===========================\n\n"
  bbb="bbb-tb-quadrupoles" && ioc_cmd $bbb $fac_passwd stop;
  printf "===========================\n\n"
  bbb="bbb-tb-dipoles" && ioc_cmd $bbb $fac_passwd stop;
  printf "===========================\n\n"
  bbb="bbb-tb-dclinks" && ioc_cmd $bbb $fac_passwd stop;
  printf "===========================\n\n"
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
