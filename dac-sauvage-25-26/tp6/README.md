# TP 6 -- Minikube 
Ceci est le dépôt pour le TP7 de Lucas Sauvage pour le cours de DAC 2025-2026. 

## Réponses aux questions

### Q1 

La première partie consiste à installer `minkube` sur une VM. 
Pour ce faire, je vais créer un rôle Ansible, disponible [**ici**](./ansible/roles/install_minikube/). 
Il configure et installe `minikube`. 
La vérification de l'installation consiste à démarrer `minkibube`. 
Le rôle correspondant est [**ici**](./ansible/roles/verif_minikube/).

Ensuite, il faut installer Docker, qui servira à fournir les counteneurs orchestrés par Minikube.
On peut ensuite vérifier que `minikube` est bien installé en démarrant le service. 

Finalement, il ne reste plus qu'à créer le playbook pour cette installation : [**Q1_install_minikube.yml**](./ansible/playbooks/Q1_install_minikube.yml). 
Le log de son éxecution (disponible tout en bas du README) permet de confirmer l'installation de `minikube` et `docker`. 
Afin de respecter le format de rendu, le fichier [*Q1.sh*](./Q1.sh) permet l'automatisation de ce qui se trouve au dessus, et se situe à la racine.


### Q2

Pour cette partie, le but est d'automatiser la création et le déploiement d'un pod dans une VM. 
Ce pod est disponible [**ici**](./Q2.yaml). 
Les 2 informations intéressantes de ce Pod sont : 
    
    - Son image : PostgreSQL-Alpine-15, une image légère 
    - Le mot de passe, en clair pour le moment. 
    - Un processus (Readiness Probe) qui permet de notifier au script principal que le Pod est prêt. 

Ensuite, il s'agit de transférer le fichier de configuration (*Q2.yaml*), ainsi que le script d'automatisation de l'installation du Pod. 
Ce script est le suivant : 
    
    - Autoriser l'utilisateur à utiliser Docker. 
    - S'assurer que minikube est bien démarré. 
    - Applique la configuration du Pod sur le cluster.
    - Attend que le Pod soit disponible.
    - Valide le fonctionnement avec une commande basique. 

### Q3 

Un deployeur permet de s'assurer que les Pods restent disponibles, même en cas de suppression. 
Pour créer le déployeur demandé, il faut suivre ces étapes :

    - Créer le fichier Q3-secret.yaml afin d'encoder le mot de passe. 
    - Créer le fichier contenant le deployeur 

Pour le fichier [**Q3-secret**](./Q3-secret.yaml), il est nécessaire d'encoder le mot de passe en base64. 
La commande suivante permet d'avoir ce mot de passe: 

```bash
[annick@Iusearchbtw tp6]$ echo -n "postgres_pw" | base64
cG9zdGdyZXNfcHc=
```

Ensuite, il faut configurer le Déployeur, disponible [**ici**](./Q3.yaml).
Au départ, je voulais copier les informations de la base de données en utilisant une ConfigMap, ce qui m'aurait permis une meilleure disponibilité. 
En effet, si demain je venais à devoir déployer cette architecture en condition réelles, il faudrait que le fichier `netflixdb-postgres.sql` soit présent sur tous les serveurs d'où est éxecuté le script .sh (i.e. `Q3.sh` ici). 
Une ConfigMap aurait permis de stocker ces informations directement dans la base de données Kubernetes et aurait permis d'être disponible sur chaque serveur de cluster. 
Comme le fichier `netflixdb-postgres.sql` fait 7.9Mb, il est trop lourd pour ConfigMap qui n'accepte que des fichiers de taille inférieure à 1Mb. 

Le fichier est alors copié via `minkube cp`, dont `hostPath` pointe dessus. 
L'injection se fait alors via un volume de type `hostPath` afin que PostgreSQL puisse lire le fichier au démarrage. 
J'ai également augmenté les temps de timeout, comme cette question traite de fichiers plus lourds que la question 2. 
Le déploiement se fait ensuite comme pour la Q2. 

Une requête via le pod lancé sur la BDD permet d'en extraire les tables présentes et de confirmer le déploiement de cette BDD.  
Les logs sont disponibles tout en bas de ce README. 

### Q4 

