#!/bin/bash

cd ..

# Colors
grn=$'\e[1;32m'
cyn=$'\e[1;36m'
end=$'\e[0m'

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

sudo apt-get update && sudo apt upgrade

# Installing Kubernetes
printf "\n%s\n" "${cyn}Installing k3s...${end}"
sleep 1
curl -sfL https://get.k3s.io | sudo sh -

echo "namespace 8.8.8.8" >> /etc/resolv.conf
echo "namespace 8.8.4.4" >> /etc/resolv.conf

# Deploying the MongoDb locally
printf "\n%s\n" "${cyn}Deploying local Mongo Database...${end}"
sleep 1
cd MongoDb
sudo docker compose up --build -d
cd ..

# Restarting for changes to take effect
printf "\n%s\n" "${grn}Done! Restarting for changes to take effect...${end}"
sleep 2
sudo reboot
