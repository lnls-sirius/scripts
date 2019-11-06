#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function print_help {
    printf "NAME\n"
    printf "       sirius-script-services-ioc-as-ap-sofb.bash - Interact with SOFB IOC services\n"
    printf "\n"
    printf "SINOPSIS\n"
    printf "       sirius-script-services-ioc-as-ap-sofb.bash [--help] CMD...\n"
    printf "\n"
    printf "DESCRIPTION\n"
    printf "       Script used to interact with SOFB services\n"
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
  for service in ${services_ioc_as_ap_sofb[@]}; do
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
  if [[ "$host" == "$server_services_ioc_as_ap_sofb" ]]; then
    run_systemctl $1
  else
    get_password sirius $server_services_ioc_as_ap_sofb
    sshpass -p $user_passwd ssh -t sirius@$server_services_ioc_as_ap_sofb "sudo sirius-script-services-ioc-as-ap-sofb.bash $1"
  fi
}


run $@
