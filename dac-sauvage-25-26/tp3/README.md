# TP3 Conteneurs et virtualisation légère 

## Réponses aux Questions

### Q1 

En premier il faut installer docker sur toutes les machines virtuelles.
Ensuite, on installe (sur chaque machine) un conteneur SQL avec cette commande : 

```sudo docker run -d --name mysql-server1 -e MYSQL_ROOT_PASSWORD='' -e MYSQL_DATABASE=test -p 3306:3306 mysql:8.0
```

On fait la même chose sur chaque VM, en oubliant pas de changer le port et le nom à chaque fois pour éviter les conflits. (par exemple mysql-server2, 3307 pour la VM2 et mysql-server-proxy, 3308 pour la VMProxy)

On peut ensuite vérifier la connexion à la BDD nouvellement créée : 

```bash
ubuntu@tp2-first:~$ sudo mysql -h 127.0.0.1 -P 3306 -u root -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 9
[...]
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| test               |
+--------------------+
5 rows in set (0.15 sec)

mysql> use test
Database changed
mysql> CREATE TABLE test1(id INT, col1 INT);
Query OK, 0 rows affected (0.12 sec)
mysql> INSERT INTO test1 VALUES (1,6);
Query OK, 1 row affected (0.05 sec)

mysql> SELECT * from test1;
+------+------+
| id   | col1 |
+------+------+
|    1 |    6 |
+------+------+
1 row in set (0.01 sec)
```

### Q2.1 

Pour cette question, je vais devoir créer l'équivalent du paramètre `mysql:8.0`. Pour ce faire, on va utiliser une image docker : un Containerfile

Je vais utiliser ubuntu24.04 et mysql-server/client (principalement). 

On commence par rédiger le Containerfile afin d'installer directement le conteneur sur les machines. 

Le fichier Containerfile est le suivant : 
```
FROM ubuntu:24.04 
ENV DEBIAN_FRONTEND=noninteractive 

ENV MYSQL_ROOT_PASSWORD=root_pw 
ENV MYSQL_DATABASE=test


RUN apt-get update && apt-get install -y \ 
    locales \
    mysql-server \ 
    mysql-client \ 
    && localedef -i en_US \ 
    -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/* 

ENV LANG=en_US.UTF-8 

RUN mkdir -p /var/run/mysqld
VOLUME /var/run/mysqld

RUN sed -i 's/bind-address.*/bind-address=0.0.0.0/' /etc/mysql/mysql.conf.d/mysqld.cnf

COPY init.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/init.sh 

VOLUME /var/lib/mysql 

EXPOSE 3306 

CMD ["/usr/local/bin/init.sh"]
```

En premier on voit que ce sera l'image d'Ubuntu 24.04 qui sera installée. La variable d'environnement juste en dessous permet d'assurer qu'aucun téléchargement ou action ne sera executée lors de l'installation. On définit ensuite les variables d'environnement pour la BDD. 

La suite d'instructions qui suit sert à installer les MAJs nécessaire au bon fonctionnement de la VM, ainsi qu'installer `mysql-server` et `mysql-client` afin de pouvoir créer et utiliser une BDD. 

On créé ensuite les espaces nécessaires pour stocker le socket ainsi que les fichiers temporaires. 

Ensuite on force MySQL à écouter sur toutes les interfaces réseaux. Sans cette modification la base de données n'aurait accepté des requêtes que depuis 127.0.0.1. 

`COPY` permet de déplacer le script à l'intérieur du conteneur. On le rend exécutable grace à chmod et on précise que c'est ce script que l'on doit exécuter au démarrage du conteneur avec `CMD`. 

Voici le fichier `init.sh`: 

