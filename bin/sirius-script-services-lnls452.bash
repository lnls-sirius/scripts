#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function run_systemctl {
  cmd=$1
  printf_blue "Runnnig systemctl $cmd for services.\n"
  printf "\n"
  for service in ${services_lnls452[@]}; do
    printf_yellow "$service...\n"
    sudo systemctl $cmd $service
    printf "\n"
  done
}


host=$(hostname)
if [[ "$host" == "lnls452-linux" ]]; then
  run_systemctl $1
else
  get_password sirius lnls452-linux
  sshpass -p $user_passwd ssh -t sirius@lnls452-linux "sudo sirius-script-services-lnls452.bash $1"
fi
