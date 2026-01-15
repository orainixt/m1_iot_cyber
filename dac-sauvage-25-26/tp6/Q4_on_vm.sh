#!/bin/bash
KUBECTL="minikube kubectl --"

echo "> [1/3] Creating service..."
$KUBECTL apply -f Q4.yaml

echo "> [2/3] Wainting files to be copied..."
sleep 5

MINIKUBE_IP=$(minikube ip)
NODE_PORT=32345

echo "> Connexion information : Host=$MINIKUBE_IP Port=$NODE_PORT"

echo "> [3/3] Ensure PostGresql is installed..."
if ! command -v psql &> /dev/null; then
    sudo apt-get update -qq
    sudo apt-get install -y postgresql-client
fi

echo "***************************TEST***************************"
echo "> [] Trying to connect to cluster via VM..."


PGPASSWORD='postgres_pw' psql -h $MINIKUBE_IP -p $NODE_PORT -U postgres -d postgres -c "SELECT version();"

if [ $? -eq 0 ]; then
    echo "--Success ! Port 32345 is open--"
else
    echo "--Failure : Port 32345 unreachable...--"
    exit 1
fi
