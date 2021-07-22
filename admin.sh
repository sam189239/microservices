#!bin/sh


yum update -y
amazon-linux-extras install docker -y

usermod -a -G docker ec2-user


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


echo "ALTER USER 'root'@'localhost' IDENTIFIED BY 'MyRootPass1@';CREATE USER 'root'@'%' IDENTIFIED BY 'MyRootPass1@';GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;FLUSH PRIVILEGES;CREATE USER 'mysqld_exporter'@'localhost' IDENTIFIED BY 'MyRootPass1@' WITH MAX_USER_CONNECTIONS 3;GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'mysqld_exporter'@'localhost';FLUSH PRIVILEGES;SELECT user,host FROM mysql.user;" > setup_sql.sql

# Log in to the server with the temporary password, and pass the SQL file to it.
mysql -u root --password="$root_temp_pass" --connect-expired-password < setup_sql.sql


echo "----------------sql setup completed-------------------"


cd microservices/admin
docker-compose build
#docker-compose up -d 

echo "---------------- Built admin-------------------"


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


 
