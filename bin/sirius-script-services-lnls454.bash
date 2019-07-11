#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function print_help {
    printf "NAME\n"
    printf "       sirius-script-services-lnls454.bash - Interact with services in lnls454-linux\n"
    printf "\n"
    printf "SINOPSIS\n"
    printf "       sirius-script-services-lnls454.bash [--help] CMD...\n"
    printf "\n"
    printf "DESCRIPTION\n"
    printf "       Script used to interact with services running in lnls454-linux\n"
    printf "\n"
    printf "       --help               print this help\n"
    printf "\n"
    printf "       status               return status of services\n"
    printf "\n"
    printf "       start                start services\n"
    printf "\n"
    printf "       stop                 stop services\n"
    printf "\n"
    printf "       restart              stop services\n"
    printf "\n"
    printf "AUTHOR\n"
    printf "       FACS-LNLS.\n"
}

function run_systemctl {
  cmd=$1
  printf_blue "Runnnig systemctl $cmd for services.\n"
  printf "\n"
  for service in ${services_lnls454[@]}; do
    printf_yellow "$service...\n"
    sudo systemctl $cmd $service
    printf "\n"
  done
}

function run {
  if [ ! $# -eq 1 ]; then
    print_help
    exit
  elif [[ "$1" == "--help" ]]; then
    print_help
    exit
  fi
  host=$(hostname)
  if [[ "$host" == "lnls454-linux" ]]; then
    run_systemctl $1
  else
    get_password sirius lnls454-linux
    sshpass -p $user_passwd ssh -t sirius@lnls454-linux "sudo sirius-script-services-lnls454.bash $1"
  fi
}


run $@
