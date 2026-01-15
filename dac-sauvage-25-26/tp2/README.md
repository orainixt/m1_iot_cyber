# TP 2 DAC

## Réponses aux questions 

### Q1

J'ai préalablement installé MySQL sur mes 2 machines distantes. 
J'ai ensuite paramétré une unique base de données. 

Voici les logs des mêmes commandes sur les 2 machines distantes qui se connectent bien à la même BDD 


```
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
4 rows in set (0.01 sec)

mysql> USE mysql;
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> SHOW TABLES
    -> ;
+------------------------------------------------------+
| Tables_in_mysql                                      |
+------------------------------------------------------+
| columns_priv                                         |
| component                                            |
| db                                                   |
| default_roles                                        |
| engine_cost                                          |
| func                                                 |
| general_log                                          |
| global_grants                                        |
| gtid_executed                                        |
| help_category                                        |
| help_keyword                                         |
| help_relation                                        |
| help_topic                                           |
| innodb_index_stats                                   |
| innodb_table_stats                                   |
| password_history                                     |
| plugin                                               |
| procs_priv                                           |
| proxies_priv                                         |
| replication_asynchronous_connection_failover         |
| replication_asynchronous_connection_failover_managed |
| replication_group_configuration_version              |
| replication_group_member_actions                     |
| role_edges                                           |
| server_cost                                          |
| servers                                              |
| slave_master_info                                    |
| slave_relay_log_info                                 |
| slave_worker_info                                    |
| slow_log                                             |
| tables_priv                                          |
| time_zone                                            |
| time_zone_leap_second                                |
| time_zone_name                                       |
| time_zone_transition                                 |
| time_zone_transition_type                            |
| user                                                 |
+------------------------------------------------------+
37 rows in set (0.01 sec)

```


### Q2 

Pour mettre en place cette architecture nous allons utiliser des machines primaires-secondaires, i.e une machine en Lecture-Ecriture et une machine en Lecture Seule.  

En premier, il faut modifier le fichier de config de la base de données et d'ajouter ces quelques lignes : 

```
bind-address = 0.0.0.0
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
```

0.0.0.0 permet à la base de données de recevoir des connexions de tout le monde. Il était auparavant de 127.0.0.1. 
Le log_bin va permettre d’activer les logs au format binaire pour la communication entre nos deux serveurs.

On utilise ensuite ```sudo systemctl restart mysql``` afin de notifier les changements au serveur MySQL.

Ensuite on "gèle" la BDD avec cette commande : ```FLUSH TABLES WITH READ LOCK;``` afin de repliquer les données en évitant qu'une donnée s'immisce lors de la réplication de la BDD. 

Ensuite il faut créer un utilisateur qui sera utilisé pour répliquer les données sur notre serveur secondaire. 

```
mysql> CREATE USER 'read-only'@'172.28.101.106' IDENTIFIED BY 'read-only-pw'
    -> ;
Query OK, 0 rows affected (0.06 sec)

mysql> GRANT REPLICATION SLAVE ON *.* TO 'read-only'@'172.28.101.106'; 
Query OK, 0 rows affected (0.02 sec)
```


Sur la seconde base de données, on configure avec cette commande : 
```
mysql> STOP SLAVE;
Query OK, 0 rows affected, 2 warnings (0.00 sec)

mysql> CHANGE MASTER TO 
    -> MASTER_HOST = '172.28.101.118',
    -> MASTER_USER = 'read-only',
    -> MASTER_PASSWORD = 'read-only-pw'
    -> ,MASTER_LOG_FILE = 'mysql-bin.000046',
    -> MASTER_LOG_POS = 1448; 
Query OK, 0 rows affected, (0.07 sec)
```

On récupere le log_file / log_pause grâce à la commande ```SHOW MASTER STATUS``` (à éxecuter dans la connexion primaire)

Ensuite on peut créer une base de données dans la BDD Primaire et confirmer avec un ```SHOW DATABASES;```

On peut ensuite se convaincre de la bonne connexion avec la commande ```SHOW REPLICA STATUS\G```

