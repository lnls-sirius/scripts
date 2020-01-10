#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash
trap _abort SIGINT;


function create_tagged_repos {
  printf_green "Create tagged local repos\n"
  printf "\n"
  tmpdir=$(get_tmpdir repos-deploy)
  mkdir -p $tmpdir
  repos=(
    "lnls-ansible:master"
  )
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
  git tag $deploy_tag
  git push --tags
  printf "\n"
}

function run_ansible {
  mode=$1
  printf_green "Running Ansible\n"
  cd /home/sirius/repos/lnls-ansible
  checkout $deploy_tag
  if [ ! "$mode" == 'fast' ]; then
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_deploy_tag=$deploy_tag global_import_nvidia_driver_role=false\"" deploy-control-room-desktops-sirius
  else
    make ANSIBLE_EXTRA_VARS="--extra-vars \"global_deploy_tag=$deploy_tag global_import_nvidia_driver_role=false\"" deploy-control-room-desktops
  fi
}

function run {
  print_header_and_inputs $1

  # move these tasks to ansible!
  update_servweb
  #checkout_tagged_repos_nfs_server

  tag_ansible
  run_ansible $1
}

run $1
