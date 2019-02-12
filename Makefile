install:
	$(MAKE) install -C iocs/
	$(MAKE) install -C etc/
	$(MAKE) install -C bin/

develop:
	$(MAKE) develop -C iocs/
	$(MAKE) develop -C etc/
	$(MAKE) develop -C bin/
