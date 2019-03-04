# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-ioc-ps.bash \
		sirius-script-ioc-ma.bash \
		sirius-script-ioc-ps-ma.bash


SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

install-update-install:
		cp sirius-script-repos-install.sh $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install.sh
