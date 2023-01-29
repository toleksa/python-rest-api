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

void setBuildStatus(String message, String state) {
  step([
      $class: "GitHubCommitStatusSetter",
      reposSource: [$class: "AnyDefinedRepositorySource"],
      contextSource: [$class: "DefaultCommitContextSource"],
      errorHandlers: [[$class: "ChangingBuildStatusErrorHandler", result: "UNSTABLE"]],
      statusResultSource: [ $class: "ConditionalStatusResultSource", results: [[$class: "AnyBuildResult", message: message, state: state]] ]
  ]);
}

pipeline {                                                                                                                                                                                 
    environment {                                                                                                                                                                          
        IMAGE = "toleksa/${JOB_NAME}"                                                                                                                                                      
        CREDENTIALS = credentials('dockerhub')                                                                                                                                             
        SUBDIR = "."     
        DB_PORT=13306
        REDIS_PORT=16379
        API_PORT=15000
        API_URL="http://api:${API_PORT}"
        PROMETHEUS_PORT=19090
        PROMETHEUS_URL="http://prometheus:${PROMETHEUS_PORT}"
    }                                                                                                                                                                                      
    agent{                                                                                                                                                                                 
        label ''                                                                                                                                                                           
    }                                                                                                                                                                                      
    stages{                                                                                                                                                                                
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
                docker.image("mariadb:latest").withRun("-p ${DB_PORT}:${DB_PORT} --network ${n} --hostname db -e MARIADB_PASSWORD='password' \
                    -e MARIADB_USER='user' -e MARIADB_DATABASE='python_rest_api' -e MARIADB_ROOT_PASSWORD=password \
                    --mount type=bind,source=${WORKSPACE}/app/init.sql,target=/docker-entrypoint-initdb.d/init.sql","--port ${DB_PORT}") { c ->
                  docker.image("redis:alpine").withRun("-p ${REDIS_PORT}:${REDIS_PORT} --network ${n} --hostname redis","redis-server --port ${REDIS_PORT}") {
                	  docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p ${API_PORT}:${API_PORT} --network ${n} --hostname api -e DB_PASS=password \
                        -e DB_USER=user -e DB_HOST=db -e DB_PORT=${DB_PORT} -e REDIS_HOST=redis -e REDIS_PORT=${REDIS_PORT} -e API_PORT=${API_PORT}") { 
                	    docker.image("bitnami/prometheus:latest").withRun("-p ${PROMETHEUS_PORT}:${PROMETHEUS_PORT} --network ${n} --hostname prometheus \
                          --mount type=bind,source=${WORKSPACE}/prometheus/prometheus.yml,target=/opt/bitnami/prometheus/conf/prometheus.yml",\
                          "--web.listen-address='0.0.0.0:${PROMETHEUS_PORT}'") {
                        sh 'sleep 30s ; docker ps -a docker logs `docker ps -a | grep "bitnami/prometheus:latest" | gawk "{ print $1 }"`'
                  	    pytest_integration_image = docker.build("${IMAGE}-pytest-integration:${BUILD_NUMBER}","-f tests/integration/Dockerfile .")
                  	    pytest_integration_image.tag("latest")
                  	    pytest_integration_image.inside("--network ${n} -e API_URL=${API_URL} -e PROMETHEUS_URL=${PROMETHEUS_URL}") {
                  	  	  sh 'counter=1 ; until $(curl --output /dev/null --silent --head --fail $API_URL/health); do if [ "$counter" -gt 30 ]; then \
                              echo "ERR: python-rest-api app not ready, exiting" ; exit 1 ; fi ; counter=$((counter+1)) ; printf "." ; sleep 1 ; done ; \
                              pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_integration_result.xml /pytest/test_integration.py ; \
                              sleep 15s ; echo $PROMETHEUS_URL ; \
                              pytest -o cache_dir=/tmp/.pytest_cache --junit-xml=test_prometheus_result.xml /pytest/test_prometheus.py'
                        }
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
              junit 'test_prometheus_result.xml'
            }
          }
        }
        stage('Performance Test') {
          steps {
            script {
              withDockerNetwork{ n ->
                docker.image("mariadb:latest").withRun("-p ${DB_PORT}:${DB_PORT} --network ${n} --hostname db -e MARIADB_PASSWORD='password' \
                    -e MARIADB_USER='user' -e MARIADB_DATABASE='python_rest_api' -e MARIADB_ROOT_PASSWORD=password \
                    --mount type=bind,source=${WORKSPACE}/app/init.sql,target=/docker-entrypoint-initdb.d/init.sql","--port ${DB_PORT}") { c ->
                  docker.image("redis:alpine").withRun("-p ${REDIS_PORT}:${REDIS_PORT} --network ${n} --hostname redis","redis-server --port ${REDIS_PORT}") {
                    docker.image("${IMAGE}:${BUILD_NUMBER}").withRun("-p ${API_PORT}:${API_PORT} --network ${n} --hostname api -e DB_PASS=password \
                        -e DB_USER=user -e DB_HOST=db -e DB_PORT=${DB_PORT} -e REDIS_HOST=redis -e REDIS_PORT=${REDIS_PORT} -e API_PORT=${API_PORT}") {
		                  docker.image("blazemeter/taurus:latest").inside("--network ${n} --hostname perf -u 0:0 --entrypoint='' -e API_URL=${API_URL}"){ cc ->
			                  sh 'bzt -o settings.env.API_URL=${API_URL} tests/performance/bzt.yml ; ls -ltr /var/lib/jenkins/workspace/python-rest-api'
		                  }
                    }
                  }
                }
              }
            }
          }
          post {
            always {
	      perfReport 'bzt-result.xml'
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
                sh '''
                    #!/bin/bash
                    for IMG in $(docker images | grep "${IMAGE} " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
                sh '''
                    #!/bin/bash
                    for IMG in $(docker images | grep "${IMAGE}-pytest-integration " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
                sh '''
                    #!/bin/bash
                    for IMG in $(docker images | grep "${IMAGE}-pytest-unit " | grep -v latest | sort -rnk 2 | tail -n +7 | gawk '{ print $1":"$2 }') ; do docker rmi $IMG ; done
                '''
                //sh 'docker volume rm $(docker volume ls -qf "dangling=true")'
                sh 'docker images'
                cleanWs()
            }
        }
    }
    post {
      success {
        setBuildStatus("Build succeeded", "SUCCESS");
      }
      failure {
        setBuildStatus("Build failed", "FAILURE");
      }
    }

}

