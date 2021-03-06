#!/bin/bash

# Install selected repository

# --- Run with sudo -HE ---
set -e
set -x

function change_directory {
	if [ -d $1 ]; then
		cd $1
	else
		echo "$1 not found. Aborting"
		exit 1
	fi
}

function clone_repo {
	command -v git >/dev/null 2>&1 || { echo >&2 "Git not found. Aborting."; exit 1; }
	if [ $protocol == 'http' ]; then
		git clone "https://github.com/$1"
	elif [ $protocol == 'ssh' ]; then
		git clone "ssh://git@github.com/$1"
	fi
}

function clone_and_develop {
	dir="$1/$2"
	if [ ! -d $dir ]; then
		change_directory $1
		clone_repo $3
	fi
	change_directory $dir
	python-sirius setup.py build
	sudo python-sirius setup.py $action
}

if [ -z $1 ]; then
	echo 'Please select a repository:'
	echo '## FAC ##'
	echo 'MML'
	echo 'apsuite'
	echo 'lnls'
	echo 'mathphys'
	echo 'trackcpp'
	echo 'fieldmaptrack'
	echo 'pyjob'
	echo 'pyaccel'
	echo 'pymodels'
	echo 'va'
	echo '## SIRIUS ##'
	echo 'control-system-constants'
	echo 'dev-packages'
	echo 'pydm'
	echo 'hla'
	echo 'pruserial485'
	echo 'machine-applications'
	echo 'sirius-scripts'
	echo '## MISC ##'
	echo 'pyjob'
	exit 1
fi

repo=$1
action=$2  # install or develop
if [ -z $action ]; then
	action=develop
fi
protocol=$3  # http or ssh
if [ -z $protocol ]; then
	protocol='http'
fi

fac_repos='/home/facs/repos'
sirius_repos='/home/sirius/repos'


#if [ ! -f $HOME/.ssh/id_rsa.pub ]; then
#	echo 'No ssh key found. Please create one using ssh-keygen and add it to your github account.'
#	exit 1
#fi

# FAC
if [ $repo == 'MML' ]; then
	if [ ! -d "$fac_repos/trackcpp/MatlabMiddleLayer" ]; then
		change_directory "$fac_repos"
		clone_repo lnls-fac/MatlabMiddleLayer.git
	fi
	echo 'Repo clone. Please follow instructions:'
	echo '1 - open matlab as root: sudo matlab'
	echo '2 - Edit the path to include the folder: /home/fac_files/lnls-fac/MatlabMiddleLayer/Release/lnls/startup_scripts'
	echo '3 - Close matlab and open matlab in user mode: matlab'
	echo '4 - Compile the .mex files in matlab: '
	echo '	>> sirius;
		>> atmexall;
		>> naff_cc;'
elif [ $repo == 'apsuite' ]; then
	repo='apsuite'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'lnls' ]; then
	repo='lnls'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'mathphys' ]; then
	repo='mathphys'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'fieldmaptrack' ]; then
	repo='fieldmaptrack'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'trackcpp' ]; then
	sudo apt-get install -y g++ libgsl0-dev swig liblapack-dev
	if [ ! -d "$fac_repos/trackcpp" ]; then
		change_directory $fac_repos
		clone_repo lnls-fac/trackcpp.git
	fi
	change_directory "$fac_repos/trackcpp"
	sudo make clean
	sudo make -j8 PYTHON=python-sirius PYTHON_VERSION=python3.6
	sudo make install PYTHON=python-sirius PYTHON_VERSION=python3.6
elif [ $repo == 'pyaccel' ]; then
	repo='pyaccel'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'pymodels' ]; then
	repo='pymodels'
	link="lnls-fac/$repo.git"
	clone_and_develop $fac_repos $repo $link
elif [ $repo == 'va' ]; then
	repo='va'
	link="lnls-fac/va.git"
	clone_and_develop $fac_repos $repo $link

# SIRIUS
elif [ $repo == 'control-system-constants' ]; then
	if [ ! -d "$sirius_repos/control-system-constants" ]; then
		change_directory $sirius_repos
		clone_repo lnls-sirius/control-system-constants.git
	fi
elif [ $repo == 'dev-packages' ]; then
	repo='dev-packages/siriuspy/'
	link="lnls-sirius/dev-packages.git"
	clone_and_develop $sirius_repos $repo $link
elif [ $repo == 'pydm' ]; then
	repo='pydm'
	link="lnls-sirius/pydm.git"
	clone_and_develop $sirius_repos $repo $link
