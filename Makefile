install-update-install:
	$(MAKE) install-update-install -C bin/

install:
	$(MAKE) install -C etc/
	$(MAKE) install -C bin/

develop:
	$(MAKE) develop -C etc/
	$(MAKE) develop -C bin/
