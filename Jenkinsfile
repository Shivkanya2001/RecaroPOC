pipeline {
    agent any

    parameters {
        // Dropdown to select the service
        choice(name: 'SERVICE_LOV', choices: ['Run All Services', 'Service1', 'Service2'], description: 'Choose a service from the list or run all services')

        // Dropdown for Start/Stop action
        choice(name: 'ACTION', choices: ['Start', 'Stop'], description: 'Choose whether to start or stop the selected service')
    }

    stages {
        stage('Checkout and Read File') {
            steps {
                script {
                    // Git clone step
                    def gitRepoUrl = 'https://github.com/Shivkanya2001/RecaroPOC.git'
                    def branchName = 'main'
                    echo "Cloning repository ${gitRepoUrl} on branch ${branchName}"

                    // Ensure the RecaroPOC directory is removed if it exists
                    def dirExists = fileExists('RecaroPOC')
                    if (dirExists) {
                        echo "Directory exists, removing RecaroPOC..."
                        bat "rmdir /S /Q RecaroPOC"  // Remove RecaroPOC directory recursively and quietly
                    } else {
                        echo "Directory RecaroPOC does not exist, proceeding with clone..."
                    }

                    // Clone the repository into the clean workspace
                    bat "git clone --branch ${branchName} ${gitRepoUrl}"

                    // Read the contents of the services.txt file
                    def txtFileContent = readFile('RecaroPOC/services.txt')  // Adjust to the correct file path after cloning
                    
                    // Split the contents of the file into a list (List of Values)
                    def servicesList = txtFileContent.split("\n").collect { it.trim() }

                    // Display the contents of the .txt file and available services
                    echo "Contents of the .txt file from the Git repo:\n${txtFileContent}"
                    echo "Available services: ${servicesList}"

                    // Dynamically populate the SERVICE_LOV dropdown
                    properties([
                        parameters([
                            choice(name: 'SERVICE_LOV', choices: ['Run All Services'] + servicesList, description: 'Choose a service from the list or run all services'),
                            choice(name: 'ACTION', choices: ['Start', 'Stop'], description: 'Choose whether to start or stop the selected service')
                        ])
                    ])
                }
            }
        }

        stage('Start/Stop Service') {
            steps {
                script {
                    // Get the selected service and action (Start or Stop)
                    def service = params.SERVICE_LOV
                    def action = params.ACTION // Start or Stop

                    echo "Selected Service: ${service}"
                    echo "Action: ${action}"

                    // If 'Run All Services' is selected, set all services to be started/stopped
                    if (service == 'Run All Services') {
                        echo "Performing action on all services"
                        def servicesList = readFile('RecaroPOC/services.txt').split("\n").collect { it.trim() }
                        servicesList.each { serviceName ->
                            echo "Performing action on service: ${serviceName}"
                            // Wrap the service name in quotes to handle spaces correctly
                            bat """
                                cd RecaroPOC && python list_services.py "${serviceName}" ${action.toLowerCase()}
                            """
                        }
                    } else {
                        // Execute the action on the selected service
                        echo "Performing action on selected service: ${service}"
                        // Wrap the service name in quotes to handle spaces correctly
                        bat """
                            cd RecaroPOC && python list_services.py "${service}" ${action.toLowerCase()}
                        """
                    }
                }
            }
        }

        stage('Build') {
            steps {
                echo "This is Build Stage"
                echo "Selected Service: ${params.SERVICE_LOV}"  // Display the selected service from LOV
            }
        }

        stage('Test') {
            steps {
                echo "This is Test Stage"
            }
        }

        stage('Deploy') {
            steps {
                echo "This is Deploy Stage"
            }
        }
    }
}
