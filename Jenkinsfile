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
            echo "Pipeline OK: imagen ${IMAGE_NAME}:${BUILD_NUMBER} publicada en Docker Hub"
        }
        failure {
            echo "Pipeline fallido en build #${BUILD_NUMBER}. Revisar la consola."
        }
    }
}
