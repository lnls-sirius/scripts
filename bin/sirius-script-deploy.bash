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
  printf_blue "Deploy Sirius Repositories\n"
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

function run_ansible {
  printf_green "Running Ansible\n"
  cd $ansible_folder
  make deploy-control-room-desktops
}

function run {
  print_header_and_inputs
  create_tagged_repos
  run_ansible
  update_deploy_file
}

run
