#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function print_header_and_inputs {
  deploy_tag=$1
  printf_blue "Deploying Sirius Repositories (existing tag)\n"
  printf "\n"
  get_password sirius desktops
  if [ -z "$deploy_tag" ]; then
    read -e -p "Enter deploy tag    : " -i "$deploy_tag" deploy_tag
  else
    printf "Deploying tag '$deploy_tag'\n"
  fi
  read -r -p "Really deploy ? [yes|no]: " answer; echo ""
  if [ ! "$answer" == 'yes' ]; then
    printf_red "bailing out...\n"
    exit
  fi
  printf "\n"
}

function run {
  print_header_and_inputs $1
  update_servweb
  checkout_tagged_repos_nfs_server
  deploy_desktops
}

run $1
