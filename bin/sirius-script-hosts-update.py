#!/usr/bin/env python-sirius

import subprocess
import os
import getpass
import sys
import socket


fac_server_ip = '10.128.254.203'
fac_server_name = 'lnls452-linux'


def get_ip_address():
	output = subprocess.check_output(['ifconfig'])
	text   = output.decode('utf-8')
	lines  = text.split('\n')
	for line in lines:
		line = line.strip()
		if ('inet addr' in line) and ('127.0.0' not in line):
			words = line.split(' ')
			ip_address = words[1].replace('addr:','')
	return ip_address


def get_hostname():
	output = subprocess.check_output(['cat', '/etc/hostname'])
	text   = output.decode('utf-8')
	lines  = text.split('\n')
	return lines[0].strip()


def import_hosts():

	login = os.getlogin()
	hostname   = get_hostname()
	userserver = login + '@' + fac_server_ip
	args = ['ssh', '-X', userserver, 'cat /etc/hosts']
	print('Running: "{}"'.format(' '.join(args)))
	output = subprocess.check_output(args)
	text  = output.decode('utf-8')
	lines = text.split('\n')
	new_text = []
	for line in lines:
		line = line.strip()
		if (fac_server_name in line) and ('127.0.1.1' in line):
			line = '#' + line
		if (hostname in line) and ('127.0.1.1' in line):
			line = line[1:]
		new_text.append(line)

	return new_text


def save_hosts(text):

	fp = open('/etc/hosts','w')
	for line in text:
		fp.write(line + '\n')


def check_root():

	user = getpass.getuser()
	if user != 'root':
		print('This script needs to be run as root!')
		sys.exit(-1)


def check_hostname():
	"""."""
	if get_hostname() == fac_server_name:
		print('Cannot update hosts in server!')
		sys.exit(-1)

check_root()
check_hostname()
hosts = import_hosts()
save_hosts(hosts)