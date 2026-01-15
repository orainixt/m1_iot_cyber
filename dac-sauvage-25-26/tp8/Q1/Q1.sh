#!/bin/bash

VM_IP="172.28.101.46"
VM_USR="debian"

SSH_KEY="$HOME/.ssh/cloud.key"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null" 

PERSISTENT_VOLUME="./persistent_volume.yaml"
CONFIG_MAP="./configmap.yaml" 
SERVICES="./services.yaml" 
STATEFUL_SET="./statefulset.yaml"
SCRIPT="./Q1_on_vm.sh" 

echo "> [1/2] Sending verif file to VM with IP : $VM_IP ..." 
scp $SSH_OPTS $CONFIG_MAP $SERVICES $STATEFUL_SET $SCRIPT $PERSISTENT_VOLUME $VM_USR@$VM_IP:

echo "> [2/2] Executing script..." 
ssh $SSH_OPTS $VM_USR@$VM_IP "chmod +x $SCRIPT && ./$SCRIPT" 


