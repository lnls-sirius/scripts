#!/usr/bin/env bash

bbbs=(
      "bbb-as-dclinks-tbts"
      "bbb-as-dclink-ia01"
      "bbb-as-dclink-ia02"
      "bbb-as-dclink-ia04"
      "bbb-as-dclink-ia05"
      "bbb-as-dclink-ia07"
      "bbb-as-dclink-ia08"
      "bbb-as-dclink-ia10"
      "bbb-as-dclink-ia11"
      "bbb-as-dclink-ia13"
      "bbb-as-dclink-ia14"
      "bbb-as-dclink-ia16"
      "bbb-as-dclink-ia17"
      "bbb-as-dclink-ia20"
      "bbb-tb-dipoles"
      "bbb-tb-correctors"
      "bbb-tb-quadrupoles"
      "bbb-bo-dipole-1"
      "bbb-bo-dipole-2"
      "bbb-bo-quadrupole-qf"
      "bbb-bo-quadrupole-qd"
      "bbb-bo-sextupole-sf"
      "bbb-bo-sextupole-sd"
      "bbb-bo-correctors-ia01"
      "bbb-bo-correctors-ia02"
      "bbb-bo-correctors-ia04"
      "bbb-bo-correctors-ia05"
      "bbb-bo-correctors-ia07"
      "bbb-bo-correctors-ia08"
      "bbb-bo-correctors-ia10"
      "bbb-bo-correctors-ia11"
      "bbb-bo-correctors-ia13"
      "bbb-bo-correctors-ia14"
      "bbb-bo-correctors-ia16"
      "bbb-bo-correctors-ia17"
      "bbb-bo-correctors-ia20"
      "bbb-ts-correctors"
      "bbb-ts-dipoles"
      "bbb-ts-quadrupoles-12"
      "bbb-ts-quadrupoles-34"
      "bbb-si-dipoles"
      "bbb-si-quadrupoles-qf"
      "bbb-si-quadrupoles-qd1"
      "bbb-si-quadrupoles-qd2"
      "bbb-si-quadrupoles-q"
      "bbb-si-sextupoles-sfb0-sdb01"
      "bbb-si-sextupoles-sfa0p0-sda0p0"
      "bbb-si-sextupoles-sda1b12"
      "bbb-si-sextupoles-sfa12-sda3p1"
      "bbb-si-sextupoles-sfb12-sdb3"
      "bbb-si-sextupoles-sfp12-sdp23")

desktops=(
  "lnls454-linux"
  #"lnls452-linux"
  "lnls451-linux"
  "lnls449-linux"
  "lnls455-linux"
  "lnls560-linux"
  "elp-pwrsupply"
  )

repos=(
  "scripts:master"
  "mathphys:master"
  "control-system-constants:master"
  "dev-packages:master"
  "eth-bridge-pru-serial485:master"
  "machine-applications:master"
  "hla:master"
  "linac-ioc-ps:master"
  "linac-opi:master"
  #"bbb-daemon:master"
  #"ARM:deploy-v0.32-2019-04-10"
  #"C28:deploy-v0.32-2019-04-10"
  )

services_ioc_ps=(
  "sirius-ioc-as-ps-dclink-tbts.service"
  "sirius-ioc-as-ps-dclink-ia01.service"
  "sirius-ioc-as-ps-dclink-ia02.service"
  "sirius-ioc-as-ps-dclink-ia04.service"
  "sirius-ioc-as-ps-dclink-ia05.service"
  "sirius-ioc-as-ps-dclink-ia07.service"
  "sirius-ioc-as-ps-dclink-ia08.service"
  "sirius-ioc-as-ps-dclink-ia10.service"
  "sirius-ioc-as-ps-dclink-ia11.service"
  "sirius-ioc-as-ps-dclink-ia13.service"
  "sirius-ioc-as-ps-dclink-ia14.service"
  "sirius-ioc-as-ps-dclink-ia16.service"
  "sirius-ioc-as-ps-dclink-ia17.service"
  "sirius-ioc-as-ps-dclink-ia20.service"
  "sirius-ioc-tb-ps-dipoles.service"
  "sirius-ioc-tb-ps-quadrupoles.service"
  "sirius-ioc-tb-ps-correctors.service"
  "sirius-ioc-bo-ps-dipole-1.service"
  "sirius-ioc-bo-ps-dipole-2.service"
  "sirius-ioc-bo-ps-quadrupole-qf.service"
  "sirius-ioc-bo-ps-quadrupole-qd.service"
  "sirius-ioc-bo-ps-sextupole-sf.service"
  "sirius-ioc-bo-ps-sextupole-sd.service"
  "sirius-ioc-bo-ps-correctors-ia01.service"
  "sirius-ioc-bo-ps-correctors-ia02.service"
  "sirius-ioc-bo-ps-correctors-ia04.service"
  "sirius-ioc-bo-ps-correctors-ia05.service"
  "sirius-ioc-bo-ps-correctors-ia07.service"
  "sirius-ioc-bo-ps-correctors-ia08.service"
  "sirius-ioc-bo-ps-correctors-ia10.service"
  "sirius-ioc-bo-ps-correctors-ia11.service"
  "sirius-ioc-bo-ps-correctors-ia13.service"
  "sirius-ioc-bo-ps-correctors-ia14.service"
  "sirius-ioc-bo-ps-correctors-ia16.service"
  "sirius-ioc-bo-ps-correctors-ia17.service"
  "sirius-ioc-bo-ps-correctors-ia20.service"
  "sirius-ioc-ts-ps-dipoles.service"
  "sirius-ioc-ts-ps-quadrupoles-12.service"
  "sirius-ioc-ts-ps-quadrupoles-34.service"
  "sirius-ioc-ts-ps-correctors.service"
  "sirius-ioc-si-ps-dipoles.service"
  "sirius-ioc-si-ps-quadrupoles-qf.service"
  "sirius-ioc-si-ps-quadrupoles-qd1.service"
  "sirius-ioc-si-ps-quadrupoles-qd2.service"
  "sirius-ioc-si-ps-quadrupoles-q.service")

