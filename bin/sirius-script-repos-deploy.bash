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

function update_servweb {
  printf_green "Update servweb ($servweb_hostname)\n"
  printf "\n"
  sshpass -p $user_passwd ssh sirius@$servweb_hostname "git -C /storage/misc/repository/control-system-constants pull"
}

function checkout_tagged_repos_nfs_server {
  printf_green "Checkout tagged repos in nfs server ($servnfs_hostname)\n"
  printf "\n"
  sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/; echo '$deploy_tag:  $comment' >> deploy.log"
  for repo in "${repos[@]}"; do
    reponame=$(echo $repo | cut -d":" -f1)
    branch=$(echo $repo | cut -d":" -f2)
    printf_yellow "[$repo]\n"
    sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/$reponame; rm -rf dist build */*.egg-info *.egg-info"
    sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/$reponame; git stash; git fetch --prune origin '+refs/tags/*:refs/tags/*'; git checkout $branch; git pull; git checkout $deploy_tag"
    printf "\n"
  done
}

function deploy_desktops {
  printf_green "Deploying in desktops\n"
  printf "\n"
  for desktop in "${desktops[@]}"; do
    printf_blue "[$desktop]\n"
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install-update.bash"
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install.bash"
    printf "\n"
  done
}

function run {
  print_header_and_inputs
  create_tagged_repos
  # update_servweb
  checkout_tagged_repos_nfs_server
  deploy_desktops
}

run
