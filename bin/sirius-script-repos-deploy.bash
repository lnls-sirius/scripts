#!/usr/bin/env bash

source ./sirius-script-bbb-utils.bash
trap _abort SIGINT;


function cmd_repo_clone_master_create_deploy_tag {
  repo=$1
  tag=$2
  tmpdir=$3
  cd $tmpdir
  if [ "$repo" == "mathphys" ]; then
      git clone ssh://git@github.com/lnls-fac/$repo
  else
    git clone ssh://git@github.com/lnls-sirius/$repo
  fi
  cd $repo
  if [ "$repo" == "control-system-constants" ]; then
    git checkout PR-update-makefile
  fi
  git tag $tag
  git push --tags
}

function create_tagged_repos {
  tmpdir=$(get_tmpdir repos-deploy)
  mkdir -p $tmpdir
  for repo in ${repos[@]}; do
    printf_white_bold "[$repo]\n"
    cmd_repo_clone_master_create_deploy_tag $repo $deploy_tag $tmpdir
    printf "\n"
  done
}

function print_header_and_inputs {
  printf_blue "Deploying Sirius Repositories\n"
  printf "\n"
  deploy_tag=$(create_deploy_tag)
  read -e -p "Enter deploy tag    : " -i "$deploy_tag" deploy_tag
  read -r -p "Enter deploy comment: " comment; echo ""
  get_password sirius destops
  read -r -p "Really deploy ? [yes|no]: " answer; echo ""
  if [ ! "$answer" == 'yes' ]; then
    printf_red "bailing out...\n"
    exit
  fi
  printf "\n"
}

function checkout_tagged_repos_nfs_server {
  printf_yellow "Checkout tagged repos in nfs server ($servnfs_hostname)\n"
  printf "\n"
  sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/; echo "$deploy_tag:  $comment" >> deploy.log"
  for repo in "${repos[@]}"; do
    printf_green ". repo $repo\n"
    sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/$repo; git fetch -p --tags; git checkout master; git pull; git checkout $deploy_tag"
    printf "\n"
  done
}


function deploy_desktops {
  printf_yellow "... deploying in desktops ..."
  printf "\n"
  for desktop in "${desktops[@]}"; do
    printf_green "installing repos in $desktop..."
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install-update.sh"
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install.sh"
  done
  printf "\n"
}


function run {
  print_header_and_inputs
  create_tagged_repos
  checkout_tagged_repos_nfs_server
}

run
