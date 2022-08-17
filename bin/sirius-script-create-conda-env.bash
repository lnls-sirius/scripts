#!/usr/bin/env bash

# Exit if any command fails
# set -e

##############################################################################
# Parse arguments.
# Adapted from: https://stackabuse.com/how-to-parse-command-line-arguments-in-bash/

function help
{
    echo "Usage: sirius-script-create-mamba-env.bash
               [ -c | --clone-repos ]
               [ -h | --help  ]"
    exit 2
}

SHORT=nh
LONG=no-clone-repos,help
OPTS=$(getopt -a -n weather --options $SHORT --longoptions $LONG -- "$@")

# Returns the count of arguments that are in short or long options
# VALID_ARGS=$#
# if [ "$VALID_ARGS" -eq 0 ]; then
#     help
# fi

eval set -- "$OPTS"

CLONE="yes"
# now enjoy the options in order and nicely split until we see --
while true; do
    case "$1" in
        -n|--no-clone-repos)
            CLONE="no"
            shift
            ;;
        -h|--help)
            help
            shift
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unexpected option: $1"
            help
            ;;
    esac
done

##############################################################################
# Define some useful functions
function printf_yellow {
  printf "\e[1;33m$1\e[0m"
}
function printf_blue {
  printf "\e[1;34m$1\e[0m"
}
function printf_green {
  printf "\e[1;32m$1\e[0m"
}
function printf_red {
  printf "\e[1;31m$1\e[0m"
}
function _abort {
  printf_red "SIGINT received. Aborting...\n"
  exit
}

# Trap SIG INT to abort exectution:
trap _abort SIGINT;

function clone_or_find
{
    printf_blue " - $1"
    if [ "$CLONE" == "yes" ]
    then
        cd $CONDA_PREFIX/repos
        if ! [ -d "$1" ]
        then
            git clone https://github.com/$2/$1.git
            printf_green "Repository $1 cloned!\n"
        else
            printf_red "Repository $1 already cloned. Skipping...\n"
        fi
        cd $1
    else
        VAR="$(find / -path */$1 2>/dev/null)"
        VAR=($VAR)
        VAR=${VAR[0]}
        if [ "$VAR" ]
        then
            cd $VAR
            printf_green "Repository $1 found in $VAR!\n"
        else
            printf_red "Package $1 not found! Skipping Installation..."
            return 1
        fi
    fi
}

##############################################################################
printf_yellow "Install system dependencies.\n"
sudo apt-get update
sudo apt-get install -y wget git

##############################################################################
printf_yellow "Install and configure mamba\n"

USER="$(whoami)"
printf_blue "User $USER identified.\n"

printf_blue "Create group mamba in system: "
GROUP="$(getent group mamba)"
if ! [ $GROUP ]
then
    sudo groupadd mamba
    printf_green "done!\n"
else
    printf_red "group already exists. Skipping...\n"
fi

printf_blue "Add user $USER to group mamba:\n"
if ! [[ $GROUP == *"$USER"* ]]
then
    sudo adduser $USER mamba
    printf_green "done!\n"
else
    printf_red "user $USER already a member of mamba. Skipping...\n"
fi

cd /opt
printf_blue "Create folder /opt/mamba_files to allocate mamba installation: "
if ! [ -d mamba_files ]
then
    sudo mkdir mamba_files
    printf_green "done!\n"
else
    printf_red "folder already exists. Skipping...\n"
fi

printf_blue "Change permissions of folder /opt/mamba_files.\n"
sudo chown -R $USER:mamba mamba_files
chmod 774 -R mamba_files
cd ~/

##############################################################################
printf_blue "Install mamba in path /opt/mamba_files/mamba: \n"
cd /opt/mamba_files
if ! [ -d mamba ]
then
    wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
    sh Mambaforge-Linux-x86_64.sh -b -p /opt/mamba_files/mamba
    rm Mambaforge-Linux-x86_64.sh
    printf_green "done!\n"
else
    printf_red "there already is a mamba installation. Skipping..."
fi

printf_blue "Fix some folder permissions.\n"
sudo chgrp -R mamba /opt/mamba_files/mamba
sudo chmod 774 -R /opt/mamba_files/mamba
sudo chown -R $USER.mamba ~/.conda

printf_blue "Adding mamba and conda to path\n"
source /opt/mamba_files/mamba/etc/profile.d/conda.sh
source /opt/mamba_files/mamba/etc/profile.d/mamba.sh

printf_blue "Adding mamba and conda paths to .bashrc\n"
cd ~/
if ! grep -q "MAMBA_ADD" .bashrc;
then
    cat >> ~/.bashrc <<'EOM'
# add conda and mamba to path
MAMBA_ADD=/opt/mamba_files/mamba/etc/profile.d/mamba.sh
if [ -f "$MAMBA_ADD" ] ; then
    source "$MAMBA_ADD"
fi
CONDA_ADD=/opt/mamba_files/mamba/etc/profile.d/conda.sh
if [ -f "$CONDA_ADD" ] ; then
    source "$CONDA_ADD"
fi
EOM
    printf_green "done!\n"
else
    printf_red "paths already in ~/.bashrc file. Skipping..."
fi

##############################################################################
printf_yellow "Create and prepare mamba enviroment\n"
printf_blue "Create new mamba python environment named sirius:"
if ! mamba env list | grep -q sirius
then
    mamba create --name sirius python=3.9.2 -y
    printf_green "done!\n"
else
    printf_red "environment already exists. Skipping...\n"
