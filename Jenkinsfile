pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = credentials('12341234')
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    git branch: 'main', credentialsId: env.GIT_CREDENTIALS, url: 'https://github.com/tomernos/python-projects.git'
                }
            }
        }

        stage('Setup') {
            steps {
                script {
                    sh '''
                    if ! sudo command -v docker &> /dev/null
                    then
                        sudo curl -fsSL https://get.docker.com/ | sh
                    fi
                    
                    if ! sudo command -v docker-compose &> /dev/null
                    then
                        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                    fi
                    
                    if ! sudo command -v python3 &> /dev/null
                    then
                        sudo apt-get update
                        sudo apt-get install -y python3 python3-pip python3-venv
                    fi
                    
                    if ! sudo command -v git &> /dev/null
                    then
                        sudo apt-get update
                        sudo apt-get install -y git
                    fi
                    '''
                }
            }
        }

        stage('Build') {
            steps {
                script {
                    sh 'sudo docker-compose build'
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    python3 -m venv venv
                    source venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    echo "Python version:"
                    python --version
                    echo "Pip version:"
                    pip --version
                    echo "Installed packages:"
                    pip list
                    python3 test_myflask.py
                    deactivate
                    '''
                

                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh 'sudo docker-compose up -d'
                }
            }
        }
    }

    post {
        always {
            sh 'sudo docker-compose down'
        }
    }
}