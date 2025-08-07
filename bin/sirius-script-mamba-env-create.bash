#!/usr/bin/env bash

# Exit if any command fails
set -e

##############################################################################
# Parse arguments.
# Adapted from: https://stackabuse.com/how-to-parse-command-line-arguments-in-bash/

help()
{
    echo "Usage: sirius-script-mamba-env-create.bash
    [ -c | --clone-repos ] Instead of finding repos in system, clone them inside environment folder.
    [ -f | --clone-folder ] If repos will be cloned, clone them in this folder. Default: ~/repos.
    [ -d | --develop ] Install sirius packages in develop mode.
    [ --no-sim ] Do not install simulation packages.
    [ --no-ioc ] Do not install IOC related packages.
    [ --no-ima ] Do not install magnets simulation packages.
    [ --no-colleff ] Do not install collective effects packages.
    [ -r | --root-lnls-repos ] Root folder for lnls repos. Default: \"/\".
    [ -b | --branches ] Branches to install. For each package you want to force a branch you must provide:
            <package1>:<branch1>,<package2>:<branch2>,...,<packagen>:<branchn>
        Please note there is no spaces in the string.
        If you want to force all packages to have the same branch you can do:
            all:<branch>
        If you want to force some specific branch for a given package and some
        other to all other packages, you can do:
            <packagei>:<branchi>,all:<def_branch>
        If nothing is passed or if some package is missing in this definition,
        the current branch will be installed.
    [ -e | --env-name ] Mamba env name. Default: \"sirius\".
    [ -h | --help  ] Print help and exit."
}

SHORT="cf:dr:b:e:h"
LONG+="clone-repos,clone-folder:,develop,no-sim,no-ioc,no-ima,no-colleff,"
LONG+="root-lnls-repos:,branches:,env-name:,help"
OPTS=$(getopt -a -n sirius-script-mamba-env-create.bash \
    --options $SHORT --longoptions $LONG -- "$@")

# Exit in case getopt return with error:
if [ $? -ne 0 ]
then
    help
    exit 0
fi

eval set -- "$OPTS"

CLONE="no"
CLONE_FOL="~/repos"
DEVELOP="no"
INST_SIM="yes"
INST_IOC="yes"
INST_IMA="yes"
INST_COL="yes"
ROOT_REP="/"
BRANCHES=""
ENV_NAME="sirius"
# now enjoy the options in order and nicely split until we see --
while true; do
    case "$1" in
        -c|--clone-repos)
            CLONE="yes"
            shift
            ;;
        -f|--clone-folder)
            CLONE_FOL="$2"
            shift 2
            ;;
        -d|--develop)
            DEVELOP="yes"
            shift
            ;;
        --no-sim)
            INST_SIM="no"
            shift
            ;;
        --no-ioc)
            INST_IOC="no"
            shift
            ;;
        --no-ima)
            INST_IMA="no"
            shift
            ;;
        --no-colleff)
            INST_COL="no"
            shift
            ;;
        -r|--root-lnls-repos)
            ROOT_REP="$2"
            shift 2
            ;;
        -b|--branches)
            BRANCHES="$2,$BRANCHES"
            # split string in array at delimiter ",":
            BRANCHES=(${BRANCHES//,/ })
            shift 2
            ;;
        -e|--env-name)
            ENV_NAME="$2"
            shift 2
            ;;
        -h|--help)
            help
            shift
            exit 0
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unexpected option: $1"
            help
            exit 2
            ;;
    esac
done

##############################################################################
# Define some useful functions
printf_yellow()
{
  printf "\e[1;33m$1\e[0m"
}
printf_yellow_clear()
{
  printf "\e[0;33m$1\e[0m"
}
printf_blue()
{
  printf "\e[1;34m$1\e[0m"
}
printf_green()
{
  printf "\e[1;32m$1\e[0m"
}
printf_red()
{
  printf "\e[1;31m$1\e[0m"
}
_abort()
{
  printf_red "SIGINT received. Aborting...\n"
  exit
}

# Trap SIG INT to abort exectution:
trap _abort SIGINT;

