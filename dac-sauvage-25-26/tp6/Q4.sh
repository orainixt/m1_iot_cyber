#!/bin/bash
VM_IP="172.28.101.129"
VM_USR="ubuntu"
KEY_PATH="$HOME/.ssh/cloud.key" 

SSH_OPTS="-i $KEY_PATH -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

echo "> [1/2] Sending files to VM..."
scp $SSH_OPTS Q4.yaml Q4_on_vm.sh $VM_USR@$VM_IP:~/

if [ $? -ne 0 ]; then
    echo "❌ Erreur de copie."
    exit 1
fi

echo "> [2/2] Executing files on VM..."
ssh $SSH_OPTS $VM_USR@$VM_IP "chmod +x Q4_on_vm.sh && ./Q4_on_vm.sh"
