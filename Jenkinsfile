def stop_success
def rename_success
def remove_success
def rollback_container

pipeline {
    agent { label 'linux-docker' }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Force Git Update') {
            steps {
                script {
                    sh """
                        git fetch --all
                        git reset --hard origin/master
                        git pull origin master
                    """
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${DOCKER_IMAGE}:${DOCKER_TAG} ."
                }
            }
        }

        stage("Stop Old Container"){
            steps {
                script {
                    // stop container process
                    stop_success = sh (
                        script: "docker stop ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    echo "Stop status (${stop_success})"
                }
            }
        }

        stage("Backup Old Container"){
            steps {
                script {
                    // rename container process
                    rename_success = sh (
                        script: "docker rename ${CONTAINER_NAME} ${CONTAINER_NAME}-OLD",
                        returnStatus: true 
                    )

                    echo "Backup status (${rename_success})"
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    withCredentials([
                        string(credentialsId: 'DB_MONARCH_USER', variable: 'db_user'),
                        string(credentialsId: 'DB_MONARCH_PASS', variable: 'db_password'),
                        string(credentialsId: 'RBMQ_MONARCH_USER', variable: 'rabbitmq_username'),
                        string(credentialsId: 'RBMQ_MONARCH_PASS', variable: 'rabbitmq_password'),
                    ]){
                        if (!db_user || !db_password || !rabbitmq_username || !rabbitmq_password) {
                            error "Missing credentials for running the application!"
                        }
                        
                        withEnv(["db_user='${db_user}'", "db_password='${db_password}'",
                        "rabbitmq_username='${rabbitmq_username}'", "rabbitmq_password='${rabbitmq_password}'"]) {
                            sh """
                                docker run --name "${CONTAINER_NAME}" -e db_user=${db_user} -e db_password=${db_password} \
                                -e rabbitmq_username=${rabbitmq_username} -e rabbitmq_password=${rabbitmq_password} \
                                -e db_host=${db_host} -e db_port=${db_port} -e db_name=${db_name} \
                                -e rabbitmq_host=${rabbitmq_host} -e rabbitmq_vhost=${db_name} \
                                --restart=${RESTART_POLICY} -d ${DOCKER_IMAGE}:${DOCKER_TAG}
                            """
                        }

                        rollback_container = false
                        echo "Container named ${CONTAINER_NAME} is running!"
                    }
                }
            }
            post {
                failure {
                    script {
                        rollback_container = true
                    }
                }
                
            }
        }

        stage("Rollback Old Container"){
            when {
                expression {
                    rename_success == 0 && rollback_container
                }
            }
            steps {
                script {
                    // delete container then put it on grep so that it won't return error if container not found
                    rename_status = sh (
                        script: "docker rename ${CONTAINER_NAME}-OLD ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    start_status = sh (
                        script: "docker start ${CONTAINER_NAME}",
                        returnStatus: true 
                    )

                    echo "Rollback status (${rename_status} - ${start_status})"
                }
            }
        }

        stage("Remove Old Container"){
            when {
                expression {
                    rename_success == 0 && !rollback_container
                }
            }
            steps {
                script {
                    // delete container then put it on grep so that it won't return error if container not found
                    remove_success = sh (
                        script: "docker rm ${CONTAINER_NAME}-OLD",
                        returnStatus: true 
                    )

                    echo "Remove return status (${remove_success})"
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed! Affected container will be rolled back, check the logs for details.'
        }
        success {
            echo 'Pipeline completed successfully!'
        }
    }
}