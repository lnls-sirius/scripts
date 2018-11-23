#!/usr/bin/env bash

# --- global variables ---

cmd=$1
fac_passwd=$2
linac_passwd=$3


# --- aux functions ---

function get_password {
  if [ -z "$fac_passwd" ]; then
    read -s -r -p "fac user's password @ bbbs: " fac_passwd; echo ""
  fi
  if [ -z "$linac_passwd" ]; then
    read -s -r -p "linac user's password @ desktop1: " linac_passwd; echo ""
  fi
}

# --- run script ---

get_password
sirius-script-ioc-ps.bash $cmd $fac_passwd
sirius-script-ioc-ps.bash $cmd $linac_passwd
