# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-ioc-ps.bash \
		sirius-script-ioc-ma.bash \
		sirius-script-ioc-ps-ma.bash


SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

install-pristine:
		cp sirius-script-bbb-utils.bash $(DEST_DIR)/
		chmod 644 $(DEST_DIR)/sirius-script-bbb-utils.bash
		cp sirius-script-repos-install-update.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install-update.bash

install-repos-install:
		cp sirius-script-repos-install.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install.bash

install:
		cp sirius-script-bbb-ping.bash $(DEST_DIR)/
