#!/usr/bin/env bash


# This script is run in remote desktops and it should clone and install all
# relevant repositories.

source ./sirius-script-bbb-utils.bash
trap _abort SIGINT;


function check_repo_install {
  repo="$1"
  tmpdir=$2
  fname="$tmpdir/log-install-$repo.stderr"
  err=$(cat $fname)
  echo $err
}

function cmd_repo_install {
  repo="$1"
  tmpdir="$2"
  cp -a $mirror_repos_path/$repo $tmpdir/
  cd $tmpdir/$repo
  if [ "$repo" == "scripts" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
    make install-hosts 1>> ../log-install-$repo.stdout 2>> ../log-install-$repo.stderr
  elif [ "$repo" == "mathphys" ]; then
    ./setup.py install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "dev-packages" ]; then
    cd ./siriuspy
    ./setup.py install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "machine-applications" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "hla" ]; then
    cd ./pyqt-apps
    make install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "bbb-daemon" ]; then
    echo "" 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  else
    echo "installation not defined for $repo !" 1> log-install-$repo.stdout 2> log-install-$repo.stderr
  fi
  var_error=$(check_repo_install $repo $tmpdir)
}


function install_all {
  tmpdir=$1
  mkdir -p $tmpdir
  for repo in ${repos[@]}; do
    printf_white "installing $repo ... "
    cmd_repo_install $repo $tmpdir
    if [[ -z "$var_error" ]]; then
      printf_green "ok\n"
    else
      printf_red "fail\n"
      exit
    fi
  done
}



function run {
  tmpdir=$(get_tmpdir repos-install)
  install_all $tmpdir
}


run $@
