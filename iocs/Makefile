# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-ioc-ps.bash


SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

uninstall:
	rm -rf $(FULLSCRIPTS)

install: uninstall $(SCRIPTS)
	cp $(SCRIPTS) $(DEST_DIR); cd $(DEST_DIR); chmod a+x $(SCRIPTS)

develop: uninstall $(SCRIPTS)
	ln -srf $(SCRIPTS) $(DEST_DIR)