elif [ $repo == 'hla' ]; then
	if [ ! -d "$sirius_repos/hla" ]; then
		change_directory $sirius_repos
		clone_repo lnls-sirius/hla.git
	fi
	change_directory "$sirius_repos/hla/pyqt-apps"
	make install-resources
	sudo make $action
elif [ $repo == 'pruserial485' ]; then
	if [ ! -d "$sirius_repos/pru-serial485" ]; then
		change_directory $sirius_repos
		clone_repo lnls-sirius/pru-serial485.git
	fi
	change_directory "$sirius_repos/pru-serial485/src"
	sudo ./library_build.sh
	sudo ./overlay.sh
elif [ $repo == 'machine-applications' ]; then
	if [ ! -d "$sirius_repos/machine-applications" ]; then
		change_directory $sirius_repos
		clone_repo lnls-sirius/machine-applications.git
	fi
	change_directory $sirius_repos/machine-applications
	sudo make $action
elif [ $repo == 'linac-opi' ]; then
	if [ ! -d "$sirius_repos/linac-opi" ]; then
		change_directory $sirius_repos
		git clone "fac@lnls350-linux:/home/fac_files/repo/sirius/linac-opi.git"
	fi
	change_directory $sirius_repos/linac-opi
	sudo make $action
elif [ $repo == 'sirius-scripts' ]; then
	if [ ! -d $sirius_repos/scripts ]; then
		change_directory $sirius_repos
		clone_repo "lnls-sirius/scripts.git"
	fi
	change_directory $sirius_repos/scripts
	sudo make $action

	users=(fernando ximenes liulin ana alexandre murilo sirius facs)
	for user in ${users[@]}; do
		if [ -d "/home/$user" ]; then
			bash_path="/home/$user/.bashrc"
			sudo cp -a /etc/skel/.bashrc $bash_path
			sudo sed -i -e '5i # --- Sirius bashrc ---' $bash_path
			sudo sed -i -e '6i SIRIUSBASHRC=/usr/local/etc/bashrc-sirius' $bash_path
			sudo sed -i -e '7i if [ -f "$SIRIUSBASHRC" ] ; then' $bash_path
			sudo sed -i -e '8i \ \ \ \ source "$SIRIUSBASHRC"' $bash_path
			sudo sed -i -e '9i fi\n' $bash_path
			sudo sed -i -e "10i bind '\"\\\e[A\": history-search-backward'" $bash_path
			sudo sed -i -e "11i bind '\"\\\e[B\": history-search-forward'" $bash_path
			if [ "$user" != "sirius" ]; then
				sudo sed -i -e '12i export VACA_PREFIX=$(whoami)-$(hostname)- # This line should be commented when in sirius computers' $bash_path
			fi
		fi
	done

# MISC
elif [ $repo == 'cs-studio' ]; then
	sudo apt-get install -y openjfx
	version='4.6.1.12'
	file="cs-studio-ess-$version-linux.gtk.x86_64.tar.gz"
	if [ -d '/opt/cs-studio' ]; then
		echo 'CS Studio installed. Passing.'
		exit 0
	fi
	if [ ! -f ./$file ]; then
		wget "https://artifactory.esss.lu.se/artifactory/CS-Studio/production/$version/$file"
	fi
	sudo tar xzvf $file
	sudo mv ./cs-studio /opt/cs-studio
	sudo ln -sf /opt/cs-studio/ESS\ CS-Studio /usr/local/bin/cs-studio
	sudo rm -rf $file
elif [ $repo == 'pyjob' ]; then
	if [ ! -d "$fac_repos/job_manager" ]; then
		change_directory $fac_repos
		clone_repo lnls-fac/job_manager.git
	fi
	change_directory "$fac_repos/job_manager/apps"
	sudo make install
	cd ..
	sudo ./install_services.py
	sudo systemctl start pyjob_run.service
elif [ $repo == 'remmina' ]; then
	if [ $(lsb_release -is) = 'Debian' ]; then
		echo 'deb http://ftp.debian.org/debian stretch-backports main' | sudo tee --append /etc/apt/sources.list.d/stretch-backports.list >> /dev/null
		sudo apt update
		sudo apt install -y -t stretch-backports remmina remmina-plugin-rdp remmina-plugin-secret
	else
		echo "No instruction for $(lsb_release -is)"
	fi
else
	echo "Repository $repo not found"
fi

exit 0
