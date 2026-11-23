pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    environment {
        IMAGE_NAME = 'fernandogarzon/devops-taskapi'
        DOCKER_CONFIG = "${WORKSPACE}/.docker"
    }

    triggers {
        pollSCM('H/5 * * * *')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate
                    python -m pip install --quiet -r requirements.txt
                    python -m pytest tests/ -v --junit-xml=test-report.xml
                '''
            }
        }

        stage('Build') {
            steps {
                sh '''
                    docker build -t "$IMAGE_NAME:$BUILD_NUMBER" .
                    docker tag "$IMAGE_NAME:$BUILD_NUMBER" "$IMAGE_NAME:latest"
                '''
            }
        }

        stage('Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh '''
                        set +x
                        printf '%s' "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
                        docker push "$IMAGE_NAME:$BUILD_NUMBER"
                        docker push "$IMAGE_NAME:latest"
                    '''
                }
            }
        }
        stage('Deploy') {
            steps {
                sh '''
                    set +x
                    mkdir -p .kube
                    cp "$HOME/.kube/config" .kube/config
                    chmod 600 .kube/config
                    export KUBECONFIG="$WORKSPACE/.kube/config"
                    kubectl config use-context docker-desktop
                    CLUSTER=$(kubectl config view --minify -o jsonpath='{.contexts[0].context.cluster}')
                    SERVER=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
                    SERVER=$(printf '%s' "$SERVER" | sed 's/127.0.0.1/host.docker.internal/g; s/localhost/host.docker.internal/g')
                    kubectl config unset "clusters.$CLUSTER.certificate-authority-data"
                    kubectl config unset "clusters.$CLUSTER.certificate-authority"
                    kubectl config set-cluster "$CLUSTER" --server="$SERVER" --insecure-skip-tls-verify=true
                    kubectl apply -f k8s/namespace.yaml
                    kubectl apply -f k8s/
                    kubectl set image deployment/taskapi taskapi="$IMAGE_NAME:$BUILD_NUMBER" -n devops-project
                    kubectl rollout status deployment/taskapi -n devops-project --timeout=120s
                    kubectl get pods -n devops-project
                '''
            }
        }

    }

    post {
        always {
            script {
                try {
                    if (fileExists('test-report.xml')) {
                        junit 'test-report.xml'
                    }
                } finally {
                    try {
                        sh 'docker logout || true'
                    } finally {
                        cleanWs()
                    }
                }
            }
        }
        success {
            echo "Pipeline OK: imagen ${IMAGE_NAME}:${BUILD_NUMBER} publicada y desplegada en Kubernetes"
        }
        failure {
            echo "Pipeline fallido en build #${BUILD_NUMBER}. Revisar la consola."
        }
    }
}
