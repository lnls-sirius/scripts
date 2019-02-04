#!/usr/bin/env bash


ROOT_FAC=/home/fac_files
LNLS_FAC=$ROOT_FAC/lnls-fac
LNLS_SIRIUS=$ROOT_FAC/lnls-sirius

HOSTNAME=`hostname`


function check_bbb_hostname {
		if [[ $HOSTNAME != *"PSCtrl"* ]]; then
			printf "\e[1;31m'$HOSTNAME' is not a valid beaglebone name!\e[0m\n"
			exit
		fi
}


function install_fac_bashrc {
	mkdir -p $LNLS_FAC
	cd $LNLS_FAC

	# update repository and install
	if [ -d "./scripts" ]; then
		cd ./scripts && git pull
	else
		git clone https://github.com/lnls-fac/scripts
		cd ./scripts
	fi

	cd ./etc
	make install-bbb
}


function install_as_ps_ioc_systemd {
	# install systemd service files
	cd $LNLS_SIRIUS/machine-applications/systemd
	make install-services

	# allow fac user to run systemctl as root without passwords
	rm -rf /tmp/sudoers-tmp
	cat /etc/sudoers | grep -v sirius-bbb > /tmp/sudoers-tmp
	echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl start sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
	echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl stop sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
  echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl restart sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
  echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl status sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
	mv /tmp/sudoers-tmp /etc/sudoers
}


function install_machine_applications {
	# update repository and install
	cd $LNLS_SIRIUS
	if [ -d "./machine-applications" ]; then
		cd ./machine-applications && git pull
	else
		printf "\e[1;31Missing 'machine-applications' repository in default path $LNSL_SIRIUS!\e[0m\n"
		exit
	fi
	cd ./as-ps
	./setup.py install
}


check_bbb_hostname
install_fac_bashrc
install_machine_applications
install_as_ps_ioc_systemd
