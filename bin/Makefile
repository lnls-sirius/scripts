# Destination directory
DEST_DIR = /usr/local/bin

GENERALSCRIPTS = \
		sirius-script-utils.bash \
		sirius-script-app-demag.py \
		sirius-script-app-ps-pvsprint.py \
		sirius-script-services-ioc-bo-ma.bash \
		sirius-script-services-ioc-bo-ps-fam.bash \
		sirius-script-services-ioc-bo-ps-corr.bash \
		sirius-script-services-ioc-dclinks-ps.bash \
		sirius-script-services-ioc-fac.bash \
		sirius-script-services-ioc-li-ps.bash \
		sirius-script-services-ioc-si-ma-corr.bash \
		sirius-script-services-ioc-si-ma-fam.bash \
		sirius-script-services-ioc-si-ps-corr.bash \
		sirius-script-services-ioc-si-ps-fam.bash \
		sirius-script-services-ioc-tb-ma.bash \
		sirius-script-services-ioc-tb-ps.bash \
		sirius-script-services-ioc-ts-ma.bash \
		sirius-script-services-ioc-ts-ps.bash \
		sirius-script-clientarch-resumepvs.py \
		sirius-script-clientarch-renamepvs.py \
		sirius-script-deploy.bash \
		sirius-script-ps-firmware-version.py \
		sirius-script-ps-devices.py \
		sirius-script-li-egun-ramp.py

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
