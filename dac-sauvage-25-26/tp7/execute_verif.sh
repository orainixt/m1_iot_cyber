#!/bin/bash 
VM_IP="172.28.101.46"
VM_USR="debian"

SSH_KEY="$HOME/.ssh/cloud.key"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

VERIF="verif.yaml" 
SCRIPT="execute_verif_on_vm.sh"

echo "> [1/2] Sending verif file to VM with IP : $VM_IP ..." 
scp $SSH_OPTS $VERIF $SCRIPT $VM_USR@$VM_IP:


if [ $? -ne 0 ]; then
  echo "Copy error."
  exit 1
fi

echo "> [2/2] Executing verif script ..."
ssh $SSH_OPTS $VM_USR@$VM_IP "chmod +x $SCRIPT && ./$SCRIPT"
