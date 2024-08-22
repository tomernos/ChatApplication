pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = '12341234' 
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', credentialsId: env.GIT_CREDENTIALS, url: 'https://github.com/tomernos/python-projects.git'
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