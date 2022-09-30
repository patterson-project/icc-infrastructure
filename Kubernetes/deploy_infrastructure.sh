#!/bin/bash

# Colors
cyn=$'\e[1;36m'
grn=$'\e[1;32m'
end=$'\e[0m'


printf "%s\n" "${cyn}Deleting all cluster resources...${end}"
sudo kubectl delete services,deployments,pods,ingress,secrets --all

printf "\n%s\n" "${cyn}Deploying all SECRETS...${end}"
envsubst < Secrets/secrets.yaml | sudo kubectl apply -f -

printf "\n%s\n" "${cyn}Deploying all DEPLOYMENTS...${end}"
for filename in Deployments/*.yaml; do
    envsubst < $filename | sudo kubectl apply -f -
done

printf "\n%s\n" "${cyn}Deploying all INGRESS routing...${end}"
for filename in Ingress/*.yaml; do
    envsubst < $filename | sudo kubectl apply -f -
done

printf "\n%s\n\n" "${grn}Done.${end}"
