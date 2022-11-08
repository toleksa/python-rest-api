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
    }
}
