# TP8 -- DAC -- Lucas SAUVAGE 

**Auteur** : Lucas SAUVAGE
**Matière** : DAC 

## Réponses aux questions 

### Q1 -- Configuration de base

L'architecture WAL (Write-Ahead Logging) Streaming Replication est constituée : 

    - D'un primaire qui accepte les requêtes et distribue les accès en lecture seule. 
    - De secondaires se connectant au primaire et pouvant exécuter des requêtes de lecture. 

L'interêt de cette architecture est de pouvoir "relancer" un secondaire, il n'a qu'à lire la base de donnée Primaire. 


#### Différence entre Deployment et StatefulSet 

L'API Deployment fournit des pods interchangeable. Dès qu'un Pod tombe, il est remplacé. 
Cependant les Pods n'ont pas d'identité propre. 
Pour avoir une architecture où l'on distribue des accès en lecture uniquement, il faut pouvoir identifier le Pod primaire. 
L'API StatefulSet permet cette indentification, et la réutilisation du pod même après son déploiement. 
De plus, pour configurer une relation Primaire-Secondaire, l'ordre compte, car il faut que le Primaire existe pour que les Secondaires puissent se synchroniser. 

Il faut donc définir : 

- Un [**fichier ConfigMap**](./Q1/configmap.yaml) (pour instancier les VMs et la réplication).
- Un [**fichier Persistent Volume**](./Q1/persistent_volume.yaml) (permet de monter les VMs dans les volumes définis). 
- Un [**fichier Services**](./Q1/services.yaml) (gère le réseau et permets aux pods de "discuter") 
- Un [**fichier StatefulSet**](./Q1/statefulset.yaml). (création de pods identifiables)


#### Problèmes rencontrés 

J'ai eu des problèmes vis-à-vis de l'image, car tous les étudiants téléchargaient depuis Docker, qui limite à 400 téléchargements. 
J'ai donc du passer par le miroir AWS (Amazon). 

De plus, le primaire (postgres-0) écoute par défaut sur le `localhost`. 
Il faut changer ça pour qu'il écoute sur tout le monde, lors de la création (dans le *config_map*). 

J'ai également eu beaucoup de problèmes vis-à-vis des configurations déjà chargées dans le cache. 
J'ai donc rajouter tout une partie nettoyage avant l'exécution des APIs.

Le script qui envoie le vrai script est disponible [**ici**](./Q1/Q1.sh).
Il ne sert qu'à rendre exécutable [**le second**](./Q1/Q1_on_vm.sh) et à l'exécuter sur la VM.


### Q2 

Pour cette question, il faut changer les scripts de la *ConfigMap*. 
Maintenant, si le dossier de postgres-0 est vide au lancement, il va essayer de récupérer ceux de postgres-1. 
S'il arrive à les récuperer, il faut modifier le fichier d'authentification afin que postgres-0 redevienne Primaire. 
En effet, postgres-1 étant un secondaire, si jamais on ne fait pas cette modification, postgres-0 se considère secondaire mais considère également qu'il est primaire, ce qui entraîne des erreurs.
De plus, il fallait supprimer les anciens volumes et services, sinon K8s ne veut pas redistribuer un volume "utilisé" pour un nouveau pod. 

Toutes ces commandes sont disponibles dans [**ce fichier**](./Q2/Q2_on_vm.sh). 
Le fichier qui envoie ce script est disponible [**ici**](./Q2/Q2.sh). 
Les logs sont disponibles juste en dessous : (J'ai supprimé les lignes qui concernaient les pods de l'ancien TP). 
On peut voir dans la dernière table que postgres-0 démarre, puis redémarre comme voulu. 


```bash 
^C[annick@Iusearchbtw Q2]$ ./Q2.sh 
> [1/2] Sending files to 172.28.101.46...
Warning: Permanently added '172.28.101.46' (ED25519) to the list of known hosts.
configmap.yaml                      100% 1742   138.0KB/s   00:00    
services.yaml                       100%  491   184.2KB/s   00:00    
statefulset.yaml                    100% 1364   389.8KB/s   00:00    
persistent_volume.yaml              100%  581   193.2KB/s   00:00    
Q2_on_vm.sh                         100% 1605   515.5KB/s   00:00    
> [2/2] Executing distant script...
Warning: Permanently added '172.28.101.46' (ED25519) to the list of known hosts.
> CLeaning...
statefulset.apps "postgres" deleted
service "postgres" deleted
service "postgres-rw" deleted
service "postgres-ro" deleted
configmap "postgres-config" deleted
persistentvolumeclaim "data-postgres-0" deleted
persistentvolumeclaim "data-postgres-1" deleted
persistentvolumeclaim "data-postgres-2" deleted
persistentvolume "pv-volume-0" deleted
persistentvolume "pv-volume-1" deleted
persistentvolume "pv-volume-2" deleted
> Deleting files on virtual drive..
> Deploymnent
persistentvolume/pv-volume-0 created
persistentvolume/pv-volume-1 created
persistentvolume/pv-volume-2 created
configmap/postgres-config created
service/postgres-rw created
service/postgres-ro created
service/postgres created
statefulset.apps/postgres created
> Sleeping 45 secs...
NAME                  READY   STATUS    RESTARTS   AGE   IP            NODE     NOMINATED NODE   READINESS GATES
postgres-0            1/1     Running   0          46s   10.244.2.35   node-1   <none>           <none>
postgres-1            1/1     Running   0          34s   10.244.1.23   node-0   <none>           <none>
postgres-2            1/1     Running   0          22s   10.244.2.36   node-1   <none>           <none>
Warning: Immediate deletion does not wait for confirmation that the running resource has been terminated. The resource may continue to run on the cluster indefinitely.
pod "postgres-0" force deleted
persistentvolumeclaim "data-postgres-0" deleted
> Resetting the Persistent Volume...
persistentvolume "pv-volume-0" deleted
⏳ Pause technique (5s) pour laisser Kubernetes finir le ménage...
persistentvolume/pv-volume-0 unchanged
Warning: Detected changes to resource pv-volume-0 which is currently being deleted.
persistentvolume/pv-volume-1 unchanged
persistentvolume/pv-volume-2 unchanged
> Wiping physical data...
> Pod 0 should start again...
NAME                  READY   STATUS    RESTARTS   AGE
postgres-0            0/1     Running   0          7s
postgres-1            1/1     Running   0          41s
postgres-2            1/1     Running   0          29s
postgres-0            1/1     Running   0          11s
```