### Q3
Pour cette question, je suppose qu'il faut également que le serveur secondaire réplique dans le serveur primaire, ce qui entraîne donc une nouvelle relation de type primaire-primaire. 

On commence par renommer l'utilisateur qui servira a répliquer sur le secondaire (j'utilise "secondaire" pour différencier les deux car dans notre cas il n'y a plus que deux "primaires")

```
mysql> RENAME USER 'read-only'@'172.28.101.106' TO 'repl-106'@'172.28.101.106';
```

Ensuite on créé un utilisateur pour la réplication secondaire-primaire. 

```
mysql> CREATE USER 'repl-118'@'172.28.101.118' IDENTIFIED BY 'repl-118-pw'; 
Query OK, 0 rows affected (0.16 sec)
```

On doit ensuite ajouter les droits de réplication à l'utilisateur nouvellement créé. 


Il faut ensuite ajouter le chemin vers les logs pour la BDD secondaire, en rajoutant ```log_bin = /var/log/mysql/mysql-bin.log``` dans le fichier ```mysqld.cnf```

La réplication entre le primaire et le secondaire étant déjà paramétrée (suite à la question 2) il suffit alors de faire la même chose dans l'autre sens (réplication du secondaire sur le primaire)

On récupère le log et sa position : 

```bash
mysql> SHOW MASTER STATUS; 
+---------------+----------+--------------+------------------+-------------------+
| File          | Position | Binlog_Do_DB | Binlog_Ignore_DB | Executed_Gtid_Set |
+---------------+----------+--------------+------------------+-------------------+
| binlog.000012 |      358 |              |                  |                   |
+---------------+----------+--------------+------------------+-------------------+
1 row in set (0.00 sec)
```

On éxecute la suite d'instructions `CHANGE MASTER TO ....` mais cette fois du secondaire au primaire. 

Grace à `SHOW REPLICA STATUS\G` on peut confirmer la mise en place du dispositif avec les deux lignes:

```bash
Replica_IO_Running: Yes
Replica_SQL_Running: Yes
```

Comme ces deux lignes sont présentes dans les deux machines, la configuration Primaire - Primaire a bien été mise en place. 

On peut églament confirmer en créant une base de donnée "replica_2" et en affichant les bases de données disponibles sur l'autre machine, ce qui donne : 

```
mysql> CREATE DATABASE replica_2; 
Query OK, 1 row affected (0.04 sec)
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| replica            |
| replica_2          |
| sys                |
| test               |
+--------------------+
7 rows in set (0.04 sec)
```

On peut également créer une base de données replica_2, une table test et ensuite inserer une valeur aléatoire pour vérifier. 

Sur la seconde machine : 
```
mysql> CREATE TABLE test (
    -> col1 INT,
    -> col2 INT
    -> ); 
Query OK, 0 rows affected (0.14 sec)

mysql> INSERT INTO test VALUES (12,6) 
    -> ;
Query OK, 1 row affected (0.09 sec)
```

Sur la première : 
```
mysql> USE replica_2
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> SELECT * FROM test
    -> ;
+------+------+
| col1 | col2 |
+------+------+
|   12 |    6 |
+------+------+
1 row in set (0.00 sec) 
```


### Q4.1 

Pour cette architecture qui privilégie la cohérence, il va être nécessaire de se servir de la 3è machine comme d'un proxy. 
Pour ce faire, je vais utiliser HAProxy. 

Après avoir installé HAProxy, il faut modifier le fichier situé à ```etc/rsyslog.conf``` pour activer la connexion au proxy. 

Tout d'abord on autorise la connexion UDP sur le port 514 sur la machine du proxy. 
On redirige également tout ce qu'HAProxy envoie vers un fichier de logs. 

```bash
module(load="imudp")
input(type="imudp" port="514")

#HAPROXY log config 
local2.* /var/log/haproxy.log
```
Il nous reste ensuite à modifier le fichier de config d'HAProxy (qui se situe dans ```etc/haproxy.cfg``` )

