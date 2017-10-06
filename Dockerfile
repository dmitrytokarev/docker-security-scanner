FROM ubuntu:xenial

ENV LANG C.UTF-8

RUN { \
      echo '#!/bin/sh'; \
      echo 'set -e'; \
      echo; \
      echo 'dirname "$(dirname "$(readlink -f "$(which javac || which java)")")"'; \
    } > /usr/local/bin/docker-java-home && \
    chmod +x /usr/local/bin/docker-java-home

RUN apt-get update && apt-get install -y --no-install-recommends \
      bzip2 \
      unzip \
      xz-utils \
      apt-transport-https \
      ca-certificates \
      curl \
      software-properties-common \
      python3-openssl && \
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add - && \
    add-apt-repository \
    "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) \
    stable" && \
    apt-get update && apt-get install -y --no-install-recommends \
	  docker-ce=17.03.0~ce-0~ubuntu-xenial && \
    apt-get install -y \
      openjdk-8-jre \
    ; \
    rm -rf /var/lib/apt/lists/*; \
    \
    [ "$JAVA_HOME" = "$(docker-java-home)" ]; \
    \
    update-alternatives --get-selections | awk -v home="$JAVA_HOME" 'index($3, home) == 1 { $2 = "manual"; print | "update-alternatives --set-selections" }'; \
    update-alternatives --query java | grep -q 'Status: manual'

COPY packages /packages
COPY scripts /scripts

RUN	chmod +x /packages
RUN	chmod +x /scripts

WORKDIR /scripts

ENTRYPOINT ["/usr/bin/python3"]
CMD [""]
