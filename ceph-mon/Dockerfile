# DOCKER-VERSION 1.5.0
# VERSION        0.1

FROM ubuntu:utopic
MAINTAINER PV <viotti@eurecom.fr>

RUN apt-get update && apt-get install -y openssh-server language-pack-en 
COPY debs /root/debs
RUN cd /root/debs; dpkg -i *.deb; apt-get install -f -y; dpkg -i *.deb
RUN locale-gen en_GB.UTF-8
RUN mkdir /var/run/sshd

EXPOSE 22 5000 6789

RUN echo 'root:root' |chpasswd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

#WORKDIR /opt/zookeeper

CMD    ["/usr/sbin/sshd", "-D"]