```bash
#!/bin/bash 
set -e # if error init.sh stops" 
if [! -d 'var/lib/mysql/mysql"']; then 
	echo "<--Initializing MyMySQL-->"
	mysqld --initialize-insecure --user=mysql 
fi 

echo "<--Launching MyMySQL-->"

mysqld --user=mysql & 
sleep 10 # wait for sql to be ready 

echo "<--MyMySQL Launched-->"
echo "<--Creating root user-->" 

mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';" 2>/dev/null || true #true in case user already exists  
mysql -e "CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';" 2>/dev/null || true 
mysql -e "GRANT ALL PRIVILEGES ON *.* TO 'root'&'%';" 2>/dev/null || true 
mysql -e "FLUSH PRIVILEGES;" 2>/dev/null || true 

if [-n "$MYSQL_DATABASE"]; then 
	mysql -e "CREATE DATABASE IF NOT EXISTS \`${MYSQL_DATABASE}\`;" 2>/dev/null || true 
fi 

echo "<--MyMySQL Ready-->" 

wait # keep container alive 
```

Ici on initialise la BDD si elle ne l'est pas déjà. En effet, même si le conteneur est détruit, le volume lib/mysql est persistant. On aura donc besoin d'initialiser MySQL une unique fois. 

Ensuite on démarre le serveur, et on attend 10s afin de laisser le temps a MySQL de démarrer (en arrière plan, avec `&`). 

On configure ensuite le super-user avec la suite de commandes `mysql -e` (-e pour forcer le script à s'arrêter en cas d'erreur). On utilise 2>/dev/null pour envoyer toutes les erreurs dans le dossier `null`, c'est à dire le néant, la corbeille. L'option "ou" (||) true permet de rester cohérent avec l'option -e. En effet cette option arrête le script dès qu'une erreur est levée. Il faut donc gérer les erreurs "normales" de MySQL (par exemple un utilisateur qui existe déjà, une requête avec une syntaxe incorrecte etc.). Dans ce cas, la logique fait que c'est true qui est retourné, et aucune erreur "normale" ne vient interrompre le script.  


Une fois que ces 2 fichiers ont été configurés, on peut créer une BDD en s'appuyant sur mon image `my-mysql`. Pour ce faire il faut exécuter la commande `sudo docker build -t my-mysql -f Containerfile .`. Cette commande peut être décomposée en : 

    - docker build : Construit une image Docker 
    - -t : Donner un nom à l'image 
    - my-mysql : Le nom de l'image construite 
    - -f Containerfile : Docker attend normalement un fichier Dockerfile, il faut donc préciser que c'est un Containerfile 
    - . : Les configurations nécessaires à la construction de l'image se trouvent dans le dossier courant. 

Quand cette commande se termine, on peut vérifier que notre image a bien été construite avec `sudo docker images` : 

```bash 
ubuntu@tp2-first:~/perso-mysql$ sudo docker images
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
my-mysql     latest    e8c94b51a67e   21 minutes ago   710MB
mysql        8.0       34178dbaefd0   2 days ago       783MB
ubuntu       24.04     97bed23a3497   3 weeks ago      78.1MB
```

On voit bien que mon image a bien été construite. On peut ensuite créer un conteneur a partir de cette image avec la commande `sudo docker run -d -p 3306:3306 --name mysql-test my-mysql` 
Le seul point important de cette commande est la port. 

Pour tester, on vérifie que le conteneur est bien "UP" (`sudo docker ps`). J'ai affiché les logs, même si cette vérification est inutile car si je peux me connecter c'est que la configuration s'est bien passée. 

Ensuite on teste la connexion et l'insertion dans la BDD classiquement. (On utilisera en priorité une commande docker exec, que j'ai découvert plus tard dans le TP, c'est pourquoi j'insère classiquement ici.)

