#!/bin/bash
VM_IP="172.28.101.129"
VM_USR="ubuntu"
SSH_KEY="$HOME/.ssh/cloud.key" 

SSH_OPTS="-i $SSH_KEY -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null"

FILE_SQL="netflixdb-postgres.sql"

if [ ! -f "$FILE_SQL" ]; then
    echo "❌ ERREUR : Fichier $FILE_SQL introuvable !"
    exit 1
fi

echo "> [1/2] Sending files ..."
scp $SSH_OPTS Q3.yaml Q3-secret.yaml $FILE_SQL Q3_on_vm.sh $VM_USR@$VM_IP:~/

echo "> [2/2] Executing file ..."
ssh $SSH_OPTS $VM_USR@$VM_IP "chmod +x Q3_on_vm.sh && ./Q3_on_vm.sh"
