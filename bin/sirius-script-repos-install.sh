#!/usr/bin/env bash

repo_path=/home/sirius/repos

hostname=`hostname`

repos=("mathphys"
       "dev-packages"
       "machine-applications")


function get_tmpdir {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo "/tmp/deploy-"$timestamp
}

function run_install {
    repo=$1
    if [ "$repo" == "dev-packages" ]; then
        cd ./siriuspy
        ./setup.py install
    elif [ "$repo" == "machine-applications" ]; then
        make install
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
