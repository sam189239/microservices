#installing node_exporter
cd /tmp
curl -LO https://github.com/prometheus/node_exporter/releases/download/v0.18.1/node_exporter-0.18.1.linux-amd64.tar.gz
tar -xvf node_exporter-0.18.1.linux-amd64.tar.gz
mv node_exporter-0.18.1.linux-amd64/node_exporter /usr/local/bin/
useradd -rs /bin/false node_exporter
#nano /etc/systemd/system/node_exporter.service
sudo cp ./microservices/node_exporter.service /etc/systemd/system/node_exporter.service
sudo systemctl daemon-reload
sudo systemctl start node_exporter
sudo systemctl status node_exporter
sudo systemctl enable node_exporter
#http://<server-IP>:9100/metrics

echo "---------------- Installed node_exporter-------------------"

#sql_exporter installation
cd
wget https://github.com/prometheus/mysqld_exporter/releases/download/v0.11.0/mysqld_exporter-0.11.0.linux-amd64.tar.gz
tar -xvf mysqld_exporter-0.11.0.linux-amd64.tar.gz
useradd mysqld_exporter
mv mysqld_exporter-0.11.0.linux-amd64/mysqld_exporter /usr/bin/
sudo cp ./microservices/mysqld_exporter.service /etc/systemd/system/mysqld_exporter.service
systemctl start mysqld_exporter
systemctl status mysqld_exporter 
systemctl enable mysqld_exporter 
#port 9104
echo "---------------- Installed mysqld_exporter-------------------"
