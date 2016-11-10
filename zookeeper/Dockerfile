# DOCKER-VERSION 1.5.0
# VERSION        0.1

FROM ubuntu:15.04
MAINTAINER PV <viotti@eurecom.fr>

RUN mkdir /var/run/sshd

RUN apt-get update && \
apt-get install -y curl openjdk-7-jre-headless wget openssh-server

# https://www.apache.org/mirrors/dist.html
RUN curl -fL http://www-eu.apache.org/dist/zookeeper/zookeeper-3.4.8/zookeeper-3.4.8.tar.gz | tar xzf - -C /opt && \
mv /opt/zookeeper-3.4.8 /opt/zookeeper

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

EXPOSE 22 2181 3181 4181

RUN echo 'root:root' |chpasswd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

WORKDIR /opt/zookeeper

CMD ["/usr/sbin/sshd", "-D"]