```
defaults
        log     global
        mode    tcp 
        option  logasap
        option  dontlognull
        no option log-separate-errors
        option  tcplog
        retries 3
        timeout connect 2s
        timeout client  3600s
        timeout server  3600s
        timeout check   2s

listen mysql
        bind    0.0.0.0:6033 
        maxconn 1000
        timeout server 3600s
        timeout client 3600s
        default-serer port 3306 fall 3 inter 1s rise 2 downinter 1s on-marked-down shutdown-sessions
        server master1 172.28.101.118:3306 check
        server master2 172.28.101.106:3306 check 
```
On peut remarquer que le bind écoute toutes les requêtes, à condition qu'elles proviennent du port 6033 (on utilisera ce port plus tard pour se connecter à la BDD via le proxy).

Une fois que tout est paramétré, on allume les 2 bases de données précédentes. 
On peut se convaincre du bon fonctionnement de la base de données avec ```SHOW REPLICA STATUS\G``` (même vérifications que pour la question 3). Finalement on démarre le proxy sur la 3è machine. 

Grâce à ```sudo systemctl status haproxy``` on peut être sur que le proxy est bien démarré grâce à la ligne ```Active : active (running)``` du log ci dessous : 

```bash
● haproxy.service - HAProxy Load Balancer
     Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; preset: enabled)
     Active: active (running) since Tue 2025-10-21 11:29:26 CEST; 1h 32min ago
       Docs: man:haproxy(1)
             file:/usr/share/doc/haproxy/configuration.txt.gz
    Process: 2934 ExecReload=/usr/sbin/haproxy -Ws -f $CONFIG -c -q $EXTRAOPTS (code=exited, status=0/SUCCESS)
    Process: 2937 ExecReload=/bin/kill -USR2 $MAINPID (code=exited, status=0/SUCCESS)
   Main PID: 2587 (haproxy)
     Status: "Ready."
      Tasks: 2 (limit: 1110)
     Memory: 38.7M (peak: 73.3M)
        CPU: 831ms
     CGroup: /system.slice/haproxy.service
             ├─2587 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
             └─2940 /usr/sbin/haproxy -sf 2589 -x sockpair@4 -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/hapr>

```

Une fois que le proxy est lancé, il faut créer un utilisateur dans notre base de données afin de permettre au proxy de se connecter à notre base de données.

Finalement, on peut stopper la base de données, par exemple sur la machine qui héberge le premier primaire par exemple. 

On peut ensuite utiliser le proxy pour se connecter à la base de données. 

```bash
ubuntu@tp2-first:~$ sudo mysql -h 172.28.101.174 -P 6033 -u haproxy -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 94
Server version: 8.0.43-0ubuntu0.24.04.2 (Ubuntu)

Copyright (c) 2000, 2025, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> exit 
Bye
ubuntu@tp2-first:~$ sudo mysql -uroot -p
Enter password: 
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (2)
ubuntu@tp2-first:~$ 

```

On voit bien que la connexion via proxy est toujours disponible alors que la connexion directe n'est plus possible. 

Le proxy ici sert bien à maintenir la cohérence des données, étant donné que les données passent maintenant toujours via le proxy. 

Il existe donc ici une vraie répartition des charges, étant donné que le proxy répartit les requêtes sur le serveur. De plus, les deux serveurs peuvent traiter des requêtes en parallèle. 

Finalement, il reste un dernier problème à traiter afin d'assurer une **vraie** cohérence. Il faut empecher les 2 serveurs d'écrire en même temps sur la même BDD, ce qui supprimerait la cohésion des BDD. 

Pour ce faire, il faut modifier la configuration du proxy comme tel : 
    - ajouter une ligne ```balance first``` dans ```listen mysql``` du fichier ```haproxy.cfg``` 
    - changer le master 2 en 'backup' afin de n'avoir toujours qu'un seul serveur qui execute les requêtes.

Après ces changements, on observe des erreurs dans le status du proxy. En effet, l'utilisateur que j'avais configuré afin de permettre à haproxy de se connecter à la BDD avait un mot de passe, ce qui rend la configuration beaucoup plus hardue. J'ai donc décidé de simplement retirer le mot de passe de l'utilisateur **haproxy@<ADRESSE_IP_PROXY>**. (Dans mon cas, ADRESSE_IP_PROXY = 172.28.101.174) 

