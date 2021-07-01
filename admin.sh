#!bin/sh


# yum update -y
# yum install git -y
# git --version
# git clone https://github.com/mahidharvarma9/microservices.git

# sudo sh  /microservices/main.sh

yum update -y
amazon-linux-extras install docker -y

usermod -a -G docker ec2-user


# yum update -y
# yum install -y awslogs
# # Edit the /etc/awslogs/awslogs.conf file to configure the logs to track. For more information about editing this file, see CloudWatch Logs agent reference.

# # By default, the /etc/awslogs/awscli.conf points to the us-east-1 Region. To push your logs to a different Region, edit the awscli.conf file and specify that Region.
# # service docker start
# service awslogs start
# systemctl start awslogsd
# chkconfig awslogs on

echo "----------------Basic cmds and cloudwatch executed-------------------"
#git
# yum update -y
# yum install git -y
# git --version

echo "----------------Git installed-------------------"
##docker-compose
curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

docker-compose version


systemctl start docker
chmod 666 /var/run/docker.sock

echo "----------------Docker-compose installed-------------------"
## adding sql

yum install https://dev.mysql.com/get/mysql80-community-release-el7-3.noarch.rpm -y


amazon-linux-extras install epel -y
yum install mysql-community-server -y

systemctl enable --now mysqld
systemctl status mysqld

##get temp root password
grep 'temporary password' /var/log/mysqld.log

root_temp_pass=$(grep 'A temporary password' /var/log/mysqld.log |tail -1 |awk '{split($0,a,": "); print a[2]}')
echo "root_temp_pass:"$root_temp_pass

echo "----------------sql installed-------------------"




#mysql -uroot -p $root_temp_pass
#ALTER USER 'root'@'localhost' IDENTIFIED BY 'MyRootPass1@';
#CREATE USER 'root'@'%' IDENTIFIED BY 'MyRootPass1@';
#GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
#FLUSH PRIVILEGES;
#SELECT user,host FROM mysql.user;

#mysql -u root -p<<BASH_QUERY
#ALTER USER 'root'@'localhost' IDENTIFIED BY 'MyRootPass1@';
#CREATE USER 'root'@'%' IDENTIFIED BY 'MyRootPass1@';
#GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;
#FLUSH PRIVILEGES;
#SELECT user,host FROM mysql.user;
#BASH_QUERY

# Set up a batch file with the SQL commands
echo "ALTER USER 'root'@'localhost' IDENTIFIED BY 'MyRootPass1@';CREATE USER 'root'@'%' IDENTIFIED BY 'MyRootPass1@';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;FLUSH PRIVILEGES;CREATE USER 'mysqld_exporter'@'localhost' IDENTIFIED BY 'MyRootPass1@' WITH MAX_USER_CONNECTIONS 3;GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'mysqld_exporter'@'localhost';FLUSH PRIVILEGES;SELECT user,host FROM mysql.user;" > setup_sql.sql

# Log in to the server with the temporary password, and pass the SQL file to it.
mysql -u root --password="$root_temp_pass" --connect-expired-password < setup_sql.sql


echo "----------------sql setup completed-------------------"

#sudo sh setup2.sh

##running project

#git clone https://github.com/mahidharvarma9/microservices.git

echo "----------------git clone completed-------------------"

cd microservices/admin
docker-compose build
#docker-compose up -d 

echo "---------------- Built admin-------------------"
# cd ../main
# docker-compose build
# #docker-compose up -d 

# echo "---------------- Built main-------------------"


#installing node_exporter
cd /tmp
curl -LO https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz
tar -xvf node_exporter-0.18.1.linux-amd64.tar.gz
mv node_exporter-0.18.1.linux-amd64/node_exporter /usr/local/bin/
useradd -rs /bin/false node_exporter
#nano /etc/systemd/system/node_exporter.service
cp ~/microservices/node_exporter.service ~/tmp/etc/systemd/system/node_exporter.service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl status node_exporter
sudo systemctl enable node_exporter
#http://<server-IP>:9100/metrics

echo "---------------- Installed node_exporter-------------------"

## migration for admin
#docker-compose exec backend sh

#python manage.py makemigrations
#python manage.py migrate

## migration for main
#docker-compose exec backend sh
#python manager.py db init
#python manager.py db migrate
#python manager.py db upgrade

##tiget vnc
#user:ubuntu
#pass:Ubuntu1@

## create a migrations folder with __init__.py

##list of commands for dockers
 
 #any error related to memory of docker 
#sudo service docker stop
#sudo service docker start

#for running shell of db
#docker exec -it admin_db_1(Name of container in docker ps) bash
#mysql -u root -p
#MyRootPass1@

#show databases
#use admin
#select * from products_user;
#show schema
#desc products_user

#INSERT INTO products_user (id) VALUES (1), (2), (3), (4), (5), (6), (7), (8), (9), (10);

#docker restart 1
#sudo chmod 666 /var/run/docker.sock

#curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
#. ~/.nvm/nvm.sh
#nvm install node
