# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-ioc-ps.bash \
		sirius-script-ioc-ma.bash \
		sirius-script-ioc-ps-ma.bash


SCRIPTS = $(GENERALSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

install-pristine:
		cp sirius-script-utils.bash $(DEST_DIR)/
		chmod 644 $(DEST_DIR)/sirius-script-utils.bash
		cp sirius-script-repos-install-update.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install-update.bash

install-repos-install:
		cp sirius-script-repos-install.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install.bash

install:
		cp -a sirius-script-utils.bash $(DEST_DIR)/
		cp -a sirius-script-bbb-ping.bash $(DEST_DIR)/
		cp -a sirius-script-bbb-reboot.bash $(DEST_DIR)/
		cp -a sirius-script-bbb-uptime.bash $(DEST_DIR)/
		cp -a sirius-script-repos-install.bash $(DEST_DIR)/
		cp -a sirius-script-repos-install-pristine.bash $(DEST_DIR)/
		cp -a sirius-script-repos-install-update.bash $(DEST_DIR)/
		cp -a sirius-script-repos-install.bash $(DEST_DIR)/
		cp -a sirius-script-repos-deletetags.bash $(DEST_DIR)/
		cp -a sirius-script-repos-deploy.bash $(DEST_DIR)/
		cp -a sirius-script-app-demag.bash $(DEST_DIR)/
