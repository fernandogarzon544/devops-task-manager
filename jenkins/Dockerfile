FROM jenkins/jenkins:lts-jdk17

USER root

# Docker CLI, Python y gosu según la arquitectura del contenedor.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl gnupg gosu python3 python3-pip python3-venv \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg \
       | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && chmod a+r /etc/apt/keyrings/docker.gpg \
    && . /etc/os-release \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $VERSION_CODENAME stable" > /etc/apt/sources.list.d/docker.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

# kubectl fijado a la versión del clúster local y verificado por SHA-256.
ARG KUBECTL_VERSION=v1.36.1
RUN arch="$(dpkg --print-architecture)" \
    && curl -fsSLo /tmp/kubectl "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${arch}/kubectl" \
    && curl -fsSLo /tmp/kubectl.sha256 "https://dl.k8s.io/release/${KUBECTL_VERSION}/bin/linux/${arch}/kubectl.sha256" \
    && echo "$(cat /tmp/kubectl.sha256)  /tmp/kubectl" | sha256sum --check \
    && install -m 0755 /tmp/kubectl /usr/local/bin/kubectl \
    && rm /tmp/kubectl /tmp/kubectl.sha256

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
