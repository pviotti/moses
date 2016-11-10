FROM ubuntu:16.10
MAINTAINER PV <viotti@eurecom.fr>

ENV zkversion 3.4.9

RUN mkdir /var/run/sshd \
    && apt update \ 
    && apt install -y iproute2 curl openjdk-8-jre-headless wget openssh-server \
    && curl -fL http://www-eu.apache.org/dist/zookeeper/zookeeper-$zkversion/zookeeper-$zkversion.tar.gz | tar xzf - -C /opt \
    && mv /opt/zookeeper-$zkversion /opt/zookeeper \
    && echo 'root:root' | chpasswd \
    && sed -ri 's/^PermitRootLogin\s+.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -ri 's/UsePAM yes/#UsePAM yes/g' /etc/ssh/sshd_config

ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64

EXPOSE 22 2181 3181 4181

WORKDIR /opt/zookeeper

CMD ["/usr/sbin/sshd", "-D"]