fi

### Activate Environment and do stuff
printf_blue "Activate sirius enviroment\n"
mamba activate sirius

printf_blue "create symbolic link for python-sirius inside the enviroment:"
cd $CONDA_PREFIX/bin
if ! [ -f python-sirius ]
then
    ln -s python3 python-sirius
    printf_green "done!\n"
else
    printf_red "link alreay exists. Skipping...\n"
fi

printf_blue "Install some mamba packages in sirius environment.\n"
COMM="mamba install --freeze-installed -y"

printf_blue "First some system packages:\n"
$COMM gxx make binutils swig build gsl libblas wmctrl
printf_blue "Now some generic python packages:\n"
$COMM pyparsing bottleneck aiohttp=3.7.4 scipy matplotlib pytest \
    entrypoints requests pyvisa=1.10.1 pyvisa-py=0.3.1 pyqt=5.12.3 \
    pyqtgraph=0.11.0 QtAwesome=0.7.2
printf_blue "Install EPICS Base:\n"
$COMM -c conda-forge/label/cf202003 epics-base=3.15.6
printf_blue "And some other EPICS packages:\n"
$COMM pyepics=3.5.0 pcaspy==0.7.3 pydm=1.10.3 timechart=1.2.3
printf_blue "Install and configure jupyter notebook\n"
$COMM jupyter notebook
mamba update jupyter_client
$COMM jupyter_contrib_nbextensions

printf_blue "Adding conda environment to Jupyter kernels\n"
sudo python -m ipykernel install --name=sirius

### Clone and install our repositories
if [ "$CLONE" == "yes" ]
then
    printf_blue "Clone and install our applications in repos:\n"
    if ! [ -d $CONDA_PREFIX/repos ]
    then
        mkdir $CONDA_PREFIX/repos
        printf_green "Created folder repos!\n"
    else
        printf_red "Folder repos already exists. Skipping..."
    fi
else
    printf_blue "Find and install our applications:\n"
fi
clone_or_find mathphys lnls-fac && make develop-install
clone_or_find dev-packages lnls-sirius && cd siriuspy && make develop-install
clone_or_find lnls lnls-fac && make develop-install
clone_or_find trackcpp lnls-fac && git checkout fix-conda && make clean && \
    make install-cpp  && make develop-install-py
clone_or_find pyaccel lnls-fac && make develop-install
clone_or_find pymodels lnls-fac && make develop-install
clone_or_find apsuite lnls-fac && make develop-install
clone_or_find hla lnls-sirius && pyqt-apps && make develop-install
clone_or_find hlafac lnls-fac && make develop-install
clone_or_find eth-bridge-pru-serial485 lnls-sirius && cd client && \
    pip install --no-deps -e ./
clone_or_find machine-applications lnls-sirius && make develop-install
clone_or_find idanalysis lnls-fac && make develop-install
clone_or_find Radia lnls-sirius && git checkout lnls-sirius && make install
clone_or_find insertion-devices lnls-ima && \
    git checkout feat-add-block-shape-and-mag-init && pip install -e ./

printf_blue "Adding enviroment variables to conda environment\n"

#### Cria arquivo para configurar ativação do ambiente
cat > $CONDA_PREFIX/etc/conda/activate.d/sirius_env.sh <<'EOM'
# Define function to set variable and save previous state
function defvar ()
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
defvar "EPICS_CA_ADDR_LIST" '10.0.38.46:60000 10.0.38.59:60000'
defvar "EPICS_PVA_ADDR_LIST" '10.0.38.46:60000 10.0.38.59:60000'
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
defvar "SIRIUS_URL_ARCHIVER" "https://10.0.38.42"
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
alias g-conda-repos="cd $CONDA_PREFIX/repos"
EOM

#### Cria arquivo para configurar desativação do ambiente
cat > $CONDA_PREFIX/etc/conda/deactivate.d/sirius_env.sh <<'EOM'
# Define function to unset variable with previous state
function undefvar ()
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
unalias g-conda-repos
EOM

printf_blue "Deactivate conda enviroment\n"
mamba deactivate

##############################################################################
printf_blue "Fix permissions of some files\n"
# needed for mamba clone
sudo chgrp -R mamba /opt/mamba_files/mamba/pkgs
sudo chmod -R og+r /opt/mamba_files/mamba/pkgs
# needed for mamba search
sudo chmod -R g+w /opt/mamba_files/mamba/pkgs/cache/*.json


printf_blue "Create scripts to access apps in conda environment\n"

printf_green " - jupyter-sirius \n"
sudo cat > /usr/local/bin/jupyter-sirius <<'EOM'
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate sirius && jupyter notebook"
EOM

printf_green " - ipython-sirius \n"
sudo cat > /usr/local/bin/ipython-sirius <<'EOM'
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate sirius && ipython"
EOM

printf_green " - designer-sirius \n"
sudo cat > /usr/local/bin/designer-sirius <<'EOM'
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate sirius && designer"
EOM

printf_green " - sirius-hla-as-ap-launcher \n"
sudo cat > /usr/local/bin/sirius-hla-as-ap-launcher <<'EOM'
#!/bin/bash
bash -c "source /opt/mamba_files/mamba/etc/profile.d/conda.sh && conda activate sirius && sirius-hla-as-ap-launcher.py"
EOM

cd /usr/local/bin
sudo chmod +x jupyter-sirius ipython-sirius designer-sirius sirius-hla-as-ap-launcher
