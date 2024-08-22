pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'your-credentials-id' // Replace with your Jenkins credentials ID
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', credentialsId: env.GIT_CREDENTIALS, url: 'https://your-git-repo-url.git'
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'docker-compose build'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    source venv/bin/activate
                    pytest test_myflask.py
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'docker-compose up -d'
                }
            }
        }
    }

    post {
        always {
            sh 'docker-compose down'
        }
    }
}