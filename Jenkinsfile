pipeline {
	agent any
 
    environment {
        JAVA_HOME = "/opt/java17"
        DEPLOY = "/var/www/html"
	}
 
	stages {
 
        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/alessandra-15/cicd.git',
                    credentialsId: 'github-pat'
        	}
    	}
 
    	stage('Setup Python') {
            steps {
                sh '''
                python3 -m venv venv
                . venv/bin/activate
                pip install -r requirements.txt
                '''
        	}
    	}
 
        stage('Start Apache') {
            steps {
                sh 'sudo systemctl start apache2'
        	}
    	}
 
        stage('Test') {
            steps {
                sh '''
                . venv/bin/activate
                Xvfb :99 -screen 0 1024x768x16 &
                export DISPLAY=:99
                sleep 3
                python test.py
                '''
        	}
    	}
 
        stage('Deploy') {
            steps {
                sh '''
                rsync -av --delete ./ ${DEPLOY}/
                sudo chown -R www-data:www-data ${DEPLOY}
                sudo chmod -R 755 ${DEPLOY}
                '''
        	}
    	}
	}
}
