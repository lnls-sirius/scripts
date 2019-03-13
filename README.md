# General scripts for the Sirius control system

Installation

* To install all scripts just run <code>sudo make install</code> or <code>sudo make develop</code>
* To update local * <code>/etc/hosts</code> with the repo version, run <code>sudo make install-hosts</code>
* To install scripts in minion desktop for repo deployments, run <code>sudo make install-pristine</code>

IOC Scripts

* bin folder
  * <code>sirius-script-utils.bash</code>
  * <code>sirius-script-app-demag.py</code>
  * <code>sirius-script-bbb-ping.bash</code>
  * <code>sirius-script-bbb-uptime.bash</code>
  * <code>sirius-script-bbb-reboot.bash</code>
  * <code>sirius-script-repos-install-pristine.bash</code>
  * <code>sirius-script-repos-deploy.bash</code>
  * <code>sirius-script-repos-deletetags.bash</code>
  * <code>sirius-script-repos-install-update.bash</code>
  * <code>sirius-script-repos-install.bash</code>
  * <code>sirius-script-ioc-ps.bash</code>
  * <code>sirius-script-ioc-ma.bash</code>
  * <code>sirius-script-ioc-ps-ma.bash</code>
  * <code>sirius-script-csdevice-ip.py</code>

* etc folder: files to be installed in sirius desktops and in servers

* skel folder: template folder for user creation in debian/ubuntu systems.

* workstation_setup folder: scripts for system installation in prestine desktops.

* tmp folder: temporary scripts.
















  * <code>sirius-script-ioc-ma.bash</code>: init MA power supply IOCs.
    * for help, <code>sirius-script-ioc-ma.bash help</code>
