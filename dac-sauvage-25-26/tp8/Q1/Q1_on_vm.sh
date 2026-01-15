#!/bin/bash

KUBE=kubectl 

PERSISTENT_VOLUME="./persistent_volume.yaml"
CONFIG_MAP="./configmap.yaml" 
SERVICES="./services.yaml" 
STATEFUL_SET="./statefulset.yaml"

echo "> Clean-up StatefulSet..." 
$KUBE delete statefulset postgres --ignore-not-found=true
echo "> Clean-up Services & Config..."
$KUBE delete svc postgres postgres-rw postgres-ro --ignore-not-found=true
$KUBE delete configmap postgres-config --ignore-not-found=true
echo "> Clean up PVC..."
$KUBE delete pvc data-postgres-0 data-postgres-1 data-postgres-2 --ignore-not-found=true --wait=false
echo "> Clean-up PV (Persistent volumes)..."
$KUBE delete pv pv-volume-0 pv-volume-1 pv-volume-2 --ignore-not-found=true --wait=false
echo "> Sleeping for 10s.."
sleep 10

echo "> Deleting data on virtual drives..."
sudo rm -rf /mnt/data/pv0/*
sudo rm -rf /mnt/data/pv1/*
sudo rm -rf /mnt/data/pv2/*

echo "> [0/4] Applying Persistent Volume..."
$KUBE apply -f $PERSISTENT_VOLUME

echo "> [1/4] Applying ConfigMap..." 
$KUBE apply -f $CONFIG_MAP 

echo "> [2/4] Creation of services..."
$KUBE apply -f $SERVICES

echo "> [3/4] Deployment of StatefulSet Cluster..." 
kubectl apply -f $STATEFUL_SET

echo "> Sleeping for 45 secs" 
sleep 45 



echo ""
echo "Initial results (before deleting pod) :"
echo "---------------------------------------------------"
$KUBE get pods -o wide 
echo "---------------------------------------------------"

echo "> Testing resiliency, deleting pod..."
$KUBE delete pod postgres-1 

echo "> Lookup for Pod recreating itself..."
echo "---------------------------------------------------"
$KUBE get pods -w  
echo "---------------------------------------------------"

