#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function print_header_and_inputs {
  mode=$1
  printf_blue "Deploy Sirius Repositories ("$mode")\n"
  printf "\n"
  # get_password sirius desktops
  deploy_tag=$(create_deploy_tag)
  read -e -p "Enter deploy tag    : " -i "$deploy_tag" deploy_tag
  # read -r -p "Enter deploy comment: " comment; echo ""
  read -r -p "Really deploy ? [yes|no]: " answer; echo ""
  if [ ! "$answer" == 'yes' ]; then
    printf_red "bailing out...\n"
    exit
  fi
  printf "\n"
}

function tag_ansible {
  printf_green "Clonning Ansible\n"
  cd /home/sirius/repos/lnls-ansible
  git stash
  git fetch -p --all
  git checkout master
  git pull
  git tag $deploy_tag
  git push --tags
  printf "\n"
}

function run_ansible {
  mode=$1
  printf_green "Running Ansible\n"
  cd /home/sirius/repos/lnls-ansible
  git checkout $deploy_tag
  if [ "$mode" == 'fast' ]; then
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_import_nvidia_driver_role=false\"" deploy-control-room-desktops-sirius-nfs
  else
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_import_nvidia_driver_role=false\"" deploy-control-room-desktops-nfs
  fi
}

function run {
  print_header_and_inputs $1
  tag_ansible
  run_ansible $1
}

run $1
