
cd /tmp
git clone https://github.com/slaclab/timechart.git
cd timechart
sudo -EH python-sirius setup.py install
cd ../
rm -r timechart
