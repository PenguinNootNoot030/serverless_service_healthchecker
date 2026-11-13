# Serverless-service health checker

## Brief

This is a serverless health monitoring system built with AWS.

- [x] Every 5 minutes, Amazon EventBridge invokes a Lambda function to perform an HTTP health check on a configured service.
- [x] For each check, the Lambda function records:
  - Service ID
  - Timestamp of the check
  - HTTP status code
  - Response time
  - Health status
- [x] Each health-check result is stored in Amazon DynamoDB.
- [ ] If a service is unhealthy, an alert is sent through Amazon SNS.

### IAM Configuration

The Lambda execution role requires permission to write health-check results to Amazon DynamoDB.

A sample least-privilege IAM policy is provided in `iam/dynamodb-write-policy.json`, assuming the region is eu-west-2.

Before applying the policy, replace `YOUR_ACCOUNT_ID` with the target AWS account ID and verify that the Region and table name match the deployed DynamoDB table.

The policy grants only `dynamodb:PutItem` access to the specified table.
