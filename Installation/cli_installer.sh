#!/bin/bash

# sudo apt update
# sudo apt -y install python3-pip
# pip3 install -r requirements.txt

cp ../Cli/cli.py icc
sudo chmod +x icc
sudo cp icc /bin/
sudo rm icc

icc_infrastructure_dir=$(dirname $PWD)
sudo grep -q "^export ICC_INFRASTRUCTURE_PATH=" ~/.bashrc && sudo sed "s|^export ICC_INFRASTRUCTURE_PATH=.*|ICC_INFRASTRUCTURE_PATH=$icc_infrastructure_dir|" -i ~/.bashrc || sudo sed "$ a\export ICC_INFRASTRUCTURE_PATH=$icc_infrastructure_dir" -i ~/.bashrc
source ~/.bashrc