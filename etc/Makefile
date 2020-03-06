# Destination directory
HOSTNAME=$(shell hostname)
DEST_DIR = /usr/local/etc

GENERALSCRIPTS = \
		bashrc-sirius

SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))


install: uninstall install-ansible

install-ansible: install-hosts
	cp -f $(SCRIPTS) $(DEST_DIR)

develop:
	ln -srf $(SCRIPTS) $(DEST_DIR)

uninstall:
	rm -rf $(FULLSCRIPTS)

install-hosts:
	cp -f hosts /etc/hosts
	sed -i "s/#127.0.1.1 $(HOSTNAME)/127.0.1.1 $(HOSTNAME)/g" /etc/hosts

install-autofs:
	apt-get install autofs
	cp -f autofs-config/auto.master /etc/auto.master
	cp -f autofs-config/auto.sirius /etc/auto.sirius
	cp -f autofs-config/autofs.conf /etc/autofs.conf

	systemctl enable  autofs
	systemctl restart autofs
