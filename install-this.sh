#!/bin/bash

sudo yum remove -y docker \
                   docker-client \
                   docker-client-latest \
                   docker-common \
                   docker-latest \
                   docker-latest-logrotate \
                   docker-logrotate \
                   docker-engine

sudo yum install -y yum-utils \
  device-mapper-persistent-data lvm2

sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

sudo yum install -y docker-ce docker-ce-cli containerd.io
sudo systemctl enable docker
sudo systemctl start docker
sudo docker run hello-world

sudo usermod -aG docker `whoami`

# enable firewall port for the scraping
sudo firewall-cmd --permanent --add-port=9091/tcp
sudo firewall-cmd --reload

if [ -d /etc/cron.d ]; then
  sudo cp crontab-monitoring /etc/cron.d/
  echo "Crontab properly installed - enjoy!"
else
  echo "Crontab failed to install - monitoring won't poll at intervals"
fi

sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

docker build --rm -f "Dockerfile-pushgateway" -t mon-pushgateway:latest .
docker build --rm -f "Dockerfile-monitor" -t mon-get-processes:latest .

docker-compose up -d