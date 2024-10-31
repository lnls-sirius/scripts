# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-utils.bash \
		sirius-script-app-demag.py \
		sirius-script-app-ps-pvsprint.py \
		sirius-script-clientarch-resumepvs.py \
		sirius-script-clientarch-renamepvs.py \
		sirius-script-deploy.bash \
		sirius-script-ps-firmware-version.py \
		sirius-script-ps-devices.py \
		sirius-script-li-egun-ramp.py \
		sirius-script-ps-wfmupdateauto-off.py \
		sirius-script-clientarch-checkpv.py \
		sirius-script-si-acquire-bpm-triggered-data.py \
		sirius-script-clientconfigdb-compare-configs.py \
		sirius-script-install-openocd.sh \
		sirius-script-rabpm-mngr.py

REPOSSCRIPTS = \
		sirius-script-repos-install-pristine.bash \
		sirius-script-repos-install-update.bash \
		sirius-script-repos-install.bash \
		sirius-script-repos-deletetags.bash \
		sirius-script-repos-deploytag.bash
		# sirius-script-deploy-tag.bash

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

install: uninstall install-ansible

install-ansible:
		cp -a $(SCRIPTS) $(DEST_DIR)

develop: uninstall
		ln -srf $(SCRIPTS) $(DEST_DIR)

uninstall:
	rm -rf $(FULLSCRIPTS)
