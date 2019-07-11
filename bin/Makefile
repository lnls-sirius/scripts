# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-utils.bash \
		sirius-script-app-demag.py \
		sirius-script-services-fac.bash \
		sirius-script-ps-firmware-version.py \
		sirius-script-li-egun-ramp.py

REPOSSCRIPTS = \
		sirius-script-repos-install-pristine.bash \
		sirius-script-repos-install-update.bash \
		sirius-script-repos-install.bash \
		sirius-script-repos-deletetags.bash \
		sirius-script-repos-deploy.bash

BBBSCRIPTS = \
		sirius-script-bbb-ping.bash \
		sirius-script-bbb-reboot.bash \
		sirius-script-bbb-uptime.bash

SCRIPTS = $(GENERALSCRIPTS) $(REPOSSCRIPTS) $(BBBSCRIPTS)

FULLSCRIPTS = $(addprefix $(DEST_DIR)/, $(SCRIPTS))

install-pristine:
		cp sirius-script-utils.bash $(DEST_DIR)/
		chmod 644 $(DEST_DIR)/sirius-script-utils.bash
		cp sirius-script-repos-install-update.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install-update.bash

install-repos-install:
		cp sirius-script-repos-install.bash $(DEST_DIR)/
		chmod 755 $(DEST_DIR)/sirius-script-repos-install.bash

install: uninstall
		cp -a $(SCRIPTS) $(DEST_DIR)

develop: uninstall
		ln -srf $(SCRIPTS) $(DEST_DIR)

uninstall:
	rm -rf $(FULLSCRIPTS)
