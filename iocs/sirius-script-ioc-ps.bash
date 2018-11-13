#!/usr/bin/env bash

function stop_iocs_tb {
  printf "function stop_iocs_tb...\n"
  ssh root@bbb-tb-dipoles ls
}

function iocs_stop {
  printf "iocs_stop...\n"
  read -s -r -p "fac user's password @ bbb: " fac_passwd; echo ""
  echo $fac_passwd
  sshpass -p $fac_passwd ssh fac@bbb-tb-dipoles "sudo systemctl status sirius-bbb-ioc-ps.service"
}

if [ "$1" == "--help" ]; then
  echo "help"
fi

iocs_stop
