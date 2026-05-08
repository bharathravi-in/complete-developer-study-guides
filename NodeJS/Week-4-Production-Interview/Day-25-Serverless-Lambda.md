# Day 25: Serverless & AWS Lambda with Node.js

## 🎯 Learning Objectives
- Understand serverless architecture and cold starts
- Build AWS Lambda functions with Node.js
- Implement API Gateway + Lambda patterns
- Handle common serverless challenges

---

## 📚 Serverless Fundamentals

### Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                   SERVERLESS ARCHITECTURE                      │
├──────────────────────────────────────────────────────────────┤
│                                                                │
│   Client → API Gateway → Lambda → DynamoDB / RDS / S3        │
│                                                                │
│   Triggers:                                                    │
│   ├── HTTP (API Gateway / ALB)                                │
│   ├── Queue (SQS)                                             │
│   ├── Events (EventBridge / SNS)                              │
│   ├── Schedule (CloudWatch cron)                              │
│   ├── Storage (S3 uploads)                                    │
│   └── Stream (DynamoDB / Kinesis)                             │
│                                                                │
│   Benefits: No servers, auto-scale, pay-per-use               │
│   Challenges: Cold starts, 15min timeout, stateless           │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

### Lambda Handler Patterns

```javascript
// Basic Lambda handler
export const handler = async (event, context) => {
  // context.getRemainingTimeInMillis() - time left before timeout
  // event - trigger-specific payload
  
  try {
    const body = JSON.parse(event.body || '{}');
    const result = await processRequest(body);
    
    return {
      statusCode: 200,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data: result })
    };
  } catch (error) {
    console.error('Error:', error); // CloudWatch Logs
    return {
      statusCode: error.statusCode || 500,
      body: JSON.stringify({ error: error.message })
    };
  }
};

// Middleware pattern (middy)
const middy = require('@middy/core');
const httpJsonBodyParser = require('@middy/http-json-body-parser');
const httpErrorHandler = require('@middy/http-error-handler');
const validator = require('@middy/validator');

const baseHandler = async (event) => {
  // event.body is already parsed (by httpJsonBodyParser)
  const { name, email } = event.body;
  const user = await createUser({ name, email });
  return { statusCode: 201, body: JSON.stringify(user) };
};

export const handler = middy(baseHandler)
  .use(httpJsonBodyParser())
  .use(validator({ inputSchema: createUserSchema }))
  .use(httpErrorHandler());
```

### Cold Start Optimization

```javascript
// ❌ Bad: Initialize inside handler (runs every invocation)
export const handler = async (event) => {
  const db = await connectToDatabase(); // Cold on every call!
  return db.query('SELECT ...');
};

// ✅ Good: Initialize outside handler (reused across invocations)
let dbConnection;
async function getDB() {
  if (!dbConnection) {
    dbConnection = await connectToDatabase();
  }
  return dbConnection;
}

export const handler = async (event) => {
  const db = await getDB();
  return { statusCode: 200, body: JSON.stringify(await db.query('SELECT ...')) };
};

// ✅ Provisioned Concurrency (keep instances warm)
// serverless.yml:
// functions:
//   api:
//     provisionedConcurrency: 5

// ✅ Minimize bundle size (reduces cold start)
// - Use esbuild for bundling
// - Tree-shake unused code
// - Avoid heavy SDKs (import only needed AWS clients)
import { DynamoDBClient } from '@aws-sdk/client-dynamodb'; // v3 modular
// NOT: const AWS = require('aws-sdk'); // v2 imports everything
```

### Serverless Framework Setup

```yaml
# serverless.yml
service: my-api

provider:
  name: aws
  runtime: nodejs20.x
  stage: ${opt:stage, 'dev'}
  region: us-east-1
  environment:
    TABLE_NAME: ${self:service}-${self:provider.stage}
    STAGE: ${self:provider.stage}
  iam:
    role:
      statements:
        - Effect: Allow
          Action: [dynamodb:GetItem, dynamodb:PutItem, dynamodb:Query]
          Resource: !GetAtt UsersTable.Arn

functions:
  createUser:
    handler: src/handlers/users.create
    events:
      - httpApi:
          path: /users
          method: POST
    timeout: 10
    memorySize: 256

  getUser:
    handler: src/handlers/users.get
    events:
      - httpApi:
          path: /users/{id}
          method: GET

  processQueue:
    handler: src/handlers/queue.process
    events:
      - sqs:
          arn: !GetAtt OrderQueue.Arn
          batchSize: 10
    timeout: 30

resources:
  Resources:
    UsersTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:provider.environment.TABLE_NAME}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - { AttributeName: id, AttributeType: S }
        KeySchema:
          - { AttributeName: id, KeyType: HASH }

plugins:
  - serverless-esbuild
  - serverless-offline
```

