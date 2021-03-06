#!/bin/bash

set -e
set -x

# Install Epics base

# Check if git is installed
command -v git >/dev/null 2>&1 || { echo >&2 "Git not found. Aborting."; exit 1; }
# Check ssh key
#if [ ! -f $HOME/.ssh/id_rsa.pub ]; then
#	echo 'No ssh key found. Please create one using ssh-keygen and add it to your github account.'
#	exit 1
#fi
# Check epics already installed
if [ -d '/opt/epics/base-3.15.5' ]; then
	echo 'Epics base folder found. Passing.'
	exit 0
fi
# Instal epics base, TODO: check if already installed
dir=/home/sirius
if [ -d $dir ]; then
	cd $dir
	if [ ! -d $dir/epics-dev ]; then
		git clone https://github.com/lnls-sirius/epics-dev.git
	fi
	cd epics-dev/
	git checkout base-3.15
	sudo ./run-all.sh -a no -e yes -x no -s yes -r yes -i -o -c
	cd ..
	sudo rm -rf $dir/epics-dev
	exit 0
else
	echo "$dir not found. Aborting."
	exit 1
fi
