targetScope = 'resourceGroup'

@description('Explicit opt-in. The default deployment creates no application resources.')
param deployResources bool = false

@minLength(3)
@maxLength(24)
param appName string = 'careerlens-demo'
param location string = resourceGroup().location

@description('Public GHCR image pinned to a tested commit or digest. No registry passwords are needed.')
param image string

@secure()
param databaseUrl string
@secure()
param jwtSecret string
@secure()
param groqApiKey string = ''
param groqModel string = 'qwen/qwen3.8-27b'

resource environment 'Microsoft.App/managedEnvironments@2024-03-01' = if (deployResources) {
  name: '${appName}-env'
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'none'
    }
  }
}

resource app 'Microsoft.App/containerApps@2024-03-01' = if (deployResources) {
  name: appName
  location: location
  properties: {
    managedEnvironmentId: environment!.id
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        allowInsecure: false
        targetPort: 8000
        transport: 'auto'
      }
      secrets: [
        { name: 'database-url', value: databaseUrl }
        { name: 'jwt-secret', value: jwtSecret }
        { name: 'groq-key', value: groqApiKey }
      ]
    }
    template: {
      containers: [
        {
          name: 'careerlens'
          image: image
          resources: { cpu: json('0.5'), memory: '1Gi' }
          env: [
            { name: 'DATABASE_URL', secretRef: 'database-url' }
            { name: 'JWT_SECRET', secretRef: 'jwt-secret' }
            { name: 'GROQ_API_KEY', secretRef: 'groq-key' }
            { name: 'GROQ_MODEL', value: groqModel }
            { name: 'CORS_ORIGINS', value: '' }
            { name: 'ANALYSES_PER_DAY', value: '5' }
            { name: 'GLOBAL_ANALYSES_PER_DAY', value: '20' }
          ]
          probes: [
            {
              type: 'Startup'
              httpGet: { path: '/health', port: 8000, scheme: 'HTTP' }
              periodSeconds: 5
              failureThreshold: 30
            }
            {
              type: 'Readiness'
              httpGet: { path: '/health/database', port: 8000, scheme: 'HTTP' }
              periodSeconds: 15
              failureThreshold: 3
            }
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000, scheme: 'HTTP' }
              periodSeconds: 30
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          { name: 'http', http: { metadata: { concurrentRequests: '10' } } }
        ]
      }
    }
  }
}

output websiteUrl string = deployResources ? 'https://${app!.properties.configuration.ingress.fqdn}' : 'Deployment disabled'
