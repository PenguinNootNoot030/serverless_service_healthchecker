# Serverless-service health checker

## Brief
This is a serverless health monitoring system built with AWS.
Every 5 minutes, Amazon Eventbridge invokes a Lambda function to perform an HTTP health check on a provided service.
For each check, the Lambda function records：
- Service ID
- Timestamo of the check
- HTTP status code
- Response time
- Health status
Each health-check result is stored in Dynamo DB.
If a service is unhealthy, an alert is additionally sent out through Amazon SNS.