Cette question nous demande de rendre accessible la base de données précedemment installée à l'extérieur du cluster.
Pour ce faire je vais utiliser un service de type NodePort, défini dans [**ce fichier**](./Q4.yaml). 
Ensuite, comme pour les questions précédentes, il faut 2 scripts : 1 pour envoyer le second, et le 2e qui exécute les commandes nécessaires à l'installation du service. 
Le script d'envoi est [**le suivant**](./Q4.sh). 
Celui qui s'exécute sur la VM est présent [**ici**](./Q4_on_vm.sh).
Pour se convaincre du fonctionnement du service, le log d'une requête via le port défini (i.e. port 32345) est disponible en bas ce README.

Cependant, une question quant à la sécurité se pose après l'exécution de ces scripts. 
En effet, dans le script pour tester la connexion via le port, le mot de passe est renseigné en clair dans le fichier .sh. 
Ce script étant envoyé dans la VM, n'importe qui peut, à posteriori, récuperer ce fichier et le mot de passe indiqué dedans. 
Pour ce TP ce n'est pas bien grave, rien n'est à récuperer mais pour un déploiement en production il faudrait maintenant se poser la question de la sécurité de l'architecture.
On pourrait également remarquer qu'un encodage en base64 n'est pas très sécuritaire non plus (rapport à la Q3). 

Ce TP est cependant terminé, même si l'architecture ce ferait hackée en moins de 5 minutes. 

## Logs 

### Q1 

<details>
<summary>Cliquez ici pour voir les logs de la Q1</summary>

```bash
[annick@Iusearchbtw ansible]$ ansible-playbook -i inventory playbooks/Q1_install_minikube.yml 

PLAY [Install Minikube & Docker on VM1] ******************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [vm1]

TASK [install_docker : Update APT] ***********************************************************************************************************************
changed: [vm1]

TASK [install_docker : Install Docker] *******************************************************************************************************************
changed: [vm1]

TASK [install_docker : Start Docker] *********************************************************************************************************************
ok: [vm1]

TASK [install_docker : Add current user] *****************************************************************************************************************
changed: [vm1]

TASK [install_docker : Re-initialize SSH] ****************************************************************************************************************

TASK [install_minikube : Create download directory] ******************************************************************************************************
changed: [vm1]

TASK [install_minikube : Download sha256sum] *************************************************************************************************************
changed: [vm1]

TASK [install_minikube : Read sha256sum] *****************************************************************************************************************
ok: [vm1]

TASK [install_minikube : Download Minikube] **************************************************************************************************************
changed: [vm1]

TASK [install_minikube : Create the Minikube installation dir] *******************************************************************************************
ok: [vm1]

TASK [install_minikube : Install Minikube] ***************************************************************************************************************
changed: [vm1]

TASK [Restart VM to apply permission for docker group] ***************************************************************************************************
changed: [vm1]

PLAY [Verif Minikube (can't be root so new task)] ********************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [vm1]

TASK [verif_minikube : Nettoyer une éventuelle installation corrompue] ***********************************************************************************
changed: [vm1]

TASK [verif_minikube : Forcer les droits sur le socket Docker (Juste avant le start)] ********************************************************************
changed: [vm1]

TASK [verif_minikube : Start Minikube] *******************************************************************************************************************
changed: [vm1]

TASK [verif_minikube : Ensure Minikube is started] *******************************************************************************************************
ok: [vm1] => {
    "start_minikube": {
        "changed": true,
        "cmd": [
            "minikube",
            "start",
            "--driver=docker"
        ],
        "delta": "0:04:36.058020",
        "end": "2025-12-09 12:21:16.335166",
        "failed": false,
        "msg": "",
        "rc": 0,
        "start": "2025-12-09 12:16:40.277146",
        "stderr": [Lots of useless and quite long logs]
        "stdout": [Lots of useless informations about minkube version]. 
        "stdout_lines": [
            "* minikube v1.30.1 sur Ubuntu 24.04 (kvm/amd64)",
            "* minikube 1.37.0 est disponible ! Téléchargez-le ici : https://github.com/kubernetes/minikube/releases/tag/v1.37.0",
            "* Pour désactiver cette notification, exécutez : 'minikube config set WantUpdateNotification false'",
            "",
            "* Utilisation du pilote docker basé sur la configuration de l'utilisateur",
            "* Utilisation du pilote Docker avec le privilège root",
            "* Démarrage du noeud de plan de contrôle minikube dans le cluster minikube",
            "* Extraction de l'image de base...",
            "* Téléchargement du préchargement de Kubernetes v1.26.3...",
            "* Création de docker container (CPUs=2, Memory=2200Mo) ...",
            "* Préparation de Kubernetes v1.26.3 sur Docker 23.0.2...",
            "  - Génération des certificats et des clés",
            "  - Démarrage du plan de contrôle ...",
            "  - Configuration des règles RBAC ...",
            "* Configuration de bridge CNI (Container Networking Interface)...",
            "  - Utilisation de l'image gcr.io/k8s-minikube/storage-provisioner:v5",
            "* Vérification des composants Kubernetes...",
            "* Modules activés: default-storageclass, storage-provisioner",
            "* kubectl introuvable. Si vous en avez besoin, essayez : 'minikube kubectl -- get pods -A'",
            "* Terminé ! kubectl est maintenant configuré pour utiliser \"minikube\" cluster et espace de noms \"default\" par défaut."
        ]
    }
}

PLAY RECAP ***********************************************************************************************************************************************
vm1                        : ok=17   changed=11   unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```
</details>

