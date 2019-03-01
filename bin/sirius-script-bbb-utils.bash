#!/usr/bin/env bash

bbbs=("bbb-as-dclinks-01"
      "bbb-as-dclinks-02"
      "bbb-as-dclinks-03"
      "bbb-as-dclinks-04"
      "bbb-as-dclinks-05"
      "bbb-as-dclinks-06"
      "bbb-as-dclinks-07"
      "bbb-as-dclinks-08"
      "bbb-as-dclinks-09"
      "bbb-as-dclinks-10"
      "bbb-as-dclinks-11"
      "bbb-as-dclinks-12"
      "bbb-as-dclinks-13"
      "bbb-as-dclinks-14"
      "bbb-tb-dipoles"
      "bbb-tb-correctors"
      "bbb-tb-quadrupoles"
      # "bbb-bo-dipole-1"
      "bbb-bo-dipole-2"
      "bbb-bo-quadrupole-qf"
      "bbb-bo-quadrupole-qd"
      "bbb-bo-sextupole-sf"
      "bbb-bo-sextupole-sd"
      "bbb-bo-correctors-01"
      "bbb-bo-correctors-02"
      "bbb-bo-correctors-03"
      "bbb-bo-correctors-04"
      "bbb-bo-correctors-05"
      "bbb-bo-correctors-06"
      "bbb-bo-correctors-07"
      "bbb-bo-correctors-08"
      "bbb-bo-correctors-09"
      "bbb-bo-correctors-10"
      "bbb-bo-correctors-11"
      "bbb-bo-correctors-12"
      "bbb-bo-correctors-13")


function _abort {
  printf "\n"
  exit
}

function printf_green {
  printf "\e[1;32m$1\e[0m"
}

function printf_yellow {
  printf "\e[1;33m$1\e[0m"
}

function printf_red {
  printf "\e[1;31m$1\e[0m"
}

function printf_blue {
  printf "\e[1;34m$1\e[0m"
}

function printf_white {
  printf "\e[0m$1"
}

function printf_white_bold {
  printf "\e[1m$1\e[0m"
}

function get_bbb_ip {
  ip=$(cat /etc/hosts | cut -d" " -f1-2 | grep $bbb | sed "s/$bbb//g" | sed "s/ //g")
  echo $ip
}

function get_timestamp {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo $timestamp
}

function print_bbb_line {
  bbb=$1
  ip=$2
  printf "%22s %16s" $bbb "($ip) ... "
}

function print_header {
  func=$1
  nbbbs=$2
  timestamp=$(get_timestamp)
  printf_white_bold "$func\n"
  printf_white_bold "===================\n"
  printf_white_bold "number bbbs: $nbbbs\n"
  printf_white_bold "timestamp: $timestamp\n"
  printf "\n"
}

function get_password {
  username=$1
  read -s -r -p "$username's password @ beaglebones: " user_passwd; echo ""
  printf "\n"
}


# --- command ---

function cmd_ping {
  print_header "Pinging Beaglebones" $#
  lbbbs=${@}
  for bbb in ${lbbbs[@]}; do
    ip=$(get_bbb_ip $bbb)
    print_bbb_line $bbb $ip
    if ping -q -c 1 -W 1 $bbb > /dev/null; then
      printf_green "ok\n"
    else
      printf_red "fail\n"
    fi
  done
}

function cmd_uptime {
  print_header "Uptime Beaglebones" $#
  get_password fac
  lbbbs=${@}
  for bbb in ${lbbbs[@]}; do
    ip=$(get_bbb_ip $bbb)
    print_bbb_line $bbb $ip
    res=$(sshpass -p $user_passwd ssh -o LogLevel=Error -o ConnectTimeout=2 fac@$ip "uptime -p" 2> /dev/null)
    printf_blue "$res\n"
  done
}

function cmd_reboot {
  print_header "Rebooting Beaglebones" $#
  lbbbs=${@}
  for bbb in ${lbbbs[@]}; do
    ip=$(get_bbb_ip $bbb)
    print_bbb_line $bbb $ip
    printf "\n"
    curl --header "Content-Type: application/json" -k --request POST --data "{\"ip\":\"${ip}\"}" https://servbbbdaemon/bbb-daemon/api/node/reboot
    printf_blue "request sent!\n"
  done
}