Cette pratique n'est bien sûre pas une bonne pratique. Si un utilisateur a tous les droits sur une base de données (comme l'utilisateur haproxy), il faut évidemment protéger, au minimum, par un mot de passe. Pour ce TP, personne ne va essayer de hacker mes tables "test1", "test2" et "coherence", j'enlève donc le mot de passe. 

On redémarre le proxy avec ```sudo systemctl restart haproxy``` et on vérifie qu'il fonctionne avec ```sudo systemctl status haproxy``` qui nous donne le log suivant : 

```bash
ubuntu@tp2-second:~$ sudo mysql -h 172.28.101.174 -P 6033 -u haproxy
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 503
[...]
mysql> select * from users
    -> ;
+----+-------+
| id | name  |
+----+-------+
|  1 | amin  |
|  2 | lucas |
+----+-------+
2 rows in set (0.03 sec)

mysql> SELECT @@hostname;
+------------+
| @@hostname |
+------------+
| tp2-first  |
+------------+
1 row in set (0.00 sec)
```

On voit bien que l'on se connecte via le proxy, et que le proxy redirige vers le serveur numéro 1 (même en ayant "lancé" la BDD depuis la machine numéro 2). On peut ré-arreter la BDD numéro 1 (```sudo systemctl stop mysql```) et récupérer l'host de la BDD qui est maintenant le serveur numéro 2 : 

```bash 
ubuntu@tp2-second:~$ sudo mysql -h 172.28.101.174 -P 6033 -u haproxy
[...]
mysql> SELECT @@hostname;
+------------+
| @@hostname |
+------------+
| tp2-second |
+------------+
1 row in set (0.01 sec)

```

Le proxy permet donc d'assurer la cohésion en agissant comme unique point d'entrée. Toutes les requêtes passent maintenant par le proxy et les 2 serveurs ne peuvent plus écrire en même temps. 


### Q4.2 

Pour cette question, nous allons utiliser le même shéma "hardware" que la question 4.1 c'est-à-dire une machine qui sert de proxy et deux machines pour les tests. 

La différence avec la cohésion est que la disponibilité préfère que le serveur soit toujours accessible, au prix (peut-être) de cohésion dans les données échangées. 

En premier il faut désactiver la réplication semi-synchrone. En effet, cette réplication permettait d'assurer la cohérence car chaque écriture devait être confirmée par l'autre master. Maintenant que nous "abandonnons" la coherence pour la disponibilité, il faut la désactiver via ces commandes : 

```
SET GLOBAL rpl_semi_sync_master_enabled = 0;
SET GLOBAL rpl_semi_sync_slave_enabled = 0;
```

Il se trouve que ces variables n'existent pas dans ma configuration, comme le montre l'erreur suivante : 

```bash
mysql> SET GLOBAL rpl_semi_sync_master_enabled = 0;
ERROR 1193 (HY000): Unknown system variable 'rpl_semi_sync_master_enabled'
```

Ce n'est pas un problème, au contraire, cela signifie juste que le mode semi-synchrone n'est pas activée, ce qui veut dire que la bdd fonctionne en mode asynchrone. 

Dans ce mode, les écritures sont directement traitées par le serveur qui les executent sans confirmation. C'est exactement ce que l'on veut pour privilégier la disponibilité à la cohérence. 

Finalement, il reste à adapter la configuration HAProxy précédente afin de supprimer le backup et d'enlever le ```balance first``` pour privilégier une balance plus équilibrée (i.e. le proxy va maintenant distribuer les requêtes sur les 2 serveurs) 

La partie du fichier (```etc/haproxy/haproxy.cfg```) à modifier est celle dans "listen mysql". 

On passe donc de la configuration de la question 4.1 à : 

```bash
listen mysql
        bind	0.0.0.0:6033
        mode	tcp 
	balance	roundrobin 
	option tcplog 
        default-server port 3306 fall 3 inter 2s rise 2 downinter 1s on-marked-down shutdown-sessions
        server master1 172.28.101.118:3306 check
        server master2 172.28.101.106:3306 check
``` 

On redémarre HAProxy, on vérifie qu'il arrive à se connecter à la BDD : 


