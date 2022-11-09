def withDockerNetwork(Closure inner) {
//https://www.kabisa.nl/tech/running-multiple-docker-containers-in-parallel-with-jenkins/
  try {
    networkId = UUID.randomUUID().toString()
    sh "docker network create ${networkId}"
    inner.call(networkId)
  } finally {
    sh "docker network rm ${networkId}"
  }
}

pipeline {                                                                                                                                                                                 
    environment {                                                                                                                                                                          
        IMAGE = "toleksa/${JOB_NAME}"                                                                                                                                                      
        CREDENTIALS = credentials('dockerhub')                                                                                                                                             
        SUBDIR = "."                                                                                                                                                         
    }                                                                                                                                                                                      
    agent{                                                                                                                                                                                 
        label ''                                                                                                                                                                           
    }                                                                                                                                                                                      
    stages{                                                                                                                                                                                
        stage('Checkout'){                                                                                                                                                                 
            steps{                                                                                                                                                                         
                git url: 'https://github.com/toleksa/python-rest-api.git', branch: 'main'
                sh 'ls -la'
                sh 'cat ${SUBDIR}/Dockerfile'
            }                                                                                                                                                                              
        }
        stage('Build'){                                                                                                                                                                    
            steps{                                                                                                                                                                         
                script{                                                                                                                                                                    
                    docker_image = docker.build("${IMAGE}:${BUILD_NUMBER}","${SUBDIR}")                                                                                                    
                    docker_image.tag('latest')                                                                                                                                             
                }                                                                                                                                                                          
                sh 'docker images'                                                                                                                                                         
            }                                                                                                                                                                              
        }  
        stage('Unit Test'){
          steps{
            //sh 'cd ${SUBDIR} ; python3 -m pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_unit_result.xml test_unit.py'
            script {
              withDockerNetwork{ n ->
                docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p 8888:80 --network ${n} --hostname webserver") { c ->
                  pytest_unit_image = docker.build("${IMAGE}-pytest-unit:${BUILD_NUMBER}","-f tests/unit/Dockerfile .")
                  pytest_unit_image.tag("latest")
                  pytest_unit_image.inside("--network ${n}") {
                    sh 'pwd ; ls -l ; cd /pytest ; pwd ; ls -l ; pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=$OLDPWD/test_unit_result.xml /pytest/test_unit.py'
                  }
                }
              }
            }
          }
          post {
            always {
              junit 'test_unit_result.xml'
            }
          }
        }
//        stage('Integration Test') {
//          steps {
//            //script {
//            //  network_name = "${BUILD_TAG}"
//            //  sh "docker network create ${network_name}"
//            //  docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p 8888:80 --network ${network_name} --hostname webserver") {
//            //    pytest_image = docker.build("${IMAGE}-pytest:${BUILD_NUMBER}","src/pytest")
//            //    pytest_image.tag("latest")
//            //    pytest_image.inside("--network ${network_name}") {
//            //      sh 'pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_web_result.xml /pytest/test_web.py'
//            //    }
//            //  }
//            //  sh "docker network rm ${network_name}"
//            //}
//            script {
//              withDockerNetwork{ n ->
//                docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p 8888:80 --network ${n} --hostname webserver") { c ->
//                  pytest_integration_image = docker.build("${IMAGE}-pytest-integration:${BUILD_NUMBER}","src/pytest/integration")
//                  pytest_integration_image.tag("latest")
//                  pytest_integration_image.inside("--network ${n}") {
//                    sh 'pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_web_result.xml /pytest/test_web.py'
//                  }
//                }
//              }
//            }
//          }
//          post {
//            always {
//              junit 'test_web_result.xml'
//            }
//          }
//        }
        stage('Security Test') {
        // requires Jenkins plugin https://plugins.jenkins.io/warnings-ng/
          steps {
            script {
              trivyImage = docker.image('aquasec/trivy:latest')
              trivyImage.inside("--entrypoint= -u root --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock") {
                sh '''trivy image \
                            --format=json \
                            -o results.json \
                            ${IMAGE}:${BUILD_NUMBER}'''
              }
              recordIssues(tools: [trivy(pattern: 'results.json')])
            }
          }
        }
        stage('Publish'){
            steps{
                script {
                    docker.withRegistry( '', 'dockerhub' ) {
                        docker_image.push()
                        docker_image.push('latest')
                    }
                }
            }
        }
        stage('Cleanup'){
            steps{
                sh 'hostname -f'
                sh '''#!/bin/bash
                      for IMG in $(docker images | grep "${IMAGE} " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
//                sh '''#!/bin/bash
//                      for IMG in $(docker images | grep "${IMAGE}-pytest-integration " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
//                '''
//                sh '''#!/bin/bash
//                      for IMG in $(docker images | grep "${IMAGE}-pytest-unit " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
//                '''
                sh 'docker images'
            }
        }


    }
}
