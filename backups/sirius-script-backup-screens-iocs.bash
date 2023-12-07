#!/usr/bin/env bash

timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
#cd /home/sirius/shared && tar cfv - screens-iocs | ssh sirius@10.128.255.3 "cat > /storage/services/AutoBackup/FAC/screens-iocs_$timestamp.tar"
#cd /home/sirius/shared && tar cfv - screens-iocs | ssh sirius@10.0.38.42 "cat > /storage/services/AutoBackup/FAC/screens-iocs_$timestamp.tar"
cd /home/sirius/shared && tar cfv - screens-iocs | ssh ximenes.resende@swc-server-ibm1 "cat > /mnt/nfs/ibira/lnls/labs/fac/data_by_day/screens-iocs_$timestamp.tar"
