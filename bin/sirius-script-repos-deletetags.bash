#!/usr/bin/env bash

source /usr/local/bin/sirius-script-utils.bash


function get_tag {
  read -r -p "please enter deploy tag name to be deleted: " deploytag;
  echo $deploytag
}

function run {
  printf_green "Delete deploy tag\n"
  deploy_tag=`get_tag`
  printf_yellow "Deleting tag '$deploy_tag'...\n"
  read -r -p "Are you sure ? [yes|no]: " answer;
  if [ ! "$answer" == "yes" ]; then
    printf_red "bailing out...\n"
    exit
  fi
  printf "\n"

  tmpdir=$(get_tmpdir deletetags)
  mkdir -p $tmpdir
  cd $tmpdir
  for repo in "${repos[@]}"; do
    printf_yellow "[$repo]\n"
    cmd_repo_clone_master $repo $tmpdir
    git tag -d $deploy_tag
    git push --delete origin $deploy_tag
    printf "\n"
  done
}


run
