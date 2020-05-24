#!/bin/bash

git clone https://github.com/chs8691/heroscript.git

echo 
echo "Installing Garmin Downloader"
git clone https://github.com/chs8691/garmin-connect-export.git

echo 
echo "Installing Python3"
pkg install python      

echo 
echo "Installing Python2 for garmin downloader"
pkg install python2      

echo 
echo "Create directories"
cd heroscript
mkdir archive
mkdir download
mkdir download/in

echo 
echo "Create virtual environment for heroscript"
python3 -m venv venv     

echo 
echo "Start venv to install the packages (see https://github.com/termux/termux-app/issues/8)"
source venv/bin/activate 

echo 
echo "Needed for lxml, s. https://github.com/termux/termux-app/issues/8"
pip install wheel
pkg install libxml2 libxslt 

echo 
echo "Install packages in venv"
pip install -r requirements.txt 
deactivate 

echo 
echo "Doesn't work in venv mode (?)"
venv/bin/pip install flask
