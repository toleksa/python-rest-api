pipeline {                                                                                                                                                                                 
    environment {                                                                                                                                                                          
        IMAGE = "toleksa/${JOB_NAME}"                                                                                                                                                      
        CREDENTIALS = credentials('dockerhub')                                                                                                                                             
        SUBDIR = "docker"                                                                                                                                                         
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
