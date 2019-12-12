#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function create_tagged_repos {
  printf_green "Create tagged local repos\n"
  printf "\n"
  tmpdir=$(get_tmpdir repos-deploy)
  mkdir -p $tmpdir
  for repo in ${repos[@]}; do
    printf_yellow "[$repo]\n"
    cmd_repo_clone_master $repo $tmpdir
    git tag $deploy_tag
    git push --tags
    printf "\n"
  done
}

function print_header_and_inputs {
  mode=$1
  printf_blue "Deploy Sirius Repositories ("$mode")\n"
  printf "\n"
  get_password sirius desktops
  deploy_tag=$(create_deploy_tag)
  read -e -p "Enter deploy tag    : " -i "$deploy_tag" deploy_tag
  read -r -p "Enter deploy comment: " comment; echo ""
  read -r -p "Really deploy ? [yes|no]: " answer; echo ""
  if [ ! "$answer" == 'yes' ]; then
    printf_red "bailing out...\n"
    exit
  fi
  printf "\n"
}

function clone_ansible {
  printf_green "Clonning Ansible\n"
  ansible_folder=$(mktemp -d --suffix=-lnls-ansible)
  git clone https://github.com/lnls-sirius/lnls-ansible $ansible_folder
  printf "\n"
}

function run_ansible {
  mode=$1
  printf_green "Running Ansible (cloned master)\n"
  cd $ansible_folder
  if [ ! "$mode" == 'fast' ]; then
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_deploy_tag=$deploy_tag global_import_nvidia_driver_role=false\"" deploy-control-room-desktops-sirius
  else
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_deploy_tag=$deploy_tag global_import_nvidia_driver_role=false\"" deploy-control-room-desktops
  fi
}

function run {
  print_header_and_inputs $1
  #create_tagged_repos
  #update_servweb
  #checkout_tagged_repos_nfs_server
  #clone_ansible
  #run_ansible $1
  #update_deploy_file
}

run $1