services_ioc_ma=(
  "sirius-ioc-tb-ma-dipoles.service"
  "sirius-ioc-tb-ma-quadrupoles.service"
  "sirius-ioc-tb-ma-correctors.service"
  "sirius-ioc-tb-pm-injsept.service"
  "sirius-ioc-bo-ma-dipoles.service"
  "sirius-ioc-bo-ma-quadrupoles.service"
  "sirius-ioc-bo-ma-sextupoles.service"
  "sirius-ioc-bo-ma-correctors-ia01.service"
  "sirius-ioc-bo-ma-correctors-ia02.service"
  "sirius-ioc-bo-ma-correctors-ia04.service"
  "sirius-ioc-bo-ma-correctors-ia05.service"
  "sirius-ioc-bo-ma-correctors-ia07.service"
  "sirius-ioc-bo-ma-correctors-ia08.service"
  "sirius-ioc-bo-ma-correctors-ia10.service"
  "sirius-ioc-bo-ma-correctors-ia11.service"
  "sirius-ioc-bo-ma-correctors-ia13.service"
  "sirius-ioc-bo-ma-correctors-ia14.service"
  "sirius-ioc-bo-ma-correctors-ia16.service"
  "sirius-ioc-bo-ma-correctors-ia17.service"
  "sirius-ioc-bo-ma-correctors-ia20.service"
  "sirius-ioc-ts-ma-dipoles.service"
  "sirius-ioc-ts-ma-quadrupoles-12.service"
  "sirius-ioc-ts-ma-quadrupoles-34.service"
  "sirius-ioc-ts-ma-correctors.service"
  "sirius-ioc-si-ma-dipoles.service"
  "sirius-ioc-si-ma-quadrupoles-qf.service"
  "sirius-ioc-si-ma-quadrupoles-qd1.service"
  "sirius-ioc-si-ma-quadrupoles-qd2.service"
  "sirius-ioc-si-ma-quadrupoles-q.service"
  "sirius-ioc-tb-pm-injsept.service"
  "sirius-ioc-bo-pm-injkckr.service"
  "sirius-ioc-bo-pm-ejekckr.service"
  "sirius-ioc-ts-pm-ejeseptf.service"
  "sirius-ioc-ts-pm-ejeseptg.service")

services_ioc_li_ps=(
  "sirius-ioc-li-ps-spect.service"
  "sirius-ioc-li-ps-ch1.service"
  "sirius-ioc-li-ps-ch2.service"
  "sirius-ioc-li-ps-ch3.service"
  "sirius-ioc-li-ps-ch4.service"
  "sirius-ioc-li-ps-ch5.service"
  "sirius-ioc-li-ps-ch6.service"
  "sirius-ioc-li-ps-ch7.service"
  "sirius-ioc-li-ps-cv1.service"
  "sirius-ioc-li-ps-cv2.service"
  "sirius-ioc-li-ps-cv3.service"
  "sirius-ioc-li-ps-cv4.service"
  "sirius-ioc-li-ps-cv5.service"
  "sirius-ioc-li-ps-cv6.service"
  "sirius-ioc-li-ps-cv7.service"
  "sirius-ioc-li-ps-lens-01.service"
  "sirius-ioc-li-ps-lens-02.service"
  "sirius-ioc-li-ps-lens-03.service"
  "sirius-ioc-li-ps-lens-04.service"
  "sirius-ioc-li-ps-lensrev.service"
  "sirius-ioc-li-ps-qd1.service"
  "sirius-ioc-li-ps-qd2.service"
  "sirius-ioc-li-ps-qf1.service"
  "sirius-ioc-li-ps-qf2.service"
  "sirius-ioc-li-ps-qf3.service"
  "sirius-ioc-li-ps-solenoid-01.service"
  "sirius-ioc-li-ps-solenoid-02.service"
  "sirius-ioc-li-ps-solenoid-03.service"
  "sirius-ioc-li-ps-solenoid-04.service"
  "sirius-ioc-li-ps-solenoid-05.service"
  "sirius-ioc-li-ps-solenoid-06.service"
  "sirius-ioc-li-ps-solenoid-07.service"
  "sirius-ioc-li-ps-solenoid-08.service"
  "sirius-ioc-li-ps-solenoid-09.service"
  "sirius-ioc-li-ps-solenoid-10.service"
  "sirius-ioc-li-ps-solenoid-11.service"
  "sirius-ioc-li-ps-solenoid-12.service"
  "sirius-ioc-li-ps-solenoid-13.service"
  "sirius-ioc-li-ps-solenoid-14.service"
  "sirius-ioc-li-ps-solenoid-15.service"
  "sirius-ioc-li-ps-solenoid-16.service"
  "sirius-ioc-li-ps-solenoid-17.service"
  "sirius-ioc-li-ps-solenoid-18.service"
  "sirius-ioc-li-ps-solenoid-19.service"
  "sirius-ioc-li-ps-solenoid-20.service"
  "sirius-ioc-li-ps-solenoid-21.service")

