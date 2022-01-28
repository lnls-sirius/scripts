#!/usr/bin/env bash


function printf_yellow {
  printf "\e[1;33m$1\e[0m"
}
function printf_blue {
  printf "\e[1;34m$1\e[0m"
}
function printf_green {
  printf "\e[1;32m$1\e[0m"
}
function _abort {
  printf "\n"
  exit
}
trap _abort SIGINT;


printf_yellow "Install and configure conda channels\n"
printf_blue "Downloading and install conda...\n"
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
sh Miniconda3-latest-Linux-x86_64.sh -b -p /opt/conda
rm Miniconda3-latest-Linux-x86_64.sh

printf_blue "Create conda group\n"
groupadd conda
printf_blue "Adding sirius to conda group\n"
adduser sirius conda
printf_blue "Adjuste conda permissions\n"
chgrp -R conda /opt/conda

printf_blue "Adding conda to path\n" # (add to profile.d ?)
source /opt/conda/etc/profile.d/conda.sh

printf_blue "Configure conda channels\n"
conda config --add channels conda-forge
conda config --set channel_priority flexible

printf_yellow "Create and prepare conda enviroment\n"
printf_blue "Create new conda python environment\n"
# conda create --name conda_sirius python=3.6.8 -y
conda create --name conda_sirius python=3.9.2 -y

printf_blue "Activate conda enviroment\n"
conda activate conda_sirius

printf_blue "Install conda dependencies\n"
printf_green " - pyqt (5.12.3)\n"
conda install -c conda-forge -y pyqt=5.12.3  # brings qt
printf_green " - pyparsing (2.4.2)\n"
conda install -c conda-forge -y pyparsing=2.4.2
printf_green " - bottleneck (1.3.2)\n"
conda install -c conda-forge -y bottleneck=1.3.2
printf_green " - aiohttp (3.7.4)\n"
conda install -c conda-forge -y aiohttp=3.7.4
printf_green " - pyqtgraph (0.11.0)\n"
conda install -c conda-forge -y pyqtgraph=0.11.0
printf_green " - QtAwesome (0.7.2)\n"
conda install -c conda-forge -y QtAwesome=0.7.2
# printf_green " - matplotlib (3.1.2)\n"
#conda install -c conda-forge -y matplotlib=3.1.2
printf_green " - matplotlib (3.5.1)\n"
conda install -c conda-forge -y matplotlib=3.5.1
printf_green " - pytest (6.2.4)\n"
conda install -c conda-forge -y pytest=6.2.4
printf_green " - pyvisa (1.10.1)\n"
conda install -c conda-forge -y pyvisa=1.10.1
printf_green " - pyvisa-py (0.3.1)\n"
conda install -c conda-forge -y pyvisa-py=0.3.1

printf_blue "Install some packages using pip (to avoid install epics-base)\n"
printf_green " - pyepics (3.4.0)\n"
pip install pyepics==3.4.0
printf_green " - pcaspy (0.7.3)\n"
pip install pcaspy==0.7.3 # não consegui instalar pro python36 em debian11
printf_green " - pydm (1.10.3)\n"
pip install pydm==1.10.3
printf_green " - timechart\n"
pip install timechart

printf_blue "Install and configure Jupyter notebook\n"
conda install -c conda-forge -y jupyter notebook
conda update jupyter_client  # não precisou pra python39
conda install -c conda-forge -y jupyter_contrib_nbextensions=0.5.1
printf_blue "Adding conda environment to Jupyter kernels\n"
python -m ipykernel install --name=conda_sirius

printf_blue "Cloning and install our applications in repos\n"
cd $CONDA_PREFIX
mkdir repos
cd repos

printf_green " - MathPhys\n"
git clone https://github.com/lnls-fac/mathphys.git && cd mathphys && git checkout improve-install && make install
printf_green " - SiriusPy\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-sirius/dev-packages.git && cd dev-packages/siriuspy && git checkout improve-install && make install

printf_green " - LNLS\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/lnls.git && cd lnls && git checkout improve-install && make install
printf_green " - TrackCpp\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/trackcpp.git && cd trackcpp && git checkout improve-install && make clean && make install
printf_green " - PyAccel\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/pyaccel.git && cd pyaccel && git checkout improve-install && make install
printf_green " - PyModels\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/pymodels.git && cd pymodels && git checkout improve-install && make install
printf_green " - Apsuite\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/apsuite.git && cd apsuite && git checkout improve-install && make install

