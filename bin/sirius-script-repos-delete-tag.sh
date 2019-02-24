#!/usr/bin/env bash

repos_path=/home/sirius/repos

repos=("scripts"
       "mathphys"
       "dev-packages"
       "machine-applications")


function get_password {
 if [ -z "$fac_passwd" ]; then
   read -s -r -p "sirius user's password @ desktops: " sirius_passwd; echo ""
 fi
 printf "\n"
}

function delete_tag {
  printf "Delete tag \e[1;34m'$tag'\e[0m...\n"
  read -s -r -p "Are you sure [NO/yes]?: " answer; echo ""
  if [ "$answer" != 'yes' ]; then
    printf "\e[1;31mbailing out...\e[0m]\n"
    exit
  fi
  get_password
  for repo in "${repos[@]}"; do
    echo "deleting in local repo $repo..."
    cd $repos_path/$repo
    git tag -d $tag
    git push --delete origin $tag
    echo "deleting in lnls452-linux repo $repo..."
    sshpass -p $sirius_passwd ssh sirius@lnls452-linux "cd /home/nfs-shared/repos-lnls-sirius/$repo; git tag -d $tag"
  done
}

tag=$1
delete_tag
