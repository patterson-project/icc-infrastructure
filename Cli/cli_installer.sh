#!/bin/bash

printf '%s\n' 'Installing CLI dependencies...'
sudo apt-get update > /dev/null
sudo apt-get -y install python3-pip > /dev/null
pip3 install -r requirements.txt --quiet

cp ../Cli/cli.py icc
sudo chmod +x icc
sudo cp icc /bin/
sudo rm icc

icc_infrastructure_dir=$(dirname $PWD)
sed -i "/ICC_INFRASTRUCTURE_PATH/c\export ICC_INFRASTRUCTURE_PATH=$icc_infrastructure_dir" ~/.bashrc

printf '%s\n' 'Done! Run source ~/.bashrc or logout & login for these changes to take effect.'
printf '%s\n' 'Run "icc --help" for usage.'