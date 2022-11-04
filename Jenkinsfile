pipeline {                                                                                                                                                                                 
    environment {                                                                                                                                                                          
        IMAGE = "toleksa/${JOB_NAME}"                                                                                                                                                      
        CREDENTIALS = credentials('dockerhub')                                                                                                                                             
        SUBDIR = "docker/app"                                                                                                                                                         
    }                                                                                                                                                                                      
    agent{                                                                                                                                                                                 
        label ''                                                                                                                                                                           
    }                                                                                                                                                                                      
    stages{                                                                                                                                                                                
        stage('Checkout'){                                                                                                                                                                 
            steps{                                                                                                                                                                         
                git url: 'https://github.com/toleksa/python-rest-api.git', branch: 'main'
                sh 'ls -la'
            }                                                                                                                                                                              
        } 
    }
}
