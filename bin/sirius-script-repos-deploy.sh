#!/usr/bin/env bash


repos=("mathphys"
       "dev-packages"
       "machine-applications")

desktops=("lnls451-linux"
          "lnls449-linux")

repos_path=/home/sirius/repos/


function get_deploy_tag {
  timestamp=`date '+%Y-%m-%d_%Hh%Mm%Ss'`
  echo $timestamp"_"$USER"_"$LINUX_HOSTNAME
}

function get_password {
  if [ -z "$fac_passwd" ]; then
    read -s -r -p "sirius user's password @ desktops: " sirius_passwd; echo ""
  fi
  printf "\n"
}

function printf_green {
  printf "\e[1;32m$1\e[0m\n"
}

function printf_yellow {
  printf "\e[1;33m$1\e[0m\n"
}

function printf_red {
  printf "\e[1;31m$1\e[0m\n"
}

function printf_blue {
  printf "\e[1;34m$1\e[0m\n"
}

function printf_white_bold {
  printf "\e[1m$1\e[0m\n"
}

function process_local_repo {
  repo=$1
  gittag=$2
  printf_green "Processing local $repo..."
  if [ ! -d "$repos_path$repo" ]; then
    printf_red ". repo path '$repos_path$repo' does not exist!"
    exit
  fi
  cd $repos_path$repo
  if [[ -z $(git status -s) ]]; then
    # check master
    printf_white_bold ". checkout and pull master..."
    git checkout master
    git pull
    # create new tag
    printf_white_bold ". creating tag ..."
    git tag $gittag
    # push up tags
    git push --tags
    printf "\n"
  else
    printf_red ". repo is not clean!"
    printf "\n"
    exit
  fi
}

function print_header {
  printf "\n"
  printf_blue "Deploy Sirius Repositories"
  printf_blue "tag: $tag"
  printf "\n"
}

function create_tagged_local_repos {
  printf_yellow "... local repositories ..."
  printf "\n"
  for repo in "${repos[@]}"; do
    process_local_repo $repo $tag
  done
}

function checkout_tag_lnls452 {
  printf_yellow "... checkout tag in nfs server (lnls452-linux) ..."
  printf "\n"
  for repo in "${repos[@]}"; do
    printf_green ". repo $repo"
    sshpass -p $sirius_passwd ssh sirius@lnls452-linux "cd /home/nfs-shared/repos-lnls-sirius/; echo "$tag" >> deploy.log; cd $repo; git stash save state-before-$tag; git fetch -p; git checkout $tag"
  done
}

function deploy_desktops {
  printf_yellow "... deploying in desktops ..."
  printf "\n"
  for desktop in "${desktops[@]}"; do
    printf_green "installing repos in $desktop..."
    sshpass -p $sirius_passwd ssh sirius@"$desktop" "sirius-script-repos-update-install.sh"
    sshpass -p $sirius_passwd ssh sirius@"$desktop" "sirius-script-repos-install.sh"
  done
}


tag=`get_deploy_tag`
print_header
get_password
create_tagged_local_repos
checkout_tag_lnls452
deploy_desktops
