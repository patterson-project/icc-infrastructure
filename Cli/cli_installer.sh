#!/bin/bash

printf '%s\n' 'Installing dependencies...'
sudo apt-get update > /dev/null
sudo apt-get -y install python3-pip 
pip3 install -r requirements.txt 

cp ../Cli/cli.py icc
sudo chmod +x icc
sudo cp icc /bin/
sudo rm icc

icc_infrastructure_dir=$(dirname $PWD)
sudo grep -q "^export ICC_INFRASTRUCTURE_PATH=" ~/.bashrc && sudo sed "s|^export ICC_INFRASTRUCTURE_PATH=.*|ICC_INFRASTRUCTURE_PATH=$icc_infrastructure_dir|" -i ~/.bashrc || sudo sed "$ a\export ICC_INFRASTRUCTURE_PATH=$icc_infrastructure_dir" -i ~/.bashrc

printf '%s\n' 'Done! Run source ~/.bashrc or logout & login for these changes to take effect.'
printf '%s\n' 'Run "icc --help" for usage.'