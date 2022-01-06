#!/usr/bin/env bash

timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
cd /home/sirius/shared && tar zcfv - screens-iocs | ssh sirius@10.128.255.3 "cat > /storage/services/AutoBackup/FAC/screens-iocs_$timestamp.tgz"
