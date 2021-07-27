CONTENTS OF THIS FILE
---------------------

 * Connect to a AWS Instance
 * Run Zipkin Server
 * Run Admin Service
 * Run Main Service
 * Run React App
 * Install SQL-Exporter
 * Install Node-Exporter
 * 
 
 
 Connect to a AWS instance
------------------------------------------------
Open the Amazon EC2 console.
In the left navigation pane, choose Instances (Amazon Linux 2 preferred) and select the instance to which to connect.
Choose Connect.
On the Connect To Your Instance page, choose EC2 Instance Connect (browser-based SSH connection), Connect.


 Run Zipkin Service
--------------------
Run the following commands:

sudo yum update -y
sudo amazon-linux-extras install docker -y 
sudo chmod 666 /var/run/docker.sock
sudo systemctl start docker
sudo service docker start
sudo usermod -a -G docker ec2-user
docker run -d -p 9411:9411 openzipkin/zipkin

Note the Zipkin-IP


 Run Admin Service
--------------------
Clone the repo in microservices folder and run the following commands:

--Update the Zipkin-ip in settings.py and products/views.py

sudo sh ./microservices/admin.sh
cd microservices/admin
docker-compose build
docker-compose -d up

#apply migrations
docker-compose exec backend sh
python manage.py makemigrations
python manage.py migrate


 Run Main Service
--------------------
clone the repo in microservices folder and run the following commands:

--Update the Zipkin-IP and Main-IP in main.py

sudo sh ./microservices/main.sh
cd microservices/main
docker-compose build
docker-compose -d up

#apply migrations
docker-compose exec backend sh
python manager.py db init
python manager.py db migrate
python manager.py db upgrade

 Run React App
--------------------
Clone the repo in microservices folder and run the following commands:

--Update the Admin-IP Main-IP in react-crud/src/

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.34.0/install.sh | bash
. ~/.nvm/nvm.sh
nvm install node
sudo yum update -y ;sudo yum install git -y;git --version ;git clone https://github.com/mahidharvarma9/microservices.git 
cd microservices/react-crud
npm init
npm install
npm start

 Install SQL-Exporter
-----------------------
Run the following commands in both Admin and Main instances:

wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.11.0/mysqld_exporter-0.11.0.linux-amd64.tar.gz
tar -xvf mysqld_exporter-0.11.0.linux-amd64.tar.gz
sudo useradd mysqld_exporter
sudo mv mysqld_exporter-0.11.0.linux-amd64/mysqld_exporter /usr/bin/
sudo cp ./microservices/mysqld_exporter.service /etc/systemd/system/mysqld_exporter.service
sudo systemctl start mysqld_exporter
sudo systemctl status mysqld_exporter
sudo systemctl enable



 Install Node-Exporter
-----------------------
Run the following commands in both Admin and Main instances:

curl -LO https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz
tar -xvf node_exporter-0.18.1.linux-amd64.tar.gz
mv node_exporter-0.18.1.linux-amd64/node_exporter /usr/local/bin/
sudo useradd -rs /bin/false node_exporter
nano /etc/systemd/system/node_exporter.service
cd..
sudo cp ./microservices/node_exporter.service /etc/systemd/system/node_exporter.service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl status node_exporter
sudo systemctl enable node_exporter


Monitoring:
 Monitoring can be done locally or in another AWS instance. Prometheus runs on the 9090 endpoint and Grafana at 3000. They can be accessed using localhost, 
 if running locally or using the EC2 instance public IP for remote access by single or multiple parties if running on AWS.
 
 Run Prometheus
-----------------------
Clone the repo and cd in to the prometheus folder.
Update the Admin and Main app instance IPs in prometheus,yml file.
Run the command below (It automatically makes use of the prometheus.yml and rules.yml files):

./prometheus

Prometheus will now start collecting metrics and it can viewed in its UI at http://localhost/9090 or http://<instance-ip>/9090

 Run Grafana
-----------------------
Install Grafana locally using the instructions in its documentation:

https://grafana.com/docs/grafana/latest/installation/?pg=docs

Start grafana-server using:

sudo systemctl start grafana-server

Add prometheus as a datasource using http://localhost/9090 or http://<instance-ip>/9090 as source.
Clone the repo and use the dashboards' JSON files in the Grafana Dashboards folder to import and create the 4 dashboards on Grafana. 
Grafana can now be used to monitor the metrics and calculate the SLIs.












 
