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
              pytest_unit_image = docker.build("${IMAGE}-pytest-unit:${BUILD_NUMBER}","-f tests/unit/Dockerfile .")
              pytest_unit_image.tag("latest")
              pytest_unit_image.inside() {
                sh 'cd /pytest ; pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=$OLDPWD/test_unit_result.xml /pytest/test_unit.py'
              }
            }
          }
          post {
            always {
              junit 'test_unit_result.xml'
            }
          }
        }
        stage('Integration Test') {
          steps {
            script {
              withDockerNetwork{ n ->
                docker.image("mariadb:10.10.2").withRun("-p 3306:3306 --network ${n} --hostname db -e MARIADB_PASSWORD='password' -e MARIADB_USER='user' -e MARIADB_DATABASE='python_rest_api' -e MARIADB_ROOT_PASSWORD=password --mount type=bind,source=${WORKSPACE}/app/init.sql,target=/docker-entrypoint-initdb.d/init.sql") { c ->
                  docker.image("redis:7.0.5-alpine").withRun("-p 6379:6379 --network ${n} --hostname redis") {
                	  docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p 5000:5000 --network ${n} --hostname webserver -e DB_PASS=password -e DB_USER=user -e DB_HOST=db -e REDIS_HOST=redis") { 
                  	  pytest_integration_image = docker.build("${IMAGE}-pytest-integration:${BUILD_NUMBER}","-f tests/integration/Dockerfile .")
                  	  pytest_integration_image.tag("latest")
                  	  pytest_integration_image.inside("--network ${n}") {
                  	    sh 'counter=1 ; until $(curl --output /dev/null --silent --head --fail http://docker1.kube.ac:5000/health); do if [ "$counter" -gt 30 ]; then echo "ERR: python-rest-api app not ready, exiting" ; exit 1 ; fi ; counter=$((counter+1)) ; printf "." ; sleep 1 ; done ; pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_integration_result.xml /pytest/test_integration.py'
                  	  }
                    }
									}
                }
              }
            }
          }
          post {
            always {
              junit 'test_integration_result.xml'
            }
          }
        }
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
                sh '''#!/bin/bash
                      for IMG in $(docker images | grep "${IMAGE}-pytest-integration " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
                sh '''#!/bin/bash
                      for IMG in $(docker images | grep "${IMAGE}-pytest-unit " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
                sh 'docker images'
            }
        }


    }
}
