#!/usr/bin/env bash


# This script is run in remote desktops and it clones and installs all
# relevant repositories.

source sirius-script-bbb-utils.bash
trap _abort SIGINT;


function install_repos {
  tmpdir=$1
  lrepos=${@:2}
  mkdir -p $tmpdir
  for repo in ${lrepos[@]}; do
    printf_yellow "[$repo] ... "
    cmd_repo_install $repo $tmpdir
    if [[ -z "$var_error" ]]; then
      printf_green "ok\n"
    else
      printf_red "fail\n"
      printf_white_bold "Check local log file '$tmpdir/log-install-$repo.stderr'!\n"
      exit
    fi
  done
}

function run {
  printf_white "Installing repositories...\n"
  if [ $# -eq 0 ]; then
    lrepos=${repos[@]}
  else
    lrepos=$@
  fi
  tmpdir=$(get_tmpdir repos-install)
  install_repos $tmpdir $lrepos
}


run $@
