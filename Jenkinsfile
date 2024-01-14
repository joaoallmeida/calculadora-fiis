node {

    deleteDir()

    stage('Clone Repo') {
        checkout scm

    }
    stage('Build Docker Image') {
        app = docker.build('joaoallmeida/calculadora-fiis')

    }
    stage('Push Docker Image') {
        docker.withRegistry('https://registry.hub.docker.com','dockerHubCredentials') {
            app.push("${env.BUILD_NUMBER}")
        }
    }
    
    stage('Set Environment Variables') {        
        sh "sed -i 's|latest|${env.BUILD_NUMBER}|' kubernetes/deploy.yaml"
        sh "sed -i 's|buildNumber|${env.BUILD_NUMBER}|' kubernetes/deploy.yaml"

    }

    stage('Deploy to K8s') {
        withKubeConfig([credentialsId: 'mykubeconfig']) {
            sh 'kubectl apply -f kubernetes/deploy.yaml'
        } 
    }

}