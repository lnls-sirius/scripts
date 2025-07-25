#!/bin/sh

# This should be run as root

set -e

cd /root
rm -rf /root/openocd
git clone --branch xvc-tcp-support --single-branch https://github.com/lnls-dig/openocd
cd openocd
./bootstrap
./configure --enable-xvc --prefix=/usr/local
make -j $(nproc)
make install
rm -rf /root/openocd