```
ubuntu@tp2-first:~/perso-mysql$ sudo docker run -d -p 3306:3306 --name mysql-test my-mysql
576636c3043f6ab5ada4c19dd4581a777725fcdfdad1ac3d51ccda274fbc7d64
ubuntu@tp2-first:~/perso-mysql$ sudo docker ps
CONTAINER ID   IMAGE      COMMAND                  CREATED         STATUS         PORTS                                         NAMES
576636c3043f   my-mysql   "/usr/local/bin/init…"   8 seconds ago   Up 4 seconds   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql-test
ubuntu@tp2-first:~/perso-mysql$ sudo docker logs mysql-test
<--Launching MyMySQL-->
<--MyMySQL Launched-->
<--Creating root user-->
<--MyMySQL Ready-->
ubuntu@tp2-first:~/perso-mysql$ mysql -h 127.0.0.1 -P 3306 -u root -p
Enter password: 
[...]
mysql> SHOW DATABASES;
+--------------------+
| Database           |
+--------------------+
| information_schema |
| mysql              |
| performance_schema |
| sys                |
| test               |
+--------------------+
5 rows in set (0.07 sec)

mysql> SELECT User,host from mysql.user;
+------------------+-----------+
| User             | host      |
+------------------+-----------+
| root             | %         |
| debian-sys-maint | localhost |
| mysql.infoschema | localhost |
| mysql.session    | localhost |
| mysql.sys        | localhost |
| root             | localhost |
+------------------+-----------+
6 rows in set (0.00 sec)

mysql> USE test; 
Database changed
mysql> CREATE TABLE test1(id INT, col1 INT) 
    -> ; 
Query OK, 0 rows affected (0.25 sec)

mysql> INSERT INTO test1 VALUES (1,10) 
    -> ; 
Query OK, 1 row affected (0.08 sec)

mysql> SELECT * from test1 
    -> ;
+------+------+
| id   | col1 |
+------+------+
|    1 |   10 |
+------+------+
1 row in set (0.00 sec)
```

### Q2.2

Pour voir la taille des différentes images de docker, on exécute cette formule : 
```bash
ubuntu@tp2-first:~/perso-mysql$ sudo docker images
REPOSITORY   TAG       IMAGE ID       CREATED          SIZE
my-mysql     latest    cd0005b7d648   8 minutes ago    710MB
<none>       <none>    e8c94b51a67e   39 minutes ago   710MB
mysql        8.0       34178dbaefd0   2 days ago       783MB
ubuntu       24.04     97bed23a3497   3 weeks ago      78.1MB
``` 

L'image utilisée pour la Q1 est "mysql" et occupe 783MB. Mon image mysql pèse quant à elle 710MB. 

Je pense que cette différence peut être liée à plusieurs paramètres : 
    - Premièrement j'utilise ubuntu. Il existe des distributions qui pèsent plus. 
    - Après avoir vérifié et installé les MAJs je supprime tous les fichiers temporaires qui ont été créés (`rm -rf /var/lib/apt/lists/*`). 
    - Les vérifications que je fais sont sommaires. J'ai choisi d'attendre 10s pour laisser le temps à l'initialisation de se faire. MySQL utilise un système différent qui vérifit vraiment si la BDD à bien été initialisée.

