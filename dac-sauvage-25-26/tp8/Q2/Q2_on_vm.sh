#!/bin/bash
KUBE="kubectl"


echo "> CLeaning..."
$KUBE delete statefulset postgres --ignore-not-found=true
$KUBE delete svc postgres postgres-rw postgres-ro --ignore-not-found=true
$KUBE delete configmap postgres-config --ignore-not-found=true
$KUBE delete pvc data-postgres-0 data-postgres-1 data-postgres-2 --ignore-not-found=true --wait=false
$KUBE delete pv pv-volume-0 pv-volume-1 pv-volume-2 --ignore-not-found=true --wait=false
echo "> Deleting files on virtual drive.."
sudo rm -rf /mnt/data/pv0/* /mnt/data/pv1/* /mnt/data/pv2/*

sleep 5

echo "> Deploymnent"
$KUBE apply -f persistent_volume.yaml
$KUBE apply -f configmap.yaml
$KUBE apply -f services.yaml
$KUBE apply -f statefulset.yaml

echo "> Sleeping 45 secs..."
sleep 45
$KUBE get pods -o wide


$KUBE delete pod postgres-0 --force --grace-period=0
$KUBE delete pvc data-postgres-0 --wait=false

echo "> Resetting the Persistent Volume..."
$KUBE delete pv pv-volume-0 --ignore-not-found=true --wait=false


echo "> Sleeping 5 secs..."
sleep 5
$KUBE apply -f persistent_volume.yaml

echo "> Wiping physical data..."
sudo rm -rf /mnt/data/pv0/*

echo "> Pod 0 should start again..."
$KUBE get pods -w
