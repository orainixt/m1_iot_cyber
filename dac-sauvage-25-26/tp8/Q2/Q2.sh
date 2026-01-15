#!/bin/bash
# Fichier: deploy_Q2.sh

# Infos de connexion
VM_IP="172.28.101.46"
VM_USER="debian"
SSH_KEY="$HOME/.ssh/cloud.key"
SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"


FILES="./configmap.yaml ./services.yaml ./statefulset.yaml ./persistent_volume.yaml ./Q2_on_vm.sh"

echo "> [1/2] Sending files to $VM_IP..."
scp $SSH_OPTS $FILES $VM_USER@$VM_IP:

echo "> [2/2] Executing distant script..."
ssh $SSH_OPTS $VM_USER@$VM_IP "chmod +x Q2_on_vm.sh && ./Q2_on_vm.sh"
