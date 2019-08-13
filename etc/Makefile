# Destination directory
HOSTNAME=$(shell hostname)
DEST_DIR = /usr/local/etc

GENERALSCRIPTS = \
		bashrc-sirius \
    bashrc-sirius-bbb-facuser

SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))


install: install-hosts install-rsyncd
	cp $(SCRIPTS) $(DEST_DIR)

develop:
	ln -srf $(SCRIPTS) $(DEST_DIR)

uninstall:
	rm -rf $(FULLSCRIPTS)

install-hosts:
	cp -f hosts /etc/hosts
	sed -i "s/#127.0.1.1 $(HOSTNAME)/127.0.1.1 $(HOSTNAME)/g" /etc/hosts

install-rsyncd:
	cp rsyncd.conf /etc/rsyncd.conf

install-bbb: uninstall
	mkdir -p $(DEST_DIR)
	cp $(SCRIPTS) $(DEST_DIR)
	ln -sf $(DEST_DIR)/bashrc-sirius-bbb-facuser /home/fac/.bashrc; chown fac.fac /home/fac/.bashrc

install-autofs:
	apt-get install autofs
	cp -f autofs-config/auto.master /etc/auto.master
	cp -f autofs-config/auto.sirius /etc/auto.sirius
	cp -f autofs-config/autofs.conf /etc/autofs.conf

	systemctl enable  autofs
	systemctl restart autofs
