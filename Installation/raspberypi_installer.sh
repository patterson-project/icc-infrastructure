#!/bin/bash

cd ..

# Colors
grn=$'\e[1;32m'
cyn=$'\e[1;36m'
end=$'\e[0m'

sudo apt-get update && sudo apt-get upgrade -y

# Installing docker and docker compose
printf "%s\n" "${cyn}Installing docker and docker compose...${end}"
sleep 1
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg lsb-release
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Initializing environment variables
echo "MONGO_DB_USERNAME" >> ~/.bashrc
echo "MONGO_DB_IP" >> ~/.bashrc
echo "MONGO_DB_PASSWORD" >> ~/.bashrc

# Installing icc cli
printf "\n%s\n" "${cyn}Installing icc CLI...${end}"
sleep 1
cd Cli
bash cli_installer.sh
source ~/.bashrc
icc variables -a -f
cd ..

# Deploying the MongoDb locally
printf "\n%s\n" "${cyn}Deploying local Mongo Database...${end}"
sleep 1
source ~/.bashrc
icc database -c

# Installing Kubernetes
printf "\n%s\n" "${cyn}Installing k3s...${end}"
sleep 1
curl -sfL https://get.k3s.io | sudo sh -
sudo apt install -y linux-modules-extra-raspi
sudo sed -i '$s/$/ cgroup_memory=1 cgroup_enable=memory/' /boot/cmdline.txt 

echo "namespace 8.8.8.8" >> /etc/resolv.conf
echo "namespace 8.8.4.4" >> /etc/resolv.conf

# Restarting for changes to take effect
printf "\n%s\n" "${grn}Done! Restarting for changes to take effect...${end}"
sleep 2
sudo reboot
