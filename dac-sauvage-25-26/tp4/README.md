# TP4 Automatisation avec Ansible 

Ce dépôt est le dépôt du TP4 de DAC de Lucas Sauvage pour l'année 2025-2026 

## Partie 1 -- Prise en main 

L'inventaire est la première configuration nécessaire au bon développement de l'automatisation. Il permet de renseigner les adresses des machines concernées par l'automatisation. Ce fichier est disponible [**ici**](./inventory/hosts.yml)

Ici on configure le port destiné a ansible sur le port 22 et on renseigne les users/@IP des machines concernées. 

Ensuite, on peut définir notre premier playbook, destiné à la configuration du parefeu. J'utiliserai UFW dans la suite du projet. 

Le playbook est disponible [**ici**](./playbooks/ufw_playbook.yml) et agit de la sorte : 
    - Mets à jour les dépôts distants. 
    - Télécharger UFW // Le mettre à jour s'il existe déjà 
    - Refuser toutes les connections 
    - Activer OpenSSH 
    - Autoriser une connection tcp via le port 22 pour SSH

On lance ensuite le PlayBook avec la commande suivante : 
`ansible-playbook -i inventory playbooks/config_ufw.yml`. 

On ne précise pas l'inventaire car il est définit dans le [**fichier config**](./ansible.cfg). 

```bash 
ubuntu@tp4-bdd:~$ sudo ufw status verbose
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp (OpenSSH)           ALLOW IN    Anywhere                  
22/tcp                     ALLOW IN    Anywhere                  
3306/tcp                   ALLOW IN    Anywhere                  
22/tcp (OpenSSH (v6))      ALLOW IN    Anywhere (v6)             
22/tcp (v6)                ALLOW IN    Anywhere (v6)             
3306/tcp (v6)              ALLOW IN    Anywhere (v6)  
```

On voit que par defaut, toutes les connexions entrantes sont `deny`. Ensuite, seulement les ports nécessaires au fonctionnement du TP sont autorisés. Une meilleure sécurité serait de n'accepter les connexions uniquement grâce aux @IP des clients. 