### Q2

<details>
<summary>Cliquez ici pour voir les logs de la Q2</summary>

```bash 
[annick@Iusearchbtw tp6]$ ./q2.sh 
> [1/2] Sending Pod files to VM with IP : 172.28.101.129 ...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
q2.yaml                                                                                                                 100%  718    87.6KB/s   00:00    
q2_on_vm.sh                                                                                                             100%  795   242.6KB/s   00:00    
> [2/2] Executing Pod script ...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
> [1/5] Fixing Docker permissions...
> [2/5] Checking Minikube status...
> [3/5] Apply on Pod ...
pod "postgres-pod" deleted
pod/postgres-pod created
> [4/5] Wainting for Pod to be ready ...
pod/postgres-pod condition met
> [5/5] Execute SQL command inside contener ...
                                         version                                          
------------------------------------------------------------------------------------------
 PostgreSQL 15.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
(1 row)

Succes !! Postgres-Pod works
```

</details>

### Q3 

<details>
<summary>Cliquez ici pour voir les logs de la Q3</summary>

```bash
[annick@Iusearchbtw tp6]$ ./Q3.sh 
> [1/2] Sending files ...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
Q3.yaml                                                                                                                 100% 1058    45.5KB/s   00:00    
Q3-secret.yaml                                                                                                          100%  110     1.4KB/s   00:00    
netflixdb-postgres.sql                                                                                                  100% 8064KB 667.5KB/s   00:12    
Q3_on_vm.sh                                                                                                             100% 1146    56.8KB/s   00:00    
> [2/2] Executing file ...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
> Setting permissions...
> Ensure Minkube is started...
> [1/6] Copying data file into Cluster...
> [2/6] Deleting old files...
pod "postgres-deployment-64c955d9c8-crw7p" deleted
deployment.apps "postgres-deployment" deleted
replicaset.apps "postgres-deployment-64c955d9c8" deleted
secret "postgres-secret" deleted
> [3/6] Creating secret...
secret/postgres-secret created
> [4/6] Creating deployment (via HostPath)...
deployment.apps/postgres-deployment created
> [5/6] Wating for Start & Population of DB...
deployment.apps/postgres-deployment condition met
> [6/6] Fetching database to ensure import ...
            List of relations
 Schema |     Name     | Type  |  Owner   
--------+--------------+-------+----------
 public | movie        | table | postgres
 public | season       | table | postgres
 public | tv_show      | table | postgres
 public | view_summary | table | postgres
(4 rows)

[annick@Iusearchbtw tp6]$ 
```

</details> 

### Q4 

<details>
<summary>Cliquez ici pour voir les logs de la Q4</summary>

```bash
[annick@Iusearchbtw tp6]$ ./Q4.sh
> [1/2] Sending files to VM...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
Q4.yaml                                                                                                                 100%  189     7.7KB/s   00:00    
Q4_on_vm.sh                                                                                                             100%  802    39.3KB/s   00:00    
> [2/2] Executing files on VM...
Warning: Permanently added '172.28.101.129' (ED25519) to the list of known hosts.
> [1/3] Creating service...
service/postgres-service unchanged
> [2/3] Wainting files to be copied...
> Connexion information : Host=192.168.49.2 Port=32345
> [3/3] Ensure PostGresql is installed...
***************************TEST***************************
> [] Trying to connect to cluster via VM...
                                         version                                          
------------------------------------------------------------------------------------------
 PostgreSQL 15.15 on x86_64-pc-linux-musl, compiled by gcc (Alpine 15.2.0) 15.2.0, 64-bit
(1 row)

--Success ! Port 32345 is open--
```

</details>
