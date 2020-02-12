sudo apt-get install -y libgif-dev libmotif-dev libxmu-dev libxmu-headers libxt-dev libxtst-dev xfonts-100dpi xfonts-75dpi x11proto-print-dev

if [ $(lsb_release -is) = 'Ubuntu' ]; then
    WEBADDR="http://mirror.ufscar.br/ubuntu/pool/main/libx/libxp/"
    FLIBXPDEV="libxp-dev_1.0.2-1ubuntu1_amd64.deb"
    FLIBXP6="libxp6_1.0.2-1ubuntu1_amd64.deb"
else
    WEBADDR="http://mirror.ufscar.br/debian/pool/main/libx/libxp/"
    FLIBXPDEV="libxp-dev_1.0.2-2_amd64.deb"
    FLIBXP6="libxp6_1.0.2-2_amd64.deb"
fi

echo "Dowloading libxp6 and libxp-dev"
wget $WEBADDR$FLIBXPDEV
wget $WEBADDR$FLIBXP6
echo "Installing libxp6 and libxp-dev"
sudo dpkg -i $FLIBXP6 $FLIBXPDEV
rm $FLIBXP6 $FLIBXPDEV

cd /opt/epics

echo "configuring extensions"
sudo sed -i -e '21cEPICS_BASE=/opt/epics/base' -e '25s/^/#/' extensions/configure/RELEASE
sudo sed -i -e '14cX11_LIB=/usr/lib/x86_64-linux-gnu' -e '18cMOTIF_LIB=/usr/lib/x86_64-linux-gnu' extensions/configure/os/CONFIG_SITE.linux-x86_64.linux-x86_64

echo "Entering extensions and Downloading EDM"
cd extensions/src
sudo git clone https://github.com/gnartohl/edm.git
cd edm
sudo git checkout V1-12-105B

sudo sed -i -e '15s/$/ -DGIFLIB_MAJOR=5 -DGIFLIB_MINOR=1/' giflib/Makefile
sudo sed -i -e 's| ungif||g' giflib/Makefile*

sudo -EH make

cd setup
sudo sed -i -e '53cfor libdir in baselib lib epicsPv locPv calcPv util choiceButton pnglib diamondlib giflib videowidget' setup.sh
sudo sed -i -e '79d' setup.sh
sudo sed -i -e '81i\ \ \ \ $EDM -add $EDMBASE/pnglib/O.$ODIR/lib57d79238-2924-420b-ba67-dfbecdf03fcd.so' setup.sh
sudo sed -i -e '82i\ \ \ \ $EDM -add $EDMBASE/diamondlib/O.$ODIR/libEdmDiamond.so' setup.sh
sudo sed -i -e '83i\ \ \ \ $EDM -add $EDMBASE/giflib/O.$ODIR/libcf322683-513e-4570-a44b-7cdd7cae0de5.so' setup.sh
sudo sed -i -e '84i\ \ \ \ $EDM -add $EDMBASE/videowidget/O.$ODIR/libTwoDProfileMonitor.so' setup.sh

sudo -EH HOST_ARCH=linux-x86_64 sh setup.sh
