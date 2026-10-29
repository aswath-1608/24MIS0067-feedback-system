pipeline {
    agent any

    environment {
        DOCKERHUB_USER = 'aswath1608'
        IMAGE_NAME = 'feedback-system'
    }

    stages {
        stage('Validate Branch') {
            steps {
                script {
                    if (!(env.BRANCH_NAME in ['v1', 'v2', 'v3'])) {
                        error('Build only v1, v2, or v3 branches')
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %DOCKERHUB_USER%/%IMAGE_NAME%:%BRANCH_NAME% .'
            }
        }

        stage('Push to Docker Hub') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-credentials',
                        usernameVariable: 'DH_USER',
                        passwordVariable: 'DH_TOKEN'
                    )
                ]) {
                    bat '''
                        @echo off
                        echo %DH_TOKEN% | docker login -u %DH_USER% --password-stdin
                        if errorlevel 1 exit /b 1

                        docker push %DOCKERHUB_USER%/%IMAGE_NAME%:%BRANCH_NAME%
                        if errorlevel 1 exit /b 1

                        docker logout
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Docker image built and pushed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
