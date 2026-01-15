echo "> [1/5] Fixing Docker permissions..."
sudo chmod 666 /var/run/docker.sock

echo "> [2/5] Checking Minikube status..."
minikube status > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Minikube is stopped. Starting it now..."
    minikube start --driver=docker --force
fi


KUBECTL="minikube kubectl --" 
POD="q2.yaml" 


echo "> [3/5] Apply on Pod ..."
$KUBECTL delete pod postgres-pod --ignore-not-found=true # to delete old pod
$KUBECTL apply -f $POD  

echo "> [4/5] Wainting for Pod to be ready ..."
$KUBECTL wait --for=condition=Ready pod/postgres-pod --timeout=60s

echo "> [5/5] Execute SQL command inside contener ..."
$KUBECTL exec postgres-pod -- psql -U postgres -c "SELECT version();"

if [ $? -eq 0 ]; then 
	echo "Succes !! Postgres-Pod works" 
else 
	echo "Failure ..." 
fi 