(Cette partie m'a prit beaucoup de temps et de recherches mais je n'ai jamais réussi à faire fonctionner en multi-stage. J'ai tout de même laissé les traces de mes recherches)

Pour réduire la taille de l'image, on peut utiliser notamment la création multi-étape qui permet, en résumant sommairement, d'utiliser plusieurs `FROM`, ce qui permet de disposer de plusieurs bases, et ainsi de ne sélectionner que les elements nécessaires à notre image. 

Pour réduire la taille de l'image je vais donc utiliser debian bullseye, qui est une distribution plus légère qu'ubuntu. 

Ensuite, grace au multi-stage, on décompose la construction de l'imag en 2 étapes. On installe tout le nécessaire pour MySQL avec le premier `FROM`, et ensuite on utilise un autre build pour copier les fichiers nécessaires, en omettant notamment la doc, les caches etc. 

Il existe également des optimisations qui relèvent plus du détail. On peut par exemple utiliser l'option `--no-install-recommends` afin de n'installer que les paquets nécessaires.

Sinon, la configuration reste similaire à la précedente : 

```
// 1ERE ETAPE // 
FROM debian:bullseye AS builder 
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y wget gnupg lsb-release locales && \
    localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

RUN wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb && \
    dpkg -i mysql-apt-config_0.8.22-1_all.deb && \
    apt-get update && \
    apt-get install -y mysql-server mysql-client && \
    rm -rf /var/lib/apt/lists/*

// 2EME ETAPE //
FROM debian:bullseye-slim 

ENV MYSQL_ROOT_PASSWORD=root_pw 
ENV MYSQL_DATABASE=test
ENV LANG=en_US.UTF-8

COPY --from=builder /usr/sbin/mysqld /usr/sbin/mysqld 
COPY --from=builder /usr/bin/mysql* /usr/bin 
COPY --from=builder etc/mysql etc/mysql 

RUN mkdir -p /var/run/mysqld

COPY init.sh /usr/local/bin/ 
RUN chmod +x /usr/local/bin/init.sh

VOLUME /var/lib/mysql 
VOLUME /var/run/mysqld 

EXPOSE 3306

CMD ["/usr/local/bin/init.sh"] 
```

Après lancement, il se trouve que bullseye ne dispose pas des dépôts mysql. J'ai essayé de les rajouter en installant et en utilisant `wget & gnupg` mais j'avais encore des erreurs. J'ai donc décidé de lancer le builder avec ubuntu et de finir la construction avec bullseye-slim. De plus, après avoir construit la nouvelle image qui utilise debian et ubuntu, je n'ai jamais réussi à copier toutes les dépendences nécessaires à MySQL dans debian. 

J'ai donc choisi d'utiliser une autre distribution qu'ubuntu et d'utiliser debian:bookworm. Ce changement nous force à passer de MySQL à MariaDB. 

Le nouveau Containerfile (ci-dessous) est très similaire au précedent. La seule différence est la distribution.
```bash
FROM debian:bookworm-slim 
ENV DEBIAN_FRONTEND=noninteractive
ENV MYSQL_ROOT_PASSWORD=root_pw 
ENV MYSQL_DATABASE=test

RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/mysqld \ 
    && chown -R mysql:mysql /var/run/mysqld 

RUN echo "[mysqld]\nbind-address = 0.0.0.0" > /etc/mysql/mariadb.conf.d/50-server.cnf //Permet d'accepter toutes les connexions 

COPY init.sh /usr/local/bin 
RUN chmod +x /usr/local/bin/init.sh

EXPOSE 3306 

CMD ["/usr/local/bin/init.sh"]
```

Après l'avoir build, on peut vérifier grace a la commande `sudo docker images` que notre nouvelle image est bien plus légère que celle d'avant (modulo les essais ratés). 

```bash
ubuntu@tp2-first:~/perso_mysql_2$ sudo docker images
REPOSITORY   TAG             IMAGE ID       CREATED              SIZE
my-mariadb   latest          c57a1471e675   About a minute ago   448MB
mysql        8.0             34178dbaefd0   2 days ago           783MB
debian       bookworm        d89cafb62862   4 days ago           117MB
debian       bookworm-slim   31b141c0ca6b   4 days ago           74.8MB
alpine       3.20            e89557652e74   2 weeks ago          7.8MB
ubuntu       24.04           97bed23a3497   3 weeks ago          78.1MB
```

Nous sommes donc passés d'une image de 783MB à 450MB ce qui représente un gain de 300MB.
Ensuite il faut construire le conteneur associé à l'image avec `sudo docker run -d -p 3306:3306 --name mariadb-test my-mariadb`

Comme on peut le voir ci-dessous, le conteneur a bien été créé et est bien "UP" (actif).
```
ubuntu@tp2-first:~/perso_mysql_2$ sudo docker ps
CONTAINER ID   IMAGE        COMMAND                  CREATED         STATUS         PORTS                                         NAMES
4d2b83aa5400   my-mariadb   "/usr/local/bin/init…"   6 minutes ago   Up 6 minutes   0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mariadb-test
```

On peut ensuite se connecter à MariaDB avec cette commande sudo docker exec -it mariadb-test mysql -uroot -p`. Les logs ci-dessous montrent bien que la BDD, la table et la données test ont bien été créées et insérées. 

```
ubuntu@tp2-first:~/perso_mysql_2$ sudo docker run -d -p 3306:3306 --name mariadb-test my-mariadb
4d2b83aa540022566fdc4046ca1ff108ec7425759670eaf1bb26432fadf1f84a
ubuntu@tp2-first:~/perso_mysql_2$ sudo docker exec -it mariadb-test mysql -uroot -p
Enter password: 
[...]
MariaDB [(none)]> USE test; 
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed

MariaDB [test]> SELECT * from testmaria;
+------+------+
| id   | col1 |
+------+------+
|    1 |   10 |
+------+------+
1 row in set (0.002 sec)
```

### Q3.1 

sudo docker network create --subnet 172.30.0.0/16 mariadb_net


ubuntu@tp2-first:~$ sudo docker run -d --name master1 --hostname master1 --network mariadb_net --ip 172.30.0.2 -p 3307:3306 my-mariadb
e33daf1cc91c9bd452da8c08bf92a76b2f3b3346dd592b1b656d8f598638a4f9
ubuntu@tp2-first:~$ sudo docker run -d --name master2 --hostname master2 --network mariadb_net --ip 172.30.0.3 -p 3308:3306 my-mariadb
ea7aac381aa211e4b35ab575e4c6c021e350c47183dffd99a1ae52eeaf297b4f

sudo docker exec -it master1 mysql -uroot -p

MariaDB [(none)]> CREATE USER 'repl'@'%' IDENTIFIED BY 'repl_pw'; 
MariaDB [(none)]> GRANT REPLICATION ON *.* TO 'repl'@'%'; 
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near 'ON *.* TO 'repl'@'%'' at line 1
MariaDB [(none)]> GRANT REPLICATION SLAVE ON *.* TO 'repl'@'%';

Il faut également modifier le fichier 50-server.cnf présent dans etc/mysql/mariadb.conf.d/ afin de définir le log_bin de la BDD. 

On fait la même chose sur master2. 

Ensuite il faut mettre en place la réplication primaire-primaire. Pour le conteneur master2 les commandes sont les suivantes : 

```
MariaDB [(none)]> CHANGE MASTER TO 
    -> MASTER_HOST='172.0.0.2',
    -> MASTER_USER='repl',
    -> MASTER_PASSWORD='repl_pw', 
    -> MASTER_PORT=3306,
    -> MASTER_USE_GTID=current_pos;
```

On démarre ensuite la réplication avec `START REPLICA`. On peut se convaincre du bon lancement de la réplication avec `SHOW REPLICA STATUS\G;' qui affiche bien (j'ai volontairement tronqué après les informations importantes):