get_branch()
{
    for BRAN in "${BRANCHES[@]}"
    do
        local BR=(${BRAN//:/ })  # split string in array in delimiter ":"
        if [ "${BR[0]}" == "$1" ]
        then
            echo ${BR[1]}
            break
        fi
    done
}

# This function extracts the organization and repo name from a
# remote.origin.url of a given repository.
# It was done by Microsoft Windows Copilot and works for urls such as:
#    - git@github.com:org/repo.git
#    - https://gitlab.com/org/repo.git
#    - git@bitbucket.org:org/repo.git
#    - lnls-sirius/scripts.git
extract_info_git()
{
    local url="$1"
    local path=$(echo "$url" | sed -E 's|.*[:/]([^/]+/[^/]+)$|\1|')
    path=${path%.git}
    local org=$(echo "$path" | cut -d'/' -f1)
    local repo=$(echo "$path" | cut -d'/' -f2)
    echo "$org" "$repo"
}

# takes three input variables: repo name, organization, and repo tag/branch
clone_or_find()
{
    printf_yellow " - $1\n"
    if [ "$CLONE" == "yes" ]
    then
        printf_yellow_clear "Cloning repo $1 in $CLONE_FOL: \n"
        cd $CLONE_FOL
        if ! [ -d "$1" ]
        then
            git clone https://github.com/$2/$1.git
            printf_green "done\n"
        else
            printf_blue "already cloned. Skipping...\n"
        fi
        cd $1
    else
        printf_yellow_clear "Searching repo $1 in $ROOT_REP: "
        local PTH=
        local VAR="$(find "$ROOT_REP" -path */$1 2>/dev/null)"
        VAR=($VAR)
        for V in "${VAR[@]}"
        do
            cd $V
            if git rev-parse --is-inside-work-tree 1>/dev/null 2>&1
            then
                local NAME=$(git config --get remote.origin.url)
                NAME=$(extract_info_git "$NAME")
                if [ "$NAME" == "$2 $1" ]
                then
                    PTH=$(git rev-parse --show-toplevel)
                    break
                fi
            fi
        done

        if [ "$PTH" ]
        then
            cd $PTH
            printf_green "Found in $PTH\n"
        else
            printf_blue "Not found. Skipping install...\n"
            return 1
        fi
    fi
    local BRAN="$(get_branch $1)"
    if ! [ "$BRAN" ]
    then
        BRAN="$(get_branch all)"
    fi
    if [ "$BRAN" ]
    then
        printf_yellow_clear "Checking out to branch $BRAN.\n"
        git checkout $BRAN
    fi
}

##############################################################################
printf_yellow "Install system dependencies.\n"
sudo apt-get update
# libgl1-mesa-glx is needed for pyqt to work properly.
# See discussion in:
#    https://github.com/conda-forge/pygridgen-feedstock/issues/10
sudo apt-get install -y wget git libgl1-mesa-glx wmctrl

##############################################################################
printf_yellow "Configure system for mamba installation\n"

USER="$(whoami)"
printf_yellow_clear "User $USER identified.\n"

printf_yellow_clear "Create group mamba in system: "
GROUP="$(getent group mamba)"
if ! [ $GROUP ]
then
    sudo groupadd mamba
    printf_green "done!\n"
else
    printf_blue "group already exists. Skipping...\n"
fi

printf_yellow_clear "Add user $USER to group mamba: "
if ! [[ $GROUP == *"$USER"* ]]
then
    sudo adduser $USER mamba
    printf_green "done!\n"
else
    printf_blue "already a member. Skipping...\n"
fi

cd /opt
printf_yellow_clear "Create folder /opt/mamba_files for mamba installation: "
if ! [ -d mamba_files ]
then
    sudo mkdir mamba_files
    printf_green "done!\n"
    printf_yellow_clear "Change permissions of folder /opt/mamba_files.\n"
    sudo chown -R $USER:mamba mamba_files
    chmod 774 -R mamba_files
else
    printf_blue "folder already exists. Skipping...\n"
fi

##############################################################################
printf_yellow_clear "Install mamba in path /opt/mamba_files/mamba: "
cd /opt/mamba_files
if ! [ -d mamba ]
then
    fname="Miniforge3-Linux-x86_64.sh"
    wget https://github.com/conda-forge/miniforge/releases/latest/download/$fname
    sh $fname -b -p /opt/mamba_files/mamba
    rm $fname
    printf_green "done!\n"
else
    printf_blue "there already is a mamba installation. Skipping...\n"
fi

printf_yellow_clear "Fix some folder permissions.\n"
sudo chgrp -R mamba /opt/mamba_files/mamba
sudo chmod 774 -R /opt/mamba_files/mamba
sudo chown -R $USER:mamba ~/.conda

printf_yellow_clear "Adding mamba and conda to path\n"
source /opt/mamba_files/mamba/etc/profile.d/conda.sh
export MAMBA_ROOT_PREFIX='/opt/mamba_files/mamba'
eval "$(mamba shell hook --shell bash)"

printf_yellow_clear "Adding mamba and conda paths to .bashrc: "
cd ~/
if ! grep -q "CONDA_ADD" .bashrc;
then
    cat >> ~/.bashrc <<'EOM'
# add conda and mamba to path
CONDA_ADD=/opt/mamba_files/mamba/etc/profile.d/conda.sh
if [ -f "$CONDA_ADD" ] ; then
    source "$CONDA_ADD"
fi
export MAMBA_ROOT_PREFIX='/opt/mamba_files/mamba'
eval "$(mamba shell hook --shell bash)"
EOM
    printf_green "done!\n"
else
    printf_blue "paths already in ~/.bashrc file. Skipping...\n"
fi

##############################################################################
printf_yellow "Create and prepare mamba enviroment\n"
printf_yellow_clear "Create new mamba python environment named $ENV_NAME: "
if ! mamba env list | grep -q $ENV_NAME
then
    mamba create --name $ENV_NAME python=3.9.2 -y
    printf_green "done!\n"
else
    printf_blue "environment already exists. Skipping...\n"
fi

### Activate Environment and do stuff
printf_yellow_clear "Activate $ENV_NAME enviroment\n"
mamba activate $ENV_NAME

printf_yellow_clear "create link for python-sirius inside the enviroment: "
cd $CONDA_PREFIX/bin
if ! [ -f python-sirius ]
then
    ln -s python3 python-sirius
    printf_green "done!\n"
else
    printf_blue "link already exists. Skipping...\n"
fi

printf_yellow "Install some mamba packages in $ENV_NAME environment.\n"
COMM="mamba install --freeze-installed -y"

printf_yellow_clear "- System and generic python packages:\n"
pip install build
# No not use freeze installed here, since it's the first time it is called.
mamba install -y gxx make binutils swig=4.2.0 libxcrypt gsl libblas wmctrl fftw \
    pyparsing bottleneck aiohttp==3.7.4 numpy=1.23 scipy matplotlib \
    pytest mpmath entrypoints requests pyqt=5.12.3 pandas pyqtgraph=0.11.0 \
    qtpy=2.3.1 QtAwesome=0.7.2 numexpr tk sh pywavelets scikit-image \
    scikit-learn pydocstyle pycodestyle pylama openpyxl gpy gpyopt fpdf sympy \
    h5py scienceplots seaborn

printf_yellow_clear "- Install EPICS Base:\n"
$COMM -c conda-forge/label/cf202003 epics-base=3.15.6

printf_yellow_clear "- And some other EPICS packages:\n"
$COMM pyepics=3.5.7 pcaspy==0.7.3 pydm=1.10.3 timechart=1.2.3
# remove the activate and deactivate files created by pyepics and pydm:
cd $CONDA_PREFIX/etc/conda/activate.d
if [ -f "pydm.bat" ]
then
    rm pydm.bat pydm.sh pyepics_activate.sh epics_base.sh
fi
cd $CONDA_PREFIX/etc/conda/deactivate.d
if [ -f "pydm.sh" ]
then
    rm pydm.sh pyepics_deactivate.sh epics_base.sh
fi

printf_yellow_clear "- Install and configure jupyter notebook\n"
$COMM jupyter notebook
mamba update jupyter_client

### Clone and install our repositories
if [ "$CLONE" == "yes" ]
then
    printf_yellow "Clone and install our applications.\n"
    printf_yellow_clear "Creating folder $CLONE_FOL: "
    if ! [ -d $CLONE_FOL ]
    then
        mkdir $CLONE_FOL
        printf_green "done!\n"
    else
        printf_blue "already exists. Skipping...\n"
    fi
else
    printf_yellow "Find and install our applications.\n"
fi

TARGET="install"
printf_yellow "\nSIRIUS packages will be installed in: "
if [ "$DEVELOP" == "yes" ]
then
    TARGET="develop-install"
    printf_green "Develop mode.\n\n"
else
    printf_green "Install mode.\n\n"
fi

printf_yellow_clear "Installing SIRIUS Control System related packages.\n"
clone_or_find mathphys lnls-fac && make $TARGET
clone_or_find dev-packages lnls-sirius && cd siriuspy && \
    make $TARGET
clone_or_find hla lnls-sirius && cd pyqt-apps && make $TARGET
clone_or_find hlafac lnls-fac && make $TARGET
if [ "$INST_SIM" == "yes" ]
then
    printf_yellow_clear "Installing accelerators simulation packages.\n"
    clone_or_find lnls lnls-fac && make $TARGET
    clone_or_find trackcpp lnls-fac && make clean && \
        make install-cpp && make install-py
    clone_or_find pyaccel lnls-fac && make $TARGET
    clone_or_find pymodels lnls-fac && make $TARGET
    clone_or_find apsuite lnls-fac && make $TARGET
fi
if [ "$INST_COL" == "yes" ]
then
    printf_yellow_clear "Installing collective effects simulation packages.\n"
    clone_or_find collective_effects lnls-fac && cd cppcolleff && \
        make clean && make install-cpp 2>/dev/null && \
        make $TARGET-py 2>/dev/null && cd ../pycolleff && make $TARGET
fi
if [ "$INST_IOC" == "yes" ]
then
    printf_yellow_clear "Installing SIRIUS IOCs related packages.\n"
    clone_or_find eth-bridge-pru-serial485 lnls-sirius && \
        cd client && make $TARGET
    clone_or_find machine-applications lnls-sirius && make $TARGET
fi
if [ "$INST_IMA" == "yes" ]
then
    printf_yellow_clear "Installing magnets simulation packages.\n"
    clone_or_find fieldmaptrack lnls-fac && make $TARGET
    clone_or_find Radia lnls-sirius && make install 2>/dev/null
    clone_or_find idanalysis lnls-fac && make $TARGET
    clone_or_find insertion-devices lnls-ids && make $TARGET
fi

printf_yellow_clear "Deactivate conda enviroment\n"
CONDA_PREF=$CONDA_PREFIX
mamba deactivate

printf_yellow "Add enviroment variables to conda environment\n"

#### Create file to configure environment activation
cat > $CONDA_PREF/etc/conda/activate.d/sirius_env.sh <<'EOM'
# Define function to set variable and save previous state
defvar()
{
    tmp="${1}"
    if ! [ -z "${!tmp+x}" ]
    then
        export $1_OLD="${!tmp}"
    fi
    export $1="${2}"
}
# EPICS
# =====
defvar "EPICS_BASE" "${CONDA_PREFIX}/epics"
defvar "EPICS_HOST_ARCH" 'linux-x86_64'
defvar "EPICS_CA_ADDR_LIST" "10.0.38.59:62000 10.30.13.22 10.30.14.19"
defvar "EPICS_PVA_ADDR_LIST" "10.0.38.59:62000 10.30.13.22 10.30.14.19"
defvar "SIRIUS_URL_RBAC_AUTH" "https://sirius-rbac-auth.lnls.br"
defvar "SIRIUS_URL_RBAC" "https://rbac:8445"
defvar "SIRIUS_URL_NS" "http://naming-service-wildfly:8089"
defvar "SIRIUS_URL_CCDB" "http://ccdb:8083"
defvar "SIRIUS_URL_CABLES" "http://cable:8086"
defvar "SIRIUS_URL_CONSTS" "http://10.0.38.59/control-system-constants"
defvar "SIRIUS_URL_CONSTS_2" "http://10.0.38.46/control-system-constants"
defvar "SIRIUS_URL_CONFIGDB" "http://10.0.38.59/config-db"
defvar "SIRIUS_URL_CONFIGDB_2" "http://10.0.38.46/config-db"
defvar "SIRIUS_URL_LOGBOOK" "http://sirius-logbook.lnls.br/Olog"
defvar "SIRIUS_URL_ARCHIVER" "https://ais-eng-srv-ta.cnpem.br"
defvar "SIRIUS_URL_ARCHIVER_OFFLINE_DATA" "https://archiver-temp.cnpem.br"
defvar "EPICS_CA_MAX_ARRAY_BYTES" "10000000"
defvar "CONDA_EPICS_BIN" "${EPICS_BASE}/bin/${EPICS_HOST_ARCH}"
defvar "PATH" "${CONDA_EPICS_BIN}:${PATH}"
# PyDM
# ====
defvar "PYDM_DESIGNER_ONLINE" "True"
defvar "PYDM_DEFAULT_PROTOCOL" "ca://"
defvar "PYDM_EPICS_LIB" "PYEPICS"
defvar "LC_NUMERIC" "en_US.UTF-8"
# PyQt
# ====
defvar "PYQTDESIGNERPATH" "$CONDA_PREFIX/repos/hla/pyqt-apps"
# Aliases
# ======="
alias g-conda="cd $CONDA_PREFIX"
EOM

#### Cria arquivo para configurar desativação do ambiente
cat > $CONDA_PREF/etc/conda/deactivate.d/sirius_env.sh <<'EOM'
# Define function to unset variable with previous state
undefvar()
{
    tmp="${1}"
    old="${tmp}_OLD"
    if [ -z "${!old+x}" ]
    then
        unset "${tmp}"
    else
        export $tmp="${!old}"
        unset "${old}"
    fi
}
# EPICS
# =====
undefvar "EPICS_BASE"
undefvar "EPICS_HOST_ARCH"
export PATH=`echo $PATH | sed "s|${CONDA_EPICS_BIN}:||"`
undefvar "CONDA_EPICS_BIN"
undefvar "EPICS_CA_ADDR_LIST"
undefvar "EPICS_PVA_ADDR_LIST"
undefvar "SIRIUS_URL_RBAC_AUTH"
undefvar "SIRIUS_URL_RBAC"
undefvar "SIRIUS_URL_NS"
undefvar "SIRIUS_URL_CCDB"
undefvar "SIRIUS_URL_CABLES"
undefvar "SIRIUS_URL_CONSTS"
undefvar "SIRIUS_URL_CONSTS_2"
undefvar "SIRIUS_URL_CONFIGDB"
undefvar "SIRIUS_URL_CONFIGDB_2"
undefvar "SIRIUS_URL_LOGBOOK"
undefvar "SIRIUS_URL_ARCHIVER"
undefvar "SIRIUS_URL_ARCHIVER_OFFLINE_DATA"
undefvar "EPICS_CA_MAX_ARRAY_BYTES"
# PyDM
# ====
undefvar "PYDM_DESIGNER_ONLINE"
undefvar "PYDM_DEFAULT_PROTOCOL"
undefvar "PYDM_EPICS_LIB"
undefvar "LC_NUMERIC"
# PyQt
# ====
undefvar "PYQTDESIGNERPATH"
# Aliases
# =======
unalias g-conda
EOM

unset CONDA_PREF

##############################################################################
printf_yellow "Fix permissions of some files\n"
# needed for mamba clone
sudo chgrp -R mamba /opt/mamba_files/mamba/pkgs
sudo chmod -R og+r /opt/mamba_files/mamba/pkgs
# needed for mamba search
sudo chmod -R g+w /opt/mamba_files/mamba/pkgs/cache/*.json

##############################################################################
printf_yellow "Create scripts to access apps in conda environment\n"

cd /usr/local/bin
printf_yellow_clear " - jupyter-mamba-${ENV_NAME} \n"
sudo tee jupyter-mamba-${ENV_NAME} >/dev/null <<EOM
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate ${ENV_NAME} && jupyter notebook"
EOM

printf_yellow_clear " - ipython-mamba-${ENV_NAME} \n"
sudo tee ipython-mamba-${ENV_NAME} >/dev/null <<EOM
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate ${ENV_NAME} && ipython"
EOM

printf_yellow_clear " - designer-mamba-${ENV_NAME} \n"
sudo tee designer-mamba-${ENV_NAME} >/dev/null <<EOM
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate ${ENV_NAME} && designer"
EOM

printf_yellow_clear " - sirius-hla-as-ap-launcher-mamba-${ENV_NAME} \n"
sudo tee sirius-hla-as-ap-launcher-mamba-${ENV_NAME} >/dev/null <<EOM
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate ${ENV_NAME} && sirius-hla-as-ap-launcher.py"
EOM

sudo chmod +x jupyter-mamba-${ENV_NAME} ipython-mamba-${ENV_NAME} designer-mamba-${ENV_NAME} \
    sirius-hla-as-ap-launcher-mamba-${ENV_NAME}
