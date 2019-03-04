#!/usr/bin/env bash


# This script is run in remote desktops and it should clone and install all
# relevant repositories.

source ./sirius-script-bbb-utils.bash
trap _abort SIGINT;


function cmd_repo_install {
  repo=$1
  tmpdir=$2
  cp -ra $mirror_repos_path/$repo $tmpdir/
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
}


function run {
  tmpdir=$(get_tmpdir repos-install)
  echo $tmpdir
  for repo in ${repos[@]}; do
    cmd_repo_install $repo $tmpdir
    echo $repo
  done
}


run $@
