#!/bin/bash


if [ ! -f "verif.yaml" ]; then
    echo "❌ Erreur : Le fichier verif.yaml est introuvable sur la VM !"
    exit 1
fi

echo "> [1/3] Apply verif using K8s.."
kubectl apply -f verif.yaml

echo "> [2/3] Waiting pods to start..."
sleep 15

echo ""
echo "Résultats :"
echo "---------------------------------------------------"
kubectl get pods -o wide
echo "---------------------------------------------------"