services_ioc_fac=(
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
  "sirius-ioc-si-ap-chromcorr.service")



mirror_repos_path=/home/sirius/repos

servweb_hostname=10.0.38.59

servnfs_hostname=lnls454-linux

servnfs_repos_folder=/home/nfs-shared/repos-lnls-sirius/

servweb_repodir=/home/con-srv/LA-disk0/misc-brick/repository/control-system-constants/

server_services_ioc_fac=lnls454-linux

server_services_ioc_li_ps=lnls560-linux

server_services_ioc_ps=lnls560-linux

server_services_ioc_ma=lnls454-linux

ansible_folder = /home/sirius/repos/lnls-ansible

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
  printf "%27s %16s" $bbb "($ip) ... "
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

function update_servweb {
  printf_green "Update servweb ($servweb_hostname)\n"
  printf "\n"
  branch=master
  sshpass -p $user_passwd ssh sirius@$servweb_hostname "cd $servweb_repodir; git stash; git fetch --prune origin '+refs/tags/*:refs/tags/*'; git checkout $branch; git pull; git checkout $deploy_tag"
  printf "\n"
}

function update_deploy_file {
  printf_green "Update deploy file in nfs server ($servnfs_hostname)\n"
  printf "\n"
  sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/; echo '$deploy_tag:  $comment' >> deploy.log"
}

function checkout_tagged_repos_nfs_server {
  update_deploy_file
  printf_green "Checkout tagged repos in nfs server ($servnfs_hostname)\n"
  printf "\n"
  for repo in "${repos[@]}"; do
    reponame=$(echo $repo | cut -d":" -f1)
    branch=$(echo $repo | cut -d":" -f2)
    printf_yellow "[$repo]\n"
    sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/$reponame; rm -rf dist build */*.egg-info *.egg-info"
    sshpass -p $user_passwd ssh sirius@$servnfs_hostname "cd $servnfs_repos_folder/$reponame; git checkout -- .; git fetch -p; git fetch --prune origin '+refs/tags/*:refs/tags/*'; git checkout $branch; git pull; git checkout $deploy_tag"
    printf "\n"
  done
}

function deploy_desktops {
  printf_green "Deploying in desktops\n"
  printf "\n"
  for desktop in "${desktops[@]}"; do
    printf_blue "[$desktop]\n"
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install-update.bash"
    sshpass -p $user_passwd ssh sirius@"$desktop" "sudo sirius-script-repos-install.bash"
    printf "\n"
  done
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
  elif [ "$repo" == "eth-bridge-pru-serial485" ]; then
    # to avoid generating unnecessary stderr content about __file__ variable
    cd ./client
    ./setup.py install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "pydm" ]; then
    # to avoid generating unnecessary stderr content about __file__ variable
    sed -i "s/license='BSD',/license='BSD',\n    zip_safe=False,/g" setup.py
    python-sirius setup.py install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "hla" ]; then
    cd ./pyqt-apps
    make install 1> ../../log-install-$repo.stdout 2> ../../log-install-$repo.stderr
  elif [ "$repo" == "linac-opi" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
  elif [ "$repo" == "linac-ioc-ps" ]; then
    make install 1> ../log-install-$repo.stdout 2> ../log-install-$repo.stderr
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
}

function cmd_repo_clone_master {
  repo=$(echo $1 | cut -d":" -f1)
  branch=$(echo $1 | cut -d":" -f2)
  tmpdir=$2
  cd $tmpdir
  if [ "$repo" == "mathphys" ]; then
      git clone ssh://git@github.com/lnls-fac/$repo
  elif [ "$repo" == "linac-opi" ]; then
      # git clone lnls350-linux:/home/fac_files/repo/sirius/$repo
      git clone git@gitlab.cnpem.br:FACS/$repo
  elif [ "$repo" == "linac-ioc-ps" ]; then
      # git clone lnls350-linux:/home/fac_files/repo/sirius/$repo
      git clone git@gitlab.cnpem.br:FACS/$repo
  else
      git clone ssh://git@github.com/lnls-sirius/$repo
  fi
  cd $repo
  git checkout $branch
}