Ensuite on créé la base de données, l'utilisateur pour autoriser la connexion du client, modifier le `bind-adress` et changer le paramètre qui n'autorisait que des connexions locales (i.e. de l'@IP `127.0.x.x`), pour accepter toutes les connexions (i.e. `0.0.0.0`).  

Pour ce faire, j'ai défini 2 rôles et un playbook (chaque rôle doit être appelé dans un playbook, mais je veux dire que pour le serveur / client j'ai utilisé des rôles, mais pas pour la configuration d'ufw). 

  - [**Config UFW**](./playbooks/config_ufw.yml) 
  - [**Dossier Config Server**](./roles/mysql_server/)
    - [**Fichier Tasks**](./roles/mysql_server/tasks/main.yml)
  - [**Dossier Config Client**](./roles/mysql_client/)
    - [**Fichier Tasks**](./roles/mysql_client/tasks/main.yml)

On peut ensuite vérifier que l'insertion (automatisée avec config_server) a bien été réalisée. 

Connexion au client : 
```shell 
lucas@gerard:~/Desktop/m1/dac-sauvage/tp4$ ssh ubuntu@172.28.101.8
Welcome to Ubuntu 24.04.3 LTS (GNU/Linux 6.8.0-71-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/pro

 System information as of ven. 14 nov. 2025 10:34:51 CET

  System load:  0.12              Processes:             98
  Usage of /:   32.8% of 8.65GB   Users logged in:       0
  Memory usage: 55%               IPv4 address for ens3: 172.28.101.8
  Swap usage:   0%


Expanded Security Maintenance for Applications is not enabled.

0 updates can be applied immediately.

Enable ESM Apps to receive additional future security updates.
See https://ubuntu.com/esm or run: sudo pro status


*** System restart required ***
ubuntu@tp4-client:~$ mysql -uansible_user -h 172.28.100.144 
Welcome to the MySQL monitor.  Commands end with ; or \g.
[...]
```

Vérification de l'insertion : 

```sql
mysql> SHOW DATABASES; 
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| testdB             |
+--------------------+
5 rows in set (0.04 sec)

mysql> USE testdB; 
Database changed
mysql> SELECT * from testTable; 
+----+------+
| id | name |
+----+------+
|  1 | Amin |
|  2 | Amin |
+----+------+
2 rows in set (0.01 sec)
```

(Comme j'ai fait plusieurs essais avant d'arriver à une BDD fonctionnelle, il y a eu 2 insertions de la même donnée, c'est pourquoi il y a 2 "Amin").


## Partie 2 -- Automatisation d’infrastructure

Pour cette partie, je choisis de reprendre l'infrastructure qui privilégit la cohérence. 

Pour ce faire, on doit modifier la configuration ci-dessus afin de : 
  - Activer la réplication entre les 2 BDDs 
  - Configurer une relation Primaire-Primaire 
  - Créer le proxy 
  - Forcer les connexions à passer par le proxy 
  - Implémenter la cohérence (grâce au proxy, si une BDD tombe, l'autre prend le relais)

Pour ce faire, nous allons définir un playbook qui structurera la relation Primaire-Primaire.
Voici les différents rôles utilisés dans ce playbook : 

   - update 
   - mysql_configure_first
   - mysql_configure_second 
   - ufw_configure 
   - prepare_replica_1
   - replica_2 
   - replica_1

`update` s'occupe des MAJs sur les VMs, `mysql_configure_first` de la première BDD, `mysql_configure_second` de la seconde (on doit avoir 2 rôles car une BDD utilise `server-id` et  `auto_increment_offset` intialisés à 1 pendant que l'autre doit recevoir 2.
`ufw_configure` s'occupe de sécuriser grâce à un pare-feu qui n'autorise les connexions uniquement du port 3306 pour mysql et le port 22 pour SSH.
`prepare_replica_1` prépare les fichiers (dump, master_infos) nécessaire à la réplication de l'instance 2 dans l'instance 1. 
`replica_2` s'occupe de la dite réplication et `replica_1`configure l'exact inverse.

Pour confirmer, vous trouverez les logs de l'éxecution du playbook [*configure_replica.yml*](./playbooks/configure_replica.yml) en bas de ce README. 

Ensuite il faut définir le playbook pour la configuration d'HAProxy, qui permettra d'assurer la cohérence de l'architecture en redistribuant la connexion si jamais une BDD venait à tomber. 
Pour ce faire il faut : 

    - Installer HAProxy, via APT 
    - Configurer le fichier /etc/haproxy/haproxy.cfg 
        - section global : laissée par défaut
        - section defaults : mode TCP, Port par défaut du serveur (3306), limites d'essais / de temps quant aux connexions ... 
        - section listen pour écouter sur l'adresse 0000, mode TCP, adresses des Priamires 
        - La cohérence sera explicitement configurée plus bas 
    - Modifier le fichier /etc/rsyslog.cfg 
        - Décommenter le module UDP utilisé pour le proxy 
        - Décommenter la ligne de l'input UDP (toujours pour le proxy)  
        - Ajouter le fichier des logs d'HAProxy
    - Créer un utilisateur dans la base de donnée pour le proxy (je l'ai rajouté dans le fichier [prepare_replica_1](./roles/prepare_replica_1/tasks/main.yml), juste après la création d'un utilisateur pour la réplication.)

Le rôle qui configure basiquement le proxy est [**le suivant**](./roles/configure_proxy/tasks/main.yml) 

Le proxy est maintenant configuré pour redistribuer les connexions si jamais l'un des deux serveurs primaires tombe. 
Les logs sont disponible en bas du fichier. 
On voit bien que de base la connexion passe par *tp4-client*. 
Ensuite on arrête la connexion avec [**ce rôle**](./roles/stop_mysql_2/). 
On voit ensuite, en relançant le playbook du debug du proxy, que la connexion passe maintenant par le serveur *tp4-bdd*.

Maintenant que la réplication Primaire-Primaire ainsi que le proxy ont été implementés, il reste maintenant à s'occuper de la cohérence des données. 
Premièrement, il faut que le proxy ping constamment la BDD afin de savoir si elle est down. 
Comme j'utilise une méthode qui efface et colle tout le texte, je vais modifier directement le rôle qui configure le proxy. 
Il faut rajouter cette ligne : 
`option mysql-check user haproxy` qui ping les BDD avec l'user haproxy afin de détecter une erreur. 

Ensuite, il faut modifier le pare-feu afin de n'autoriser que les connexions qui viennent de l'IP du proxy. 
Il faut également autoriser les IP des BDD afin de garantir la réplication.
Je ne vais pas recréer de rôle pour paramétrer ceci, je vais plutôt directement modifier le role *ufw_config*.
 
La cohérence est maintenant implantée ! 
Si jamais le serveur 1 tombe, le deuxième prend le relai, et vice-versa. 

De plus, les connexions ne peuvent passer que par le pare feu. 

L'éxecution de [**ce playbook**](./playbooks/debug_proxy.yml) permet de tester la connexion au proxy. 
Les logs de ce playbook sont également en bas de ce README. 

Cependant, on peut voir que la connection n'a pas été acceptée et retourne 'Timeout', ce qui est le comportement attendu d'UFW. 

### Logs de l'éxecution de *configure_replica* 
```bash
[annick@Iusearchbtw tp4]$ ansible-playbook -i inventory playbooks/configure_replica.yml 

PLAY [Update all hosts] **********************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [update : Update apt cache] *************************************************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [update : Install Python MySQL library] *************************************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [update : Install MySQL server] *********************************************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [update : Ensure MySQL is started] ******************************************************************************************************************
ok: [instance1]
ok: [instance2]

PLAY [Configure MySQL for Instance 1] ********************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance1]

TASK [mysql_configure_first : Configure MySQL bind-address to allow remote connections] ******************************************************************
ok: [instance1]

TASK [mysql_configure_first : Set server-id for replication] *********************************************************************************************
ok: [instance1]

TASK [mysql_configure_first : Enable binary logging] *****************************************************************************************************
ok: [instance1]

TASK [mysql_configure_first : Active-Active Collision Prevention] ****************************************************************************************
ok: [instance1]

TASK [mysql_configure_first : Active-Active Collision Prevention] ****************************************************************************************
ok: [instance1]

TASK [mysql_configure_first : Set GTID mode ON] **********************************************************************************************************
changed: [instance1]

RUNNING HANDLER [mysql_configure_first : Restart MySQL] **************************************************************************************************
changed: [instance1]

PLAY [Configure MySQL for Instance 2] ********************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance2]

TASK [mysql_configure_second : Configure MySQL bind-address to allow remote connections] *****************************************************************
ok: [instance2]

TASK [mysql_configure_second : Set server-id for replication] ********************************************************************************************
ok: [instance2]

TASK [mysql_configure_second : Enable binary logging] ****************************************************************************************************
ok: [instance2]

TASK [mysql_configure_second : Active-Active Collision Prevention] ***************************************************************************************
ok: [instance2]

TASK [mysql_configure_second : Active-Active Collision Prevention] ***************************************************************************************
ok: [instance2]

TASK [mysql_configure_second : Set GTID mode ON] *********************************************************************************************************
changed: [instance2]

RUNNING HANDLER [mysql_configure_second : Restart MySQL] *************************************************************************************************
changed: [instance2]

PLAY [Configure UFW] *************************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [ufw_configure : APT Update] ************************************************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [ufw_configure : Install UFW] ***********************************************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Reset UFW] *************************************************************************************************************************
changed: [instance2]
changed: [instance1]

TASK [ufw_configure : Set default incoming policy to deny] ***********************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Set default outgoing policy to allow] **********************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Enable UFW for SSH] ****************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Allow SSH on Port 22] **************************************************************************************************************
changed: [instance2]
changed: [instance1]

TASK [ufw_configure : Open MySQL port] *******************************************************************************************************************
changed: [instance2]
changed: [instance1]

TASK [ufw_configure : Enable UFW] ************************************************************************************************************************
changed: [instance1]
changed: [instance2]

PLAY [Prepare Replica on Instance 1] *********************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance1]

TASK [prepare_replica_1 : Remove old dump file to force re-creation] *************************************************************************************
changed: [instance1]

TASK [prepare_replica_1 : Create databse] ****************************************************************************************************************
[WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
[DEPRECATION WARNING]: Importing 'to_native' from 'ansible.module_utils._text' is deprecated. This feature will be removed from ansible-core version 2.24. Use ansible.module_utils.common.text.converters instead.
ok: [instance1]

TASK [prepare_replica_1 : Create a limited user for instance 2] ******************************************************************************************
ok: [instance1]

TASK [prepare_replica_1 : Create replication for user i2 on db1] *****************************************************************************************
ok: [instance1]

TASK [prepare_replica_1 : Lock tables for replication snapshot] ******************************************************************************************
ok: [instance1]

TASK [prepare_replica_1 : Show Primary Status] ***********************************************************************************************************
ok: [instance1]

TASK [prepare_replica_1 : Dump database for replication] *************************************************************************************************
changed: [instance1]

TASK [prepare_replica_1 : Fetch dump from Primary (m2) to Ansible Controller] ****************************************************************************
changed: [instance1]

TASK [prepare_replica_1 : Unlock tables after replication snapshot] **************************************************************************************
ok: [instance1]

PLAY [Configure Replica from Instance 1 to Instance 2] ***************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance2]

TASK [replica_2 : Copy dump from Ansible Controller to Instance 1] ***************************************************************************************
changed: [instance2]

TASK [replica_2 : Create database] ***********************************************************************************************************************
ok: [instance2]

TASK [replica_2 : import database dump from Instance 1] **************************************************************************************************
changed: [instance2]

TASK [replica_2 : Stop REPLICA before configuring] *******************************************************************************************************
ok: [instance2]

TASK [replica_2 : Configure replication source (Change Master)] ******************************************************************************************
ok: [instance2]

TASK [replica_2 : Start Replica] *************************************************************************************************************************
ok: [instance2]

TASK [replica_2 : create a replica user for the primary] *************************************************************************************************
ok: [instance2]

TASK [replica_2 : lock tables for replication snapshot] **************************************************************************************************
ok: [instance2]

TASK [replica_2 : get master status] *********************************************************************************************************************
ok: [instance2]

TASK [replica_2 : Fetch [SQL Running & IO Running]] ******************************************************************************************************
ok: [instance2]

TASK [replica_2 : Set facts for replica status] **********************************************************************************************************
ok: [instance2]

TASK [replica_2 : Debug IO Running] **********************************************************************************************************************
ok: [instance2] => {
    "replica_io_running": "Yes"
}

TASK [replica_2 : Debug SQL Running] *********************************************************************************************************************
ok: [instance2] => {
    "replica_sql_running": "Yes"
}

TASK [replica_2 : unlock tables after replication snapshot] **********************************************************************************************
ok: [instance2]

PLAY [Configure Replica from Instance 2 to Instance 1] ***************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance1]

TASK [replica_1 : Stop REPLICA before configuring] *******************************************************************************************************
ok: [instance1]

TASK [replica_1 : Configure replication source (Change Master)] ******************************************************************************************
ok: [instance1]

TASK [replica_1 : Start Replica] *************************************************************************************************************************
ok: [instance1]

TASK [replica_1 : Fetch [SQL Running & IO Running]] ******************************************************************************************************
ok: [instance1]

TASK [replica_1 : Set facts for replica status] **********************************************************************************************************
ok: [instance1]

TASK [replica_1 : Debug IO Running] **********************************************************************************************************************
ok: [instance1] => {
    "replica_io_running": "Yes"
}

TASK [replica_1 : Debug SQL Running] *********************************************************************************************************************
ok: [instance1] => {
    "replica_sql_running": "Yes"
}

PLAY RECAP ***********************************************************************************************************************************************
instance1                  : ok=18   changed=3    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
instance2                  : ok=15   changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

### Logs de l'éxecution de *debug_proxy*
```bash
[annick@Iusearchbtw tp4]$ ansible-playbook -i inventory playbooks/debug_proxy.yml 

PLAY [Test HAProxy Port and dB Host] *********************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instanceP]

TASK [debug_proxy : Check HAProxy Port [6033 to not conflict with 3033]] *********************************************************************************
ok: [instanceP]

TASK [debug_proxy : Debug HAProxy Port Test [Lookup for "failed", "port" and "state"]] *******************************************************************
ok: [instanceP] => {
    "port_check": {
        "changed": false,
        "elapsed": 0,
        "failed": false,
        "match_groupdict": {},
        "match_groups": [],
        "path": null,
        "port": 6033,
        "search_regex": null,
        "state": "started"
    }
}

TASK [debug_proxy : Test Hostname [which VM's used to run server]] ***************************************************************************************
[WARNING]: Deprecation warnings can be disabled by setting `deprecation_warnings=False` in ansible.cfg.
[DEPRECATION WARNING]: Importing 'to_native' from 'ansible.module_utils._text' is deprecated. This feature will be removed from ansible-core version 2.24. Use ansible.module_utils.common.text.converters instead.
ok: [instanceP]

TASK [debug_proxy : Debug @@hostname] ********************************************************************************************************************
ok: [instanceP] => {
    "hostname.query_result": [
        [
            {
                "@@hostname": "tp4-client"
            }
        ]
    ]
}

PLAY [Stop MySQL on BDD 2] *******************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance2]

TASK [Stop Mysql] ****************************************************************************************************************************************
changed: [instance2]

PLAY [Check if hostname has changed] *********************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instanceP]

TASK [debug_proxy : Check HAProxy Port [6033 to not conflict with 3033]] *********************************************************************************
ok: [instanceP]

TASK [debug_proxy : Debug HAProxy Port Test [Lookup for "failed", "port" and "state"]] *******************************************************************
ok: [instanceP] => {
    "port_check": {
        "changed": false,
        "elapsed": 0,
        "failed": false,
        "match_groupdict": {},
        "match_groups": [],
        "path": null,
        "port": 6033,
        "search_regex": null,
        "state": "started"
    }
}

TASK [debug_proxy : Test Hostname [which VM's used to run server]] ***************************************************************************************
ok: [instanceP]

TASK [debug_proxy : Debug @@hostname] ********************************************************************************************************************
ok: [instanceP] => {
    "hostname.query_result": [
        [
            {
                "@@hostname": "tp4-bdd"
            }
        ]
    ]
}

PLAY [Start MySQL on BDD 2] ******************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance2]

TASK [Start MySQL] ***************************************************************************************************************************************
changed: [instance2]

PLAY [Change UFW rules] **********************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : APT Update] ************************************************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Install UFW] ***********************************************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Reset UFW] *************************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Set default incoming policy to deny] ***********************************************************************************************
ok: [instance1]
ok: [instance2]

