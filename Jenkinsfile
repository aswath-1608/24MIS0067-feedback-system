stage('Push to Docker Hub') {
    steps {
        withCredentials([
            usernamePassword(
                credentialsId: 'dockerhub-credentials-new',
                usernameVariable: 'DH_USER',
                passwordVariable: 'DH_TOKEN'
            )
        ]) {
            bat '''
                @echo off
                echo %DH_TOKEN% | docker login -u %DH_USER% --password-stdin
                if errorlevel 1 exit /b 1

                docker push aswath1608/feedback-system:%BRANCH_NAME%
                if errorlevel 1 exit /b 1

                docker logout
            '''
        }
    }
}
