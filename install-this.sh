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

sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

echo "Now to run it, log out/in and fire off this command: docker-compose up --build -d"