TASK [ufw_configure : Set default outgoing policy to allow] **********************************************************************************************
ok: [instance2]
ok: [instance1]

TASK [ufw_configure : Enable UFW for SSH] ****************************************************************************************************************
changed: [instance2]
changed: [instance1]

TASK [ufw_configure : Allow SSH on Port 22] **************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Open MySQL port] *******************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Authorize tp4-bdd] *****************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Authorize tp4-client] **************************************************************************************************************
changed: [instance1]
changed: [instance2]

TASK [ufw_configure : Enable UFW] ************************************************************************************************************************
changed: [instance1]
changed: [instance2]

PLAY [Test Forbidden Request] ****************************************************************************************************************************

TASK [Gathering Facts] ***********************************************************************************************************************************
ok: [localhost]

TASK [Test Forbidden reqest from tp4-bdd] ****************************************************************************************************************
[ERROR]: Task failed: Module failed: Timeout when waiting for 172.28.100.122:3306
Origin: /home/annick/dac-sauvage/tp4/playbooks/debug_proxy.yml:44:7

42   become: true
43   tasks :
44     - name: Test Forbidden reqest from tp4-bdd 
         ^ column 7

fatal: [localhost]: FAILED! => {"changed": false, "elapsed": 4, "msg": "Timeout when waiting for 172.28.100.122:3306"}
...ignoring

TASK [Firewall not workin] *******************************************************************************************************************************
skipping: [localhost]

TASK [Firewall working] **********************************************************************************************************************************
ok: [localhost] => {
    "msg": "SUCCES: Le port 3306 est bien fermé."
}

PLAY RECAP ***********************************************************************************************************************************************
instance1                  : ok=12   changed=7    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
instance2                  : ok=16   changed=9    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
instanceP                  : ok=10   changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
localhost                  : ok=3    changed=0    unreachable=0    failed=0    skipped=1    rescued=0    ignored=1   
```
