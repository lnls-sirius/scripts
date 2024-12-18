#!/bin/sh

set -e

if [ "$#" -ne 3 ]; then
	echo "Usage: $0 afcv3/afcv4-sfp mch-hostname slot" >&2
	exit 1
fi

board="$1"
mch="$2"
slot="$3"

if [ "$slot" -lt 1 ] || [ "$slot" -gt 12 ]; then
	echo "Invalid slot number: ${slot}" >&2
	exit 2
fi

port=$(( $slot + 2540 ))
svf_scansta=$(mktemp)
svf_boot=$(mktemp)

printf 'TRST OFF;
ENDIR IDLE;
ENDDR IDLE;
STATE RESET;
STATE IDLE;
//Operation: bsdebug -start
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
//Operation: bsdebug -reset
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
//Operation: bsdebug -scanir 00000000
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDIR IDLE;
SIR 8 TDI (00) SMASK (ff) MASK (ff) ;
//Operation: bsdebug -scanir 10100000
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDIR IDLE;
SIR 8 TDI (a0) ;
//Operation: bsdebug -scanir 10100101
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDIR IDLE;
SIR 8 TDI (a5) ;
//Operation: bsdebug -scandr 01011010
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDDR IDLE;
SDR 8 TDI (5a) SMASK (ff) MASK (ff) ;
//Operation: bsdebug -scanir 11000011
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDIR IDLE;
SIR 8 TDI (c3) ;
//Operation: bsdebug -scandr 01011010
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
ENDDR IDLE;
SDR 8 TDI (5a) ;
//Operation: bsdebug -stop
TIR 0 ;
HIR 0 ;
TDR 0 ;
HDR 0 ;
' > "$svf_scansta"

printf 'TRST OFF;
ENDIR IDLE;
ENDDR IDLE;
HIR 0;
TIR 0;
HDR 0;
TDR 0;
RUNTEST 625000 TCK;
SIR 6 TDI (0b);
STATE RESET;
RUNTEST 200000 TCK;
STATE RESET;
' > "$svf_boot"

if [ "$board" == "afcv3" ]; then
	scansta_cmd="svf ${svf_scansta} -quiet"
	sfp_jtag=""
elif [ "$board" == "afcv4-sfp" ]; then
	scansta_cmd=""
	sfp_jtag="jtag newtap fmc_4sfp tap -irlen 8 -ignore-version -expected-id 0x16d4a093"
else
	echo "Invalid board type: ${board}" >&2
	exit 3
fi

openocd -c "adapter driver xvc" \
		-c "xvc_host ${mch}" \
		-c "xvc_port ${port}" \
		-c "${sfp_jtag}" \
		-c "source [find cpld/xilinx-xc7.cfg]" \
		-c "adapter speed 3000" \
		-c "init" \
		-c "${scansta_cmd}" \
		-c "svf ${svf_boot} -quiet" \
		-c "exit"

rm "$svf_scansta"
rm "$svf_boot"
