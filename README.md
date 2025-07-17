# Perplexity API Client

A production-ready Python client for the Perplexity API with AWS integration for storing responses in S3 and DynamoDB.

## Features

- Fetch data from Perplexity API with Cloudflare bypass
- Save responses to local JSON files
- Upload audio files to Amazon S3
- Store structured data in Amazon DynamoDB
- Environment-based configuration
- Clean architecture with separation of concerns:
  - Client layer for API communication
  - Service layer for business logic
  - Dependency injection for better testability
- Asynchronous operations with aioboto3
