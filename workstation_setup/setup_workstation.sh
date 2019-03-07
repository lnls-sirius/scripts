#!/bin/bash

set -e
set -x

function execute {
    echo "Executing $1"
    if "./$1" $2 $3; then
        echo "Finished $1 with sucess."
    else
        echo "$1 failed. Aborting."
        exit 1
    fi
}

function set_nfs {
    sudo apt-get install nfs-common

    mkdir -p /home/sirius/Desktop/lost-and-found
    mkdir -p /home/sirius/Desktop/screens-iocs
    chown -R sirius:sirius /home/sirius/Desktop/lost-and-found
    chown -R sirius:sirius /home/sirius/Desktop/screens-iocs

    rules=(
        '10.128.254.203:/home/nfs-shared/repos-lnls-sirius   /home/sirius/repos nfs ro 0 0'
        '10.128.254.203:/home/nfs-shared/lost-and-found   /home/sirius/Desktop/lost-and-found nfs rw'
        '10.128.254.203:/home/nfs-shared/screens-iocs   /home/sirius/Desktop/screens-iocs nfs rw')
    for rule in ${rules[@]}; do
        if ! grep -Fxq $rule /etc/fstab; then
            echo $rule | sudo tee -a /etc/fstab
        fi
    done

    sudo mount -a
}

# Check write permission
if [ ! -w ./ ]; then
	echo 'You do not have write permission for the current directory. Aborting.'
	exit 1
fi

execute set_vlans.sh
execute debian_mirrors.sh

# Copy skel
if [ -d ../skel ]; then
    sudo cp -r ../skel/. /etc/skel
else
    echo 'Could not find ../skel directory. Aborting.'
    exit 1
fi

execute create_groups.sh
# execute create_users.sh
execute directories_permissions.sh

# execute install_git.sh
sudo apt-get install -y git

execute create_bbb_repositories.sh

execute install_python.sh
execute install_epics.sh
execute install_pyepics.sh
execute install_qt.sh
execute install_sip.sh
execute install_pyqt.sh

execute install_fac_deps.sh

set_nfs

execute install_misc.sh cs-studio
execute install_misc.sh remmina
execute install_misc.sh rdesktop

execute install_css_opi.sh pulsed

sudo apt-get install -y htop vim
