pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = credentials('git-credentials-id')
        DB_CREDENTIALS = credentials('db-credentials-id')
        DB_HOST = credentials('db-host-id')
        DB_NAME = credentials('db-name-id')
        SECRET_KEY = credentials('secret-key-id')
    }

    stages {

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

                    echo "directory:"
                    python3 --version

                    # Upgrade pip and install requirements in the virtual environment
                    ./venv/bin/pip3 install --upgrade pip
                    ./venv/bin/pip3 install -r requirements.txt

                    # Display information about the Python environment
                    echo "Python version:"
                    ./venv/bin/python3 --version
                    echo "Pip version:"
                    ./venv/bin/pip3 --version
                    echo "Installed packages:"
                    pip3 list
            
    

                    # Run the tests
                    ./venv/bin/python3 test_myflask.py

                    # Deactivate the virtual environment
                    deactivate
                    '''
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    sh '''
                    echo "Deploying the application..."
                    # Create a temporary .env file
                    echo "DB_USER=$DB_CREDENTIALS_USR" > .env
                    echo "DB_PASSWORD=$DB_CREDENTIALS_PSW" >> .env
                    echo "DB_HOST=$DB_HOST" >> .env
                    echo "DB_NAME=$DB_NAME" >> .env
                    echo "SECRET_KEY=$SECRET_KEY" >> .env
                    
                    # Use the .env file in your deployment
                    docker-compose --env-file .env up -d
                    '''
                }
            }
        }
    }

    post {
        /*always {
            //sh 'sudo docker-compose down'
           
            
        }*/
        success {
            sh '''
                echo 'Application deployed successfully and is running'
            '''
        }
        failure {
            sh '''
                echo 'Deployment failed'
                sudo docker-compose down
            '''
        }
    }
}