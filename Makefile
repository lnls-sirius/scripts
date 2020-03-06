install-pristine:
	$(MAKE) install-pristine -C bin/

install-repos-install:
	$(MAKE) install-repos-install -C bin/

install:
	$(MAKE) install -C etc/
	$(MAKE) install -C bin/

install-ansible:
	# $(MAKE) install-ansible -C etc/
	$(MAKE) install-ansible -C bin/

develop:
	$(MAKE) develop -C etc/
	$(MAKE) develop -C bin/

install-hosts:
	$(MAKE) install-hosts -C etc/
