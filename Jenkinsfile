// Basic ML pipeline
pipeline {
    agent any

    stages {
        stage('Download') {
            steps {
                sh 'bash scripts/shell/download.sh'
            }
        }

        stage('Train') {
            steps {
                sh 'bash scripts/shell/train_model.sh'
            }
        }

        stage('Deploy') {
            steps {
                sh 'bash scripts/shell/deploy.sh'
            }
        }

        stage('Status') {
            steps {
                sh 'bash scripts/shell/status.sh'
            }
        }
    }
}