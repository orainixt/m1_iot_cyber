#!/bin/bash
echo "> Setting permissions..."
sudo chmod 666 /var/run/docker.sock
chmod 644 /home/ubuntu/netflixdb-postgres.sql

echo "> Ensure Minkube is started..." 
minikube status > /dev/null 2>&1
if [ $? -ne 0 ]; then
    minikube start --driver=docker --force --cpus=1
fi

KUBECTL="minikube kubectl --"

echo "> [1/6] Copying data file into Cluster..."
minikube cp /home/ubuntu/netflixdb-postgres.sql /tmp/netflixdb-postgres.sql

echo "> [2/6] Deleting old files..."
$KUBECTL delete all -l app=postgres --ignore-not-found=true
$KUBECTL delete configmap postgres-init-data --ignore-not-found=true
$KUBECTL delete secret postgres-secret --ignore-not-found=true

echo "> [3/6] Creating secret..."
$KUBECTL apply -f Q3-secret.yaml

echo "> [4/6] Creating deployment (via HostPath)..."
$KUBECTL apply -f Q3.yaml

echo "> [5/6] Wating for Start & Population of DB..."
$KUBECTL wait --for=condition=available deployment/postgres-deployment --timeout=120s

echo "> [6/6] Fetching database to ensure import ..."
POD_NAME=$($KUBECTL get pods | grep postgres | awk '{print $1}' | head -n 1)
$KUBECTL exec $POD_NAME -- psql -U postgres -c "\dt"