### SQS Event Processing

```javascript
// Process messages from SQS queue
export const handler = async (event) => {
  const results = await Promise.allSettled(
    event.Records.map(async (record) => {
      const message = JSON.parse(record.body);
      await processOrder(message);
    })
  );

  // Return failed message IDs for retry (partial batch failure)
  const failures = results
    .map((result, idx) => result.status === 'rejected' ? event.Records[idx] : null)
    .filter(Boolean);

  return {
    batchItemFailures: failures.map(record => ({
      itemIdentifier: record.messageId
    }))
  };
};
```

---

## 🧪 Interview Questions

### Beginner
**Q1: What is serverless and how does it differ from traditional servers?**
Serverless: cloud provider manages infrastructure, auto-scales, pay-per-execution. You deploy functions, not servers. No idle costs. Differences: no server management, auto-scaling (0 to N), event-driven, stateless, short-lived (max 15 min). Drawbacks: cold starts, vendor lock-in, limited execution time.

**Q2: What is a cold start in Lambda and how does it affect performance?**
Cold start: when Lambda creates a new execution environment (download code, start runtime, initialize). Adds 100ms-5s latency. Occurs on: first invocation, scaling up, after idle timeout (~5-15 min). Mitigation: provisioned concurrency, smaller bundles, keep connections outside handler, use lighter runtimes (Node > Java for cold starts).

**Q3: What triggers can invoke an AWS Lambda function?**
API Gateway (HTTP), SQS (queues), SNS (notifications), S3 (file uploads), DynamoDB Streams (data changes), EventBridge (scheduled/events), CloudWatch (alarms/logs), Kinesis (streaming), Cognito (auth triggers), Step Functions (workflows). Each provides a different event shape.

### Intermediate
**Q4: How do you handle database connections in Lambda functions?**
Challenge: each invocation may create a new connection (connection exhaustion). Solutions: (1) Reuse connections across invocations (module-level variable). (2) Use RDS Proxy (connection pooling). (3) Use DynamoDB (connectionless). (4) Set small connection pool (1-2 per instance). Close connections on SIGTERM.

**Q5: How do you implement error handling and retries in Lambda?**
Sync (API Gateway): return error response, no auto-retry. Async (SQS/SNS): Lambda retries 2x by default. DLQ for persistent failures. SQS: visibility timeout for retry, maxReceiveCount → DLQ. Use partial batch failures (return failed messageIds). Implement idempotency for retried messages (idempotency key in DynamoDB).

**Q6: How do you test Lambda functions locally?**
Tools: serverless-offline (simulates API Gateway), SAM CLI (`sam local invoke`), docker-lambda. Unit test: extract business logic from handler, test separately. Integration test: use localstack (simulates AWS services). Pattern: handler is thin (parse event, call service, format response), services are testable independently.

### Advanced
**Q7: Design a serverless event-driven architecture for an e-commerce order system.**
Flow: API Gateway → Order Lambda → DynamoDB + SQS. Queue triggers: Payment Lambda → SNS → parallel: Inventory Lambda, Notification Lambda, Analytics Lambda. Step Functions for saga orchestration (compensating transactions on failure). EventBridge for cross-service events. DLQ for failed messages.

**Q8: How do you handle the 15-minute Lambda timeout for long-running processes?**
Strategies: (1) Break into smaller steps (Step Functions). (2) Fan-out with SQS (parallel processing). (3) Use ECS/Fargate for long tasks. (4) Recursive invocation (Lambda invokes itself with checkpoint). (5) Stream processing (Kinesis batches). Design for resumability: save progress, pick up where left off.

**Q9: Compare Lambda with containers (ECS/Fargate) — when to use each?**
Lambda: short tasks (<15 min), sporadic traffic, event processing, quick scaling, cost-efficient at low volume. Containers: long-running, consistent traffic, need full control, stateful, complex dependencies. Hybrid: Lambda for API + event processing, containers for background workers. Cost crossover: ~1M requests/month Lambda may exceed container cost.

---

## 🛠️ Hands-on Exercise
Build a serverless API:
1. Serverless Framework project with TypeScript + esbuild
2. CRUD API with DynamoDB
3. SQS queue processing with DLQ
4. Cold start optimization patterns
5. Local development with serverless-offline
6. Deploy to AWS (or localstack)
