install-prestine:
	$(MAKE) install-prestine -C bin/

install-repos-install:
	$(MAKE) install-repos-install -C bin/

install:
	$(MAKE) install -C etc/
	$(MAKE) install -C bin/

develop:
	$(MAKE) develop -C etc/
	$(MAKE) develop -C bin/
