# Destination directory
DEST_DIR = /usr/local/etc

GENERALSCRIPTS = \
		bashrc-sirius \
    bashrc-sirius-bbb-facuser

SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

install: uninstall $(SCRIPTS)
	cp $(SCRIPTS) $(DEST_DIR)

install-bbb: uninstall $(SCRIPTS)
	mkdir -p $(DEST_DIR)
	cp $(SCRIPTS) $(DEST_DIR)
	ln -sf $(DEST_DIR)/bashrc-sirius-bbb-facuser /home/fac/.bashrc; chown fac.fac /home/fac/.bashrc

uninstall:
	-rm -rf $(FULLSCRIPTS)
