#!/usr/bin/env bash

timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
# cd /home/sirius/shared && tar zcfv - screens-iocs | ssh sirius@10.128.255.3 "cat > /storage/services/AutoBackup/FAC/screens-iocs_$timestamp.tgz"
# cd /home/sirius/shared && tar cfv - screens-iocs | ssh sirius@10.128.255.3 "cat > /storage/services/AutoBackup/FAC/screens-iocs_$timestamp.tar"
# cd /home/sirius/shared && rsync -avzh screens-iocs sirius@10.128.255.3:/storage/services/AutoBackup/FAC/$timestamp"
cd /home/sirius/repos-dev && rsync -avzh scripts -e ssh sirius@10.128.255.3:/storage/services/AutoBackup/FAC/$timestamp