```
*************************** 1. row ***************************
                Slave_IO_State: Waiting for master to send event
                   Master_Host: 172.30.0.3
                   Master_User: repl
                   Master_Port: 3306
                 Connect_Retry: 60
               Master_Log_File: mysql-bin.000001
           Read_Master_Log_Pos: 328
                Relay_Log_File: master1-relay-bin.000002
                 Relay_Log_Pos: 627
         Relay_Master_Log_File: mysql-bin.000001
              Slave_IO_Running: Yes
             Slave_SQL_Running: Yes
```

Il faut ensuite parametrer le proxy (on utilisera également HAProxy). Pour ce faire, il faut recréer une image HAProxy très sommaire (le plus simple est souvent le mieux) : 

```
FROM haproxy:2.8-alpine
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
```

On doit également définir le fichier haproxy.cfg qui est relativement similaire à celui du TP2 : 

```
global
    log stdout format raw local0
    maxconn 4096
    tune.ssl.default-dh-param 2048

defaults
    log global
    mode tcp
    option tcplog
    timeout connect 10s
    timeout client 1m
    timeout server 1m

frontend mysql_front
    bind *:3306
    default_backend mysql_back

backend mysql_back
    mode tcp
    balance roundrobin
    option tcp-check
    server mysql1 172.30.0.2:3306 check
    server mysql2 172.30.0.3:3306 check
```