printf_green " - HLA\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-sirius/hla.git && cd hla/pyqt-apps && git checkout improve-install && make install
printf_green " - HLA FAC\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-fac/hlafac.git && cd hlafac && git checkout improve-install && make install

printf_green " - Eth-bridge-pru-serial485\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-sirius/eth-bridge-pru-serial485.git && cd eth-bridge-pru-serial485 && cd client && git checkout v2.7.1 && pip install --no-deps --compile ./
printf_green " - Machine Applications\n"
cd $CONDA_PREFIX/repos && git clone https://github.com/lnls-sirius/machine-applications.git && cd machine-applications && git checkout improve-install && make install

printf_blue "Adding enviroment variables to conda environment\n"
echo "# PyDM" > $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh
echo "# ====" >> $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh
echo "export PYDM_DESIGNER_ONLINE=True" >> $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh
echo "export PYDM_DEFAULT_PROTOCOL=\"ca://\"" >> $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh
echo "export PYDM_EPICS_LIB="PYEPICS"  # PYEPICS, PYCA, CAPROTO" >> $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh
echo "export LC_NUMERIC=en_US.UTF-8" >> $CONDA_PREFIX/etc/conda/activate.d/pydm_app.sh

echo "# PyQt" > $CONDA_PREFIX/etc/conda/activate.d/sirius_hla.sh
echo "# ====" >> $CONDA_PREFIX/etc/conda/activate.d/sirius_hla.sh
echo "export PYQTDESIGNERPATH=$CONDA_PREFIX/repos/hla/pyqt-apps" >> $CONDA_PREFIX/etc/conda/activate.d/sirius_hla.sh

echo "# PyDM" > $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh
echo "# ====" >> $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh
echo "unset PYDM_DESIGNER_ONLINE" >> $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh
echo "unset PYDM_DEFAULT_PROTOCOL" >> $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh
echo "unset PYDM_EPICS_LIB" >> $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh
echo "unset LC_NUMERIC" >> $CONDA_PREFIX/etc/conda/deactivate.d/pydm_app.sh

echo "# PyQt" > $CONDA_PREFIX/etc/conda/deactivate.d/sirius_hla.sh
echo "# ====" >> $CONDA_PREFIX/etc/conda/deactivate.d/sirius_hla.sh
echo "unset PYQTDESIGNERPATH" >> $CONDA_PREFIX/etc/conda/deactivate.d/sirius_hla.sh

printf_blue "Create python-sirius symlink (necessary for scripts)\n"
cd $CONDA_PREFIX/bin && ln -s python3 python-sirius

printf_blue "Deactivate conda enviroment\n"
conda deactivate

printf_blue "Fix permissions in /opt/conda/pkgs after install root environments\n"
chgrp -R conda /opt/conda/pkgs  # necessary for conda clone...
chmod -R o+r /opt/conda/pkgs  # necessary for conda clone...
chmod -R g+r /opt/conda/pkgs  # necessary for conda clone...
chmod -R g+w /opt/conda/pkgs/cache/*.json  # necessary for conda search...

printf_blue "Create scripts to access apps in conda environment\n"
printf_green " - jupyter-sirius \n"
echo "#!/bin/bash" > /usr/local/bin/jupyter-sirius
echo "bash -c \"source /opt/conda/etc/profile.d/conda.sh && conda activate conda_sirius && jupyter notebook\"" >> /usr/local/bin/jupyter-sirius
chmod +x /usr/local/bin/jupyter-sirius

printf_green " - ipython-sirius \n"
echo "#!/bin/bash" > /usr/local/bin/ipython-sirius
echo "bash -c \"source /opt/conda/etc/profile.d/conda.sh && conda activate conda_sirius && ipython\"" >> /usr/local/bin/ipython-sirius
chmod +x /usr/local/bin/ipython-sirius

printf_green " - designer-sirius \n"
echo "#!/bin/bash" > /usr/local/bin/designer-sirius
echo "bash -c \"source /opt/conda/etc/profile.d/conda.sh && conda activate conda_sirius && designer\"" >> /usr/local/bin/designer-sirius
chmod +x /usr/local/bin/designer-sirius

printf_green " - sirius-hla-as-ap-launcher \n"
echo "#!/bin/bash" > /usr/local/bin/sirius-hla-as-ap-launcher
echo "bash -c \"source /opt/conda/etc/profile.d/conda.sh && conda activate conda_sirius && sirius-hla-as-ap-launcher.py\"" >> /usr/local/bin/sirius-hla-as-ap-launcher
chmod +x /usr/local/bin/sirius-hla-as-ap-launcher
