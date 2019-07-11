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
      "bbb-bo-correctors-13")

desktops=("lnls454-linux"
          "lnls452-linux"
          "lnls451-linux"
          "lnls449-linux"
          "lnls455-linux"
          "elp-pwrsupply")

repos=("scripts:master"
       "mathphys:master"
       "control-system-constants:master"
       "dev-packages:master"
       "machine-applications:master"
       "hla:master"
       "linac-opi:master"
       "bbb-daemon:master"
       "ARM:deploy-v0.32-2019-04-10"
       "C28:deploy-v0.32-2019-04-10")

services_lnls454=(
         "sirius-ioc-tb-ma-dipoles.service"
         "sirius-ioc-tb-ma-quadrupoles.service"
         "sirius-ioc-tb-ma-correctors.service"
         "sirius-ioc-bo-ma-dipoles.service"
         "sirius-ioc-bo-ma-quadrupoles.service"
         "sirius-ioc-bo-ma-sextupoles.service"
         "sirius-ioc-bo-ma-correctors-01.service"
         "sirius-ioc-bo-ma-correctors-02.service"
         "sirius-ioc-bo-ma-correctors-03.service"
         "sirius-ioc-bo-ma-correctors-04.service"
         "sirius-ioc-bo-ma-correctors-05.service"
         "sirius-ioc-bo-ma-correctors-06.service"
         "sirius-ioc-bo-ma-correctors-07.service"
         "sirius-ioc-bo-ma-correctors-08.service"
         "sirius-ioc-bo-ma-correctors-09.service"
         "sirius-ioc-bo-ma-correctors-10.service"
         "sirius-ioc-bo-ma-correctors-11.service"
         "sirius-ioc-bo-ma-correctors-12.service"
         "sirius-ioc-bo-ma-correctors-13.service"

         "sirius-ioc-tb-ps-diag.service"
         "sirius-ioc-bo-ps-diag.service"
         # "sirius-ioc-ts-ps-diag.service"
         # "sirius-ioc-si-ps-diag-fam.service"
         # "sirius-ioc-si-ps-diag-ch.service"
         # "sirius-ioc-si-ps-diag-cv.service"
         # "sirius-ioc-si-ps-diag-qs.service"
         # "sirius-ioc-si-ps-diag-fc.service"
         # "sirius-ioc-si-ps-diag-trim-01.service"
         # "sirius-ioc-si-ps-diag-trim-02.service"

         "sirius-ioc-tb-pm-injsept.service"
         "sirius-ioc-bo-pm-injkckr.service"


         "sirius-ioc-as-ti-evts.service"
         "sirius-ioc-as-ti-trig.service"
         "sirius-ioc-li-ti-trig.service"
         "sirius-ioc-tb-ti-trig.service"
         "sirius-ioc-bo-ti-trig.service"
         "sirius-ioc-ts-ti-trig.service"
         "sirius-ioc-si-ti-trig.service"

         "sirius-ioc-bo-ap-currinfo-current.service"
         "sirius-ioc-bo-ap-currinfo-lifetime.service"
         #"sirius-ioc-si-ap-currinfo-charge.service"  # Broken!
         "sirius-ioc-si-ap-currinfo-current.service"
         "sirius-ioc-si-ap-currinfo-lifetime.service"

         "sirius-ioc-tb-ap-posang.service"
         "sirius-ioc-ts-ap-posang.service"

         "sirius-ioc-tb-ap-sofb.service"
         "sirius-ioc-bo-ap-sofb.service"
         "sirius-ioc-ts-ap-sofb.service"
         "sirius-ioc-si-ap-sofb.service"

         "sirius-ioc-bo-ap-tunecorr.service"
         "sirius-ioc-bo-ap-chromcorr.service"
         "sirius-ioc-si-ap-tunecorr.service"
         "sirius-ioc-si-ap-chromcorr.service"
         )

mirror_repos_path=/home/sirius/repos

servweb_hostname=sirius-consts.lnls.br

servnfs_hostname=lnls454-linux

servnfs_repos_folder=/home/nfs-shared/repos-lnls-sirius/


# --- aux functions ---

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
  ip=$(cat /etc/hosts | grep $bbb | sed "s/ \+/ /g" | cut -d" " -f1)
  echo $ip
}

function get_timestamp {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo $timestamp
}

function get_tmpdir {
  timestamp=$(get_timestamp)
  prefix=$1
  if [[ -z "$prefix" ]]; then
    tmpdir="/tmp/sirius-script-"$timestamp
  else
    tmpdir="/tmp/sirius-script-"$prefix"-"$timestamp
  fi
  echo $tmpdir
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
  hosttype=$2
  read -s -r -p "$username's password @ $hosttype: " user_passwd; echo ""
  if [ "$hosttype" == "desktops" ]; then
    res=$( sshpass -p $user_passwd ssh sirius@$servnfs_hostname ls 2>&1 |grep denied)
    if [ ! -z "$res" ]; then
      echo "Invalid Password."
      exit 1
    fi
  fi
  printf "\n"
}

function check_repo_install {
  # repo=$(echo $1 | cut -d":" -f1)
  tmpdir=$2
  fname="$tmpdir/log-install-$repo.stderr"
  err=$(cat $fname)
  echo $err
}

function create_deploy_tag {
  timestamp=$(get_timestamp)
  echo "deploy-"$timestamp"_"$USER"_"$LINUX_HOSTNAME
}

# --- command functions  ---

function cmd_bbb_ping {
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

function cmd_bbb_uptime {
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

function cmd_bbb_reboot {
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

function cmd_repo_install {
  repo=$(echo $1 | cut -d":" -f1)
  tmpdir="$2"
  if [[ ! -d "$mirror_repos_path/$repo" ]]; then
    echo "repo '$repo' is missing in '$mirror_repos_path'!" > $tmpdir/log-install-$repo.stderr
    var_error=$(check_repo_install $repo $tmpdir)
    return
  fi
  cp -a $mirror_repos_path/$repo $tmpdir/
  cd $tmpdir/$repo
  if [ "$repo" == "scripts" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
    make install-hosts 1>> ../log-install-$repo.stdout 2>> ../log-install-$repo.stderr
  elif [ "$repo" == "mathphys" ]; then
    ./setup.py install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "dev-packages" ]; then
    cd ./siriuspy
    ./setup.py install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "machine-applications" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "pydm" ]; then
    # to avoid generating unnecessary stderr content about __file__ variable
    sed -i "s/license='BSD',/license='BSD',\n    zip_safe=False,/g" setup.py
    python-sirius setup.py install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "hla" ]; then
    cd ./pyqt-apps
    make install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "linac-opi" ]; then
    make install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "bbb-daemon" ]; then
    echo "" 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "control-system-constants" ]; then
    if [ "$(hostname)" == "$servweb_hostname" ]; then
      make install-html 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
    else
      echo "" 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
    fi
  else
    echo "installation not defined for $repo !" 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  fi
  var_error=$(check_repo_install $repo $tmpdir)
}

function cmd_repo_clone_master {
  repo=$(echo $1 | cut -d":" -f1)
  branch=$(echo $1 | cut -d":" -f2)
  tmpdir=$2
  cd $tmpdir
  if [ "$repo" == "mathphys" ]; then
      git clone ssh://git@github.com/lnls-fac/$repo
  elif [ "$repo" == "linac-opi" ]; then
      git clone lnls350-linux:/home/fac_files/repo/sirius/$repo
  else
      git clone ssh://git@github.com/lnls-sirius/$repo
  fi
  cd $repo
  git checkout $branch
}