On peut tester la connexion comme ci-dessous : (Le serveur utilise mysql mais c'est bien MariaDB qui est lancée)
```
ubuntu@tp2-first:~$ mysql -h 127.0.0.1 -P 3309 -uroot -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 21
Server version: 5.5.5-10.11.14-MariaDB-0+deb12u2-log Debian 12
[...]
mysql> SELECT VERSION(), @@version_comment;
+--------------------------------+-------------------+
| VERSION()                      | @@version_comment |
+--------------------------------+-------------------+
| 10.11.14-MariaDB-0+deb12u2-log | Debian 12         |
+--------------------------------+-------------------+
1 row in set (0.01 sec)
```

On peut tester l'insertion comme ceci : 
```
mysql> CREATE DATABASE mariadb-test;
ERROR 1064 (42000): You have an error in your SQL syntax; check the manual that corresponds to your MariaDB server version for the right syntax to use near '-test' at line 1
mysql> CREATE DATABASE mariadb_test;
Query OK, 1 row affected (0.01 sec)

mysql> CREATE TABLE table_test; 
ERROR 1046 (3D000): No database selected
mysql> SELECT mariadb_test; 
ERROR 1054 (42S22): Unknown column 'mariadb_test' in 'SELECT'
mysql> USE mariadb_test;
Database changed
mysql> CREATE TABLE table_test;
ERROR 1113 (42000): A table must have at least 1 column
mysql> CREATE TABLE table_test(id INT, col1 INT) ;
Query OK, 0 rows affected (0.03 sec)

mysql> INSERT INTO table_test VALUES (1,10) 
    -> ;
Query OK, 1 row affected (0.01 sec)

mysql> SELECT * from table_test ;
+------+------+
| id   | col1 |
+------+------+
|    1 |   10 |
+------+------+
1 row in set (0.00 sec)

mysql> SELECT @@hostname; 
+------------+
| @@hostname |
+------------+
| master1    |
+------------+
1 row in set (0.01 sec)
``` 

Pour le test final, je vais arrêter la base de données du master1, et le proxy va automatiquement changer l'host vers le master2. 

```
ubuntu@tp2-first:~$ sudo docker stop master1
master1
ubuntu@tp2-first:~$ mysql -h 127.0.0.1 -P 3309 -uroot -p
[...]
mysql> SELECT @@hostname; 
+------------+
| @@hostname |
+------------+
| master2    |
+------------+
1 row in set (0.02 sec)
``` 

Comme on peut le voir sur les logs, le proxy a bien balancé la connexion sur le serveur qui était encore UP. 


### Q3.2 

Afin de séparer et sécuriser le réseau interne, il faut tout d'abord supprimer les conteneurs déjà installés. En effet, ils utilisent le port 330{7/8} pour se connecter au réseau public. On va également supprimer les réseaux. A priori il est possible de ne pas les supprimer mais à ce stade je préfère recommencer pour éviter les erreurs. 


ubuntu@tp2-first:~$ sudo docker run -d --name master1 --hostname master1 --network mariadb_private --ip 172.30.0.2 my-mariadb
8c75257e68c1dcd196a962c672a2be8511ece605b8b06129b06291a00eebb6d2
ubuntu@tp2-first:~$ sudo docker run -d --name master2 --hostname master2 --network mariadb_private --ip 172.30.0.3 my-mariadb
4d90c07d51f2488bb45f984c1a93071b5a9301ceaab87dbacdcf6157cdeded2c
ubuntu@tp2-first:~$ sudo docker run -d --name haproxy --network mariadb_private -p 3309:3306 my-haproxy


En enlevant les ports, on "retire" master1 et master2 du réseau public. La connexion ne peut maintenant passer que par le proxy, qui est le seul à avoir un port public et qui écoute sur le port 3306 qui est celui de ma BDD. 

(A noter : La replication Primaire-Primaire n'est plus active car j'ai supprimé les conteneurs). 

Finalement, on peut essayer de se connecter depuis une autre machine (car tp2-firt est connectée au réseau Docker local). Donc par exemple sur tp2-second (172.28.101.118 est l'adresse de tp2-first):

```
ubuntu@tp2-second:~$ mysql -h 172.28.101.118 -P 3306 -uroot -proot_pw
mysql: [Warning] Using a password on the command line interface can be insecure.
ERROR 2003 (HY000): Can't connect to MySQL server on '172.28.101.118:3306' (111)
ubuntu@tp2-second:~$ 
```

Ici la connexion a bien été refusée, master1 et master2 ne sont accessibles que via le réseau local. Par contre, l'accès est toujours possible via le proxy : 

```
ubuntu@tp2-second:~$ mysql -h 172.28.101.118 -P 3309 -uroot -p
Enter password: 
[...]
mysql> SELECT @@hostname;
+------------+
| @@hostname |
+------------+
| master1    |
+------------+
```

La connexion est maintenant seulement possible via le proxy ! Les conteneurs master1 et master2 sont donc bien disponibles seulement via le réseau local ou via le proxy. 


### Q3.3 

Afin de déployer sur plusieurs instances en gardant les garanties de sécurité, il faut déployer 2 conteneurs minimum : 
    - Un conteneur avec MariaDB 
    - Un conteneur avec HAProxy 
De plus il faut que uniquement les proxys puissent acceder au réseau public. 
Il faut donc déployer 3 fois la question 3.2 

Sur chaque VMs les logs sont plutôt similaires, voici ceux de la machine tp2-second : 

```bash
ubuntu@tp2-second:~/mysql-2$ cat Containerfile 
FROM debian:bookworm-slim 
ENV DEBIAN_FRONTEND=noninteractive
ENV MYSQL_ROOT_PASSWORD=root_pw 
ENV MYSQL_DATABASE=test

RUN apt-get update && apt-get install -y --no-install-recommends \
    mariadb-server \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /var/run/mysqld \ 
    && chown -R mysql:mysql /var/run/mysqld 

RUN echo "[mysqld]\nbind-address = 0.0.0.0" > /etc/mysql/mariadb.conf.d/50-server.cnf

COPY init.sh /usr/local/bin 
RUN chmod +x /usr/local/bin/init.sh

EXPOSE 3306 

CMD ["/usr/local/bin/init.sh"]

ubuntu@tp2-second:~/mysql-2$ sudo docker images
REPOSITORY   TAG             IMAGE ID       CREATED       SIZE
my-mariadb   latest          fe10cf775795   3 hours ago   448MB
mysql        8.0             34178dbaefd0   3 days ago    783MB
debian       bookworm-slim   31b141c0ca6b   4 days ago    74.8MB
[Erreurs ...]
ubuntu@tp2-second:~/mysql-2$ sudo docker network create --subnet 172.30.0.0/16 mariadb_private
[Erreurs ...]
ubuntu@tp2-second:~/mysql-2$ sudo docker start master1
master1
ubuntu@tp2-second:~/mysql-2$ sudo docker ps -a
CONTAINER ID   IMAGE        COMMAND                  CREATED              STATUS         PORTS      NAMES
177d4079f789   my-mariadb   "/usr/local/bin/init…"   About a minute ago   Up 8 seconds   3306/tcp   master1
ubuntu@tp2-second:~/mysql-2$ mysql -uroot -proot_pw
mysql: [Warning] Using a password on the command line interface can be insecure.
ERROR 1698 (28000): Access denied for user 'root'@'localhost'
ubuntu@tp2-second:~/mysql-2$ cd ../
ubuntu@tp2-second:~$ mkdir haproxy 
ubuntu@tp2-second:~$ cd haproxy/
ubuntu@tp2-second:~/haproxy$ sudo vi Containerfile
ubuntu@tp2-second:~/haproxy$ sudo vi haproxy.cfg
ubuntu@tp2-second:~/haproxy$ sudo docker build -t my-haproxy -f Containerfile .
DEPRECATED: The legacy builder is deprecated and will be removed in a future release.
            Install the buildx component to build images with BuildKit:
            https://docs.docker.com/go/buildx/

Sending build context to Docker daemon  3.072kB
Step 1/2 : FROM haproxy:2.8-alpine
2.8-alpine: Pulling from library/haproxy
2d35ebdb57d9: Pulling fs layer
c8c0654f77bf: Pulling fs layer
236a0d9ac9b0: Pulling fs layer
a2ba2650cb94: Pulling fs layer
259b22a7d03e: Pulling fs layer
4f4fb700ef54: Pulling fs layer
a2ba2650cb94: Waiting
259b22a7d03e: Waiting
4f4fb700ef54: Waiting
c8c0654f77bf: Verifying Checksum
c8c0654f77bf: Download complete
236a0d9ac9b0: Verifying Checksum
236a0d9ac9b0: Download complete
2d35ebdb57d9: Verifying Checksum
2d35ebdb57d9: Download complete
259b22a7d03e: Verifying Checksum
259b22a7d03e: Download complete
4f4fb700ef54: Verifying Checksum
4f4fb700ef54: Download complete
a2ba2650cb94: Verifying Checksum
a2ba2650cb94: Download complete
2d35ebdb57d9: Pull complete
c8c0654f77bf: Pull complete
236a0d9ac9b0: Pull complete
a2ba2650cb94: Pull complete
259b22a7d03e: Pull complete
4f4fb700ef54: Pull complete
Digest: sha256:16c87727732eadb4559b119a0d9466b5de820a3b2e13d909b8b75f2bdb14a01b
Status: Downloaded newer image for haproxy:2.8-alpine
 ---> 16ea690df52c
Step 2/2 : COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
 ---> 948778654678
Successfully built 948778654678
Successfully tagged my-haproxy:latest
[Erreurs ...]
ubuntu@tp2-second:~$ sudo docker images
REPOSITORY   TAG             IMAGE ID       CREATED          SIZE
my-haproxy   latest          948778654678   27 minutes ago   26.6MB
my-mariadb   latest          fe10cf775795   3 hours ago      448MB
mysql        8.0             34178dbaefd0   3 days ago       783MB
debian       bookworm-slim   31b141c0ca6b   4 days ago       74.8MB
haproxy      2.8-alpine      16ea690df52c   3 weeks ago      26.6MB
ubuntu@tp2-second:~$ sudo docker run -d --name haproxy --network mariadb_private -p 3309:3306 my-haproxy
0ed4e8e7272bcc33d4ec4d4f19eb950f32318d2e3702e3d64c145c330198d464
ubuntu@tp2-second:~$ sudo docker exec -it my-haproxy mysql -h 127.0.0.1 -P 3306 -u root -p -e "INSERT INTO test.testmaria VALUES (2, 20);"
[Erreurs ...]
ubuntu@tp2-second:~$ sudo docker exec -it master1 mysql -u root -p -e "INSERT INTO test.testmaria VALUES (2, 20);"
Enter password: 
ubuntu@tp2-second:~$ sudo docker exec -it master1 mysql -u root -p -e "SELECT * FROM test.testmaria;"
Enter password: 
+------+------+
| id   | col1 |
+------+------+
|    1 |   10 |
|    2 |   20 |
+------+------+
```

Par contre si l'on essaye de se connecter depuis une autre VM, il faut passer par le proxy, l'accès n'est plus possible sans passer par le proxy :

```bash
ubuntu@tp2-first:~$ mysql -h 172.28.101.106 -P 3309 -uroot -p  -e "SELECT * FROM test.testmaria;"
Enter password: 
+------+------+
| id   | col1 |
+------+------+
|    1 |   10 |
|    2 |   20 |
+------+------+
ubuntu@tp2-first:~$ mysql -h 172.28.101.106 -uroot -p  -e "SELECT * FROM test.testmaria;"
Enter password: 
ERROR 1045 (28000): Access denied for user 'root'@'172.28.101.118' (using password: YES)
```



