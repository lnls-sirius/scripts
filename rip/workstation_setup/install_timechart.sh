
cd /tmp
git clone https://github.com/slaclab/timechart.git
cd timechart
git checkout v1.2.2
sudo -EH python-sirius setup.py install
cd ../
sudo rm -r timechart
