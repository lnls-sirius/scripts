# Destination directory
HOSTNAME=$(shell hostname)
DEST_DIR = /usr/local/etc

GENERALSCRIPTS = \
		bashrc-sirius \
    bashrc-sirius-bbb-facuser

SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))


install: uninstall $(SCRIPTS) install-bashrc install-rsyncd
	cp $(SCRIPTS) $(DEST_DIR)

install-hosts:
	rm /etc/hosts
	cp hosts /etc/hosts
	sed -i "s/#127.0.1.1 $(HOSTNAME)/127.0.1.1 $(HOSTNAME)/g" /etc/hosts

install-rsyncd:
	cp rsyncd.conf /etc/rsyncd.conf

develop: uninstall $(SCRIPTS)
	ln -srf $(SCRIPTS) $(DEST_DIR)

install-bbb: uninstall $(SCRIPTS)
	mkdir -p $(DEST_DIR)
	cp $(SCRIPTS) $(DEST_DIR)
	ln -sf $(DEST_DIR)/bashrc-sirius-bbb-facuser /home/fac/.bashrc; chown fac.fac /home/fac/.bashrc

uninstall:
	rm -rf $(FULLSCRIPTS)
