#!/bin/bash

set -e
set -x

application=$1
if [ -z application ]; then
	echo 'Please select an application:'
    echo 'cs-studio'
    echo 'remmina'
	echo 'vscode'
	echo 'atom'
    exit 1
fi

if [ $application == 'cs-studio' ]; then
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
elif [ $application == 'remmina' ]; then
	if [ $(lsb_release -is) = 'Debian' ]; then
		echo 'deb http://ftp.debian.org/debian stretch-backports main' | sudo tee --append /etc/apt/sources.list.d/stretch-backports.list >> /dev/null
		sudo apt update
		sudo apt install -y -t stretch-backports remmina remmina-plugin-rdp remmina-plugin-secret
	else
		echo "No instruction for $(lsb_release -is)"
	fi
elif  [ $application == 'vscode' ]; then
    sudo apt-get install -y apt-transport-https
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.gpg
    sudo install -o root -g root -m 644 microsoft.gpg /etc/apt/trusted.gpg.d/
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/vscode stable main" > /etc/apt/sources.list.d/vscode.list'
    sudo apt-get update
    sudo apt-get install -y code
    sudo rm microsoft.gpg
elif  [ $application == 'atom' ]; then
    sudo apt-get install -y apt-transport-https
    wget -qO - https://packagecloud.io/AtomEditor/atom/gpgkey | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] https://packagecloud.io/AtomEditor/atom/any/ any main" > /etc/apt/sources.list.d/atom.list'
    sudo apt-get update
    sudo apt-get -y install atom
elif  [ $application == 'rdesktop' ]; then
		# needed to access one type of oscilloscope
		sudo apt-get update
		sudo apt-get -y install rdesktop
else
	echo "No instructions found for $application"
fi

exit 0
