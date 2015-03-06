# DOCKER-VERSION 1.5.0
# VERSION        0.1

FROM debian:jessie
MAINTAINER PV <viotti@eurecom.fr>

ENV ZK_VERSION 3.4.6

RUN apt-get update && apt-get install -y openjdk-7-jre-headless wget openssh-server
RUN wget -q -O - http://apache.mirrors.pair.com/zookeeper/zookeeper-$ZK_VERSION/zookeeper-$ZK_VERSION.tar.gz | tar -xzf - -C /opt \
    && mv /opt/zookeeper-$ZK_VERSION /opt/zookeeper \
    && mkdir -p /tmp/zookeeper
RUN mkdir /var/run/sshd

ENV JAVA_HOME /usr/lib/jvm/java-7-openjdk-amd64

EXPOSE 22 2181 3181 4181

RUN echo 'root:root' |chpasswd
RUN sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config
RUN sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

WORKDIR /opt/zookeeper

CMD    ["/usr/sbin/sshd", "-D"]