```bash
● haproxy.service - HAProxy Load Balancer
     Loaded: loaded (/usr/lib/systemd/system/haproxy.service; enabled; preset: enabled)
     Active: active (running) since Thu 2025-10-23 13:25:11 CEST; 1s ago
       Docs: man:haproxy(1)
             file:/usr/share/doc/haproxy/configuration.txt.gz
   Main PID: 23584 (haproxy)
     Status: "Ready."
      Tasks: 2 (limit: 1110)
     Memory: 6.7M (peak: 7.0M)
        CPU: 167ms
     CGroup: /system.slice/haproxy.service
             ├─23584 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock
             └─23586 /usr/sbin/haproxy -Ws -f /etc/haproxy/haproxy.cfg -p /run/haproxy.pid -S /run/haproxy-master.sock

Oct 23 13:25:11 tp2-proxy systemd[1]: Starting haproxy.service - HAProxy Load Balancer...
Oct 23 13:25:11 tp2-proxy haproxy[23584]: [NOTICE]   (23584) : New worker (23586) forked
Oct 23 13:25:11 tp2-proxy haproxy[23584]: [NOTICE]   (23584) : Loading success.
Oct 23 13:25:11 tp2-proxy systemd[1]: Started haproxy.service - HAProxy Load Balancer.
```

On peut ensuite faire les mêmes vérifications que pour la 4.2. On se connecte, on voit que le serveur utilisé est le second, on arrête le second et on vérifie : le proxy a bien transferé les requêtes du serveur down vers le serveur up. 

```sql
mysql> SELECT @@hostname;
+------------+
| @@hostname |
+------------+
| tp2-second |
+------------+
1 row in set (0.00 sec)

mysql> SELECT @@hostname;
ERROR 2013 (HY000): Lost connection to MySQL server during query
No connection. Trying to reconnect...
Connection id:    14
Current database: *** NONE ***

+------------+
| @@hostname |
+------------+
| tp2-first  |
+------------+
1 row in set (0.21 sec)

mysql> 
```

### Q4.3 

La principale différence entre les 2 configurations réside dans l'algorithme de distribution des requêtes et le mode de fonctionnement des serveurs : la configuration 4.1 utilise `balance first` avec un serveur en mode `backup` pour garantir qu'un seul serveur traite les requêtes à la fois (privilégiant ainsi la cohérence), tandis que la configuration 4.2 utilise `balance roundrobin` avec les deux serveurs actifs simultanément pour répartir équitablement la charge (privilégiant ainsi la disponibilité).

Je pense que la cohérence doit être respectée dans les domaines ou les données sont très importante, par exemple les banques, il vaut mieux être sur que Monsieur X ait l'argent sur son compte avant de lui accorder un crédit, même si la requête doit prendre plus de temps. 

Quant à la disponibilité, je pense qu'elle est de mise dans des serveurs ou les données ne sont pas très importante, et ou une erreur ne couterait pas de l'argent (ou des humains! pauvre secretaire qui doit expliquer à Monsieur X que le virement de $20k était une erreur). Je pense notamment à des blogs ou bien des journaux. 

Par rapport à l'exercice précendent, la solution Primaire-Primaire est très basique. Pour un TP cela peut être une bonne solution, mais si c'est une base de données qui a pour but d'être réellement déployée, cette solution va atteindre rapidement ses limites. 
Par contre, l'ajout du proxy ajoute une complexité supplémentaire (surtout dans le cas de notre TP). Chaque requête va devoir passer en plus par le proxy avant d'atteindre la base de données. 

L'ajout du proxy rajoute une sécurité. 
En effet, dès qu'un serveur tombe en panne, le proxy redirige alors les requêtes vers le(s) serveurs (1 par 1) qui sont indiqués comme ```backup```. Il permet également d'avoir un point d'entrée unique.
Mais il entraîne aussi des problèmes : Comme toutes les connexions passent par le proxy (pour la cohérence), si le proxy tombe en panne, toute la base de données tombe en panne ! 

De plus, pour la disponibilité, les 2 serveurs peuvent écrire en même temps ce qui peut entrainer des données incohérentes. 
