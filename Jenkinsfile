// === PARAMETER UI BLOCK ===
properties([
  parameters([
    choice(name: 'ENVIRONMENT', choices: ['dev', 'prod'], description: 'Select environment'),

    [$class: 'CascadeChoiceParameter',
      choiceType: 'PT_SINGLE_SELECT',
      filterLength: 1,
      name: 'HOSTNAME',
      description: 'Select Hostname from selected environment',
      referencedParameters: 'ENVIRONMENT',
      script: [
        $class: 'GroovyScript',
        fallbackScript: [script: 'return ["IZ_DENBG0167VM"]', sandbox: false],
        script: [script: '''
          import groovy.json.JsonSlurper

          def env = ENVIRONMENT ?: 'prod'
          def fallback = [dev: "DENBG0166VM", prod: "IZ_DENBG0167VM"]
          def defaultList = [fallback[env]]

          try {
            def file = new File("C:/JenkinsShared/host_mapping.json")
            if (!file.exists()) return defaultList
            def json = new JsonSlurper().parse(file)
            def envList = json[env]
            if (envList && envList.size() > 0) {
              if (!envList.contains(fallback[env])) {
                envList.add(0, fallback[env])
              }
              return envList
            } else {
              return defaultList
            }
          } catch (Exception e) {
            return defaultList
          }
        ''', sandbox: false]
      ]
    ],

    choice(name: 'SERVICE_LOV', choices: ['Run All Services'], description: 'Static fallback (to be updated after clone)'),
    choice(name: 'ACTION', choices: ['Start', 'Stop'], description: 'Choose whether to start or stop the selected service')
  ])
])

pipeline {
  agent none

  stages {
    stage('Setup and Clone') {
      agent any
      steps {
        script {
          def repoDir = 'RecaroPOC'
          if (fileExists(repoDir)) {
            bat "rmdir /S /Q ${repoDir}"
          }
          bat "git clone https://github.com/Shivkanya2001/RecaroPOC.git"

          def txtFilePath = "${repoDir}/services.txt"
          def txtFileContent = readFile(txtFilePath)
          def servicesList = txtFileContent.split("\n").collect { it.trim() }.findAll()

          echo "✅ Contents of services.txt:\n${txtFileContent}"
          echo "📋 Parsed services: ${servicesList}"

          // Update dropdown for next build
          properties([
            parameters([
              choice(name: 'ENVIRONMENT', choices: ['dev', 'prod'], description: 'Select environment'),
              [$class: 'CascadeChoiceParameter',
                choiceType: 'PT_SINGLE_SELECT',
                filterLength: 1,
                name: 'HOSTNAME',
                description: 'Select Hostname from selected environment',
                referencedParameters: 'ENVIRONMENT',
                script: [
                  $class: 'GroovyScript',
                  fallbackScript: [script: 'return ["IZ_DENBG0167VM"]', sandbox: false],
                  script: [script: '''
                    import groovy.json.JsonSlurper

                    def env = ENVIRONMENT ?: 'prod'
                    def fallback = [dev: "DENBG0166VM", prod: "IZ_DENBG0167VM"]
                    def defaultList = [fallback[env]]

                    try {
                      def file = new File("C:/JenkinsShared/host_mapping.json")
                      if (!file.exists()) return defaultList
                      def json = new JsonSlurper().parse(file)
                      def envList = json[env]
                      if (envList && envList.size() > 0) {
                        if (!envList.contains(fallback[env])) {
                          envList.add(0, fallback[env])
                        }
                        return envList
                      } else {
                        return defaultList
                      }
                    } catch (Exception e) {
                      return defaultList
                    }
                  ''', sandbox: false]
              ]],
              choice(name: 'SERVICE_LOV', choices: ['Run All Services'] + servicesList, description: 'Choose a service or run all'),
              choice(name: 'ACTION', choices: ['Start', 'Stop'], description: 'Start or stop the selected service')
            ])
          ])

          echo "ℹ️ SERVICE_LOV updated. New values will reflect in the next build."
        }
      }
    }

    stage('Validate Hostname Selection') {
      agent any
      steps {
        script {
          if (!params.HOSTNAME?.trim()) {
            echo "⚠️ Invalid hostname '${params.HOSTNAME}' for environment '${params.ENVIRONMENT}', skipping execution."
            currentBuild.result = 'SUCCESS'
            return
          }

          timeout(time: 10, unit: 'SECONDS') {
            if (!isNodeAvailable(params.HOSTNAME)) {
              echo "❌ Host '${params.HOSTNAME}' is not online. Skipping service execution."
              currentBuild.result = 'SUCCESS'
              return
            } else {
              echo "✅ Host '${params.HOSTNAME}' is online."
            }
          }
        }
      }
    }

    stage('Start/Stop Service') {
      agent none
      steps {
        script {
          if (isNodeAvailable(params.HOSTNAME)) {
            node(params.HOSTNAME) {
              echo "🔧 Executing on: ${params.HOSTNAME}, ENV: ${params.ENVIRONMENT}, Action: ${params.ACTION}"

              dir('RecaroPOC') {
                if (params.SERVICE_LOV == 'Run All Services') {
                  def services = readFile('services.txt').split("\n").collect { it.trim() }.findAll()
                  services.each { svc ->
                    echo "➡ ${params.ACTION} ${svc}"
                    bat "python list_services.py \"${svc}\" ${params.ACTION.toLowerCase()}"
                  }
                } else {
                  bat "python list_services.py \"${params.SERVICE_LOV}\" ${params.ACTION.toLowerCase()}"
                }
              }
            }
          } else {
            echo "⚠️ Skipping execution as node '${params.HOSTNAME}' is not available."
          }
        }
      }
    }
  }
}

def isNodeAvailable(String nodeName) {
  try {
    def node = jenkins.model.Jenkins.instance.getNode(nodeName)
    def isOnline = node?.toComputer()?.isOnline()
    return isOnline == true
  } catch (Exception e) {
    echo "⚠️ Error checking node availability: ${e.message}"
    return false
  }
}
