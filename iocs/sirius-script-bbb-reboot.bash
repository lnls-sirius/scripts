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
      "bbb-bo-dipole-1"
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
      "bbb-bo-correctors-13"
      )


function my_abort {
  printf "\n"
  exit
}

trap my_abort SIGINT;

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

function run_ping {
  cat /etc/hosts | cut -d" " -f1-2 | grep "bbb-" > /tmp/hosts-log
  nr_oks=0
  for bbb in "${bbbs[@]}"; do
    ip=`cat /tmp/hosts-log | grep $bbb | sed "s/$bbb//g" | sed "s/ //g"`
    printf_white "pinging $bbb ($ip) ... "
    if ping -q -c 2 -W 1 $bbb > /dev/null; then
      printf_green "ok\n"
      let "nr_oks++"
    else
      printf_red "fail\n"
    fi
  done
  if [ "$nr_oks" != "${#bbbs[@]}" ]; then
    printf "\e[1;31mAt least one beaglebone is not pinging!\e[0m\n"
  else
    printf "\e[1;32mAll beaglebones are pinging!\e[0m\n"
  fi
}

function run_reboot {
  cat /etc/hosts | cut -d" " -f1-2 | grep "bbb-" > /tmp/hosts-log
  for bbb in "${bbbs[@]}"; do
    ip=`cat /tmp/hosts-log | grep $bbb | sed "s/$bbb//g" | sed "s/ //g"`
    printf "rebooting $bbb ($ip)...\n"
    curl --header "Content-Type: application/json" -k --request POST --data "{\"ip\":\"${ip}\"}" https://servbbbdaemon/bbb-daemon/api/node/reboot
  done
}

$1
