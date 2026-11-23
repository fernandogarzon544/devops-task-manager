#!/bin/bash
set -e

# Permite a Jenkins usar el grupo del socket sin abrir permisos a todos.
if [ -S /var/run/docker.sock ]; then
    socket_gid="$(stat -c '%g' /var/run/docker.sock)"
    socket_group="$(getent group "$socket_gid" | cut -d: -f1)"
    if [ -z "$socket_group" ]; then
        socket_group=docker-host
        groupadd -g "$socket_gid" "$socket_group"
    fi
    usermod -aG "$socket_group" jenkins
fi

# Copia privada para que el usuario jenkins pueda leer el kubeconfig del host.
if [ -f /kube/config ]; then
    install -d -m 0700 -o jenkins -g jenkins /var/jenkins_home/.kube
    install -m 0600 -o jenkins -g jenkins /kube/config /var/jenkins_home/.kube/config
fi

exec gosu jenkins /usr/bin/tini -- /usr/local/bin/jenkins.sh "$@"
