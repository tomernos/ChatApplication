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

        stage('Setup') {
            steps {
                script {
                    sh '''
                    if ! sudo command -v docker &> /dev/null
                    then
                        sudo curl -fsSL https://get.docker.com/ | sh
                    fi
                    '''
      
        
                    sh '''
                    if ! sudo command -v docker-compose &> /dev/null
                    then
                        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
                        sudo chmod +x /usr/local/bin/docker-compose
                    fi
                    ''' 
            
                    sh '''
                    if ! sudo command -v python3 &> /dev/null
                    then
                        sudo apt-get update
                        sudo apt-get install -y python3 python3-pip
                    fi
                    '''
                    sh '''
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

        stage('Check Environment') {
            steps {
                sh '''
                   echo "User: $(whoami)"
                   echo "Python Version:"
                   python3 --version
                   echo "Python Path:"
                   which python3
                   echo "Pip List:"
                   pip list
                   echo "Environment Variables:"
                   env
                '''
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    # Create and activate virtual environment
                    python3 -m venv venv
                    . venv/bin/activate

                    # Upgrade pip and install requirements in the virtual environment
                    pip install --upgrade pip
                    pip install -r requirements.txt

                    # Display information about the Python environment
                    echo "Python version:"
                    python --version
                    echo "Pip version:"
                    pip --version
                    echo "Installed packages:"
                    pip list

                    # Run the tests
                    python test_myflask.py

                    # Deactivate the virtual environment
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