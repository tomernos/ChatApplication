pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = credentials('git-credentials')
        DB_CREDENTIALS = credentials('rds-db-credentials')
        DB_HOST = 'flask-app-postgres-db.cn4wyakgw2cz.us-east-1.rds.amazonaws.com'
        DB_NAME = 'flaskapp'
        DB_PORT = '5432'
        //FLASK_SECRET_KEY = credentials('flask-secret-key')
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
                    git branch: 'feature/pgrds', credentialsId: 'git-credentials', url: 'https://github.com/your-repo/your-projects.git'
                
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

                    ./venv/bin/pip3 export DB_USER=$DB_CREDENTIALS_USR
                    ./venv/bin/pip3 export DB_PASSWORD=$DB_CREDENTIALS_PSW
                    ./venv/bin/pip3 export DB_HOST=$DB_HOST
                    ./venv/bin/pip3 export DB_NAME=$DB_NAME
                    ./venv/bin/pip3 export DB_PORT=$DB_PORT
                    # ./venv/bin/pip3 export SECRET_KEY=$FLASK_SECRET_KEY

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
            
                    export DB_USER=$DB_CREDENTIALS_USR
                    export DB_PASSWORD=$DB_CREDENTIALS_PSW
                    export DB_HOST=$DB_HOST
                    export DB_NAME=$DB_NAME
                    export DB_PORT=$DB_PORT
                    # export SECRET_KEY=$FLASK_SECRET_KEY
                    
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