#!/usr/bin/env bash

ROOT_FAC=/home/fac_files
LNLS_FAC=$ROOT_FAC/lnls-fac
LNLS_SIRIUS=$ROOT_FAC/lnls-sirius
SIRIUS_URL_CONSTS=10.128.254.203

HOSTNAME=`hostname`


function check_bbb_hostname {
		printf "\e[1;32mCheck BBB hostname...\e[0m\n"
		if [[ $HOSTNAME != *"Ctrl"* ]]; then
			printf "\e[1;31m'$HOSTNAME' is not a valid beaglebone name!\e[0m\n"
			exit
		fi
}


function install_fac_bashrc {
	printf "\e[1;32mInstall FAC bashrc...\e[0m\n"
	mkdir -p $LNLS_FAC
	sudo chown -R fac.fac $LNLS_FAC
	cd $LNLS_FAC

	# update repository and install
	if [ -d "./scripts" ]; then
		cd ./scripts && git pull
	else
		git clone https://github.com/lnls-sirius/scripts
		cd ./scripts
	fi

	cd ./etc
	make install-bbb
}


function install_as_ps_ioc_systemd {
	printf "\e[1;32mInstall AS PS IOC systemd...\e[0m\n"
	# install systemd service files
	sudo chown -R fac.fac $LNLS_SIRIUS
	cd $LNLS_SIRIUS/machine-applications && git checkout master
	cd ./as-ps/systemd && make install-services

	# allow fac user to run systemctl as root without passwords
	rm -rf /tmp/sudoers-tmp
	cat /etc/sudoers | grep -v sirius-bbb > /tmp/sudoers-tmp
	echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl start sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
	echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl stop sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
  echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl restart sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
  echo "%fac ALL=(ALL) NOPASSWD: /bin/systemctl status sirius-bbb-ioc-ps.service" >> /tmp/sudoers-tmp
	mv /tmp/sudoers-tmp /etc/sudoers
}


function install_dev_packages {
	printf "\e[1;32mInstall dev packages...\e[0m\n"
	# update repository and install
	cd $LNLS_SIRIUS
	if [ -d "./dev-packages" ]; then
		cd ./dev-packages && git checkout master && git pull
	else
		printf "\e[1;31Missing 'dev-packages' repository in default path $LNSL_SIRIUS!\e[0m\n"
		exit
	fi
	cd ./siriuspy
	./setup.py install
}


function install_machine_applications {
	printf "\e[1;32mInstall machine applications...\e[0m\n"
	# update repository and install
	cd $LNLS_SIRIUS
	if [ -d "./machine-applications" ]; then
		cd ./machine-applications && git checkout master && git pull
	else
		printf "\e[1;31Missing 'machine-applications' repository in default path $LNSL_SIRIUS!\e[0m\n"
		exit
	fi
	cd ./as-ps
	./setup.py install
}


function update_hosts {
	printf "\e[1;32mUpdate /etc/hosts...\e[0m\n"
	cat /etc/hosts | grep -v sirius-consts.lnls.br > /etc/hosts
	echo "$SIRIUS_URL_CONSTS sirius-consts.lnls.br" >> /etc/hosts
}


check_bbb_hostname
update_hosts
install_fac_bashrc
install_dev_packages
install_machine_applications
install_as_ps_ioc_systemd
