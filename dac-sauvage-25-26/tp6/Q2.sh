#!/bin/bash 
VM_IP="172.28.101.129"
VM_USR="ubuntu"

SSH_KEY="$HOME/.ssh/cloud.key"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

KUBECTL="minikube kubectl --" 
POD="q2.yaml" 

echo "> [1/2] Sending Pod files to VM with IP : $VM_IP ..." 
scp $SSH_OPTS $POD q2_on_vm.sh $VM_USR@$VM_IP:~/ 

if [ $? -ne 0 ]; then
  echo "Copy error."
  exit 1
fi

echo "> [2/2] Executing Pod script ..."
ssh $SSH_OPTS $VM_USR@$VM_IP "chmod +x Q2_on_vm.sh && ./Q2_on_vm.sh"
