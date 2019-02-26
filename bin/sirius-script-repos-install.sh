#!/usr/bin/env bash

repo_path=/home/sirius/repos

hostname=`hostname`

repos=("scripts"
       "mathphys"
       "dev-packages"
       "machine-applications"
       "hla"
       "bbb-daemon")


function get_tmpdir {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo "/tmp/deploy-"$timestamp
}

function run_install {
    repo=$1
    if [ "$repo" == "scripts" ]; then
      pushd ./etc > /dev/null
        make install
        make install-hosts
      popd > /dev/null
    elif [ "$repo" == "mathphys" ]; then
      ./setup.py install
    elif [ "$repo" == "dev-packages" ]; then
      cd ./siriuspy
      ./setup.py install
    elif [ "$repo" == "machine-applications" ]; then
      make install
    elif [ "$repo" == "hla" ]; then
      cd ./pyqt-apps
      make install
    elif [ "$repo" == "bbb-daemon" ]; then
      :
    else
      echo "installation not defined for $repo !"
    fi
}

function install_repos {
  mkdir -p $tmpdir
  for repo in "${repos[@]}"; do
    echo "installing $repo"
    cp -ra $repo_path/$repo $tmpdir/
    pushd $tmpdir/$repo > /dev/null
      run_install $repo
    popd > /dev/null
  done
}


tmpdir=`get_tmpdir`
install_repos
