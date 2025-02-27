# VirtuNote

VirtuNote is an application for storing and sharing musical notation that enables users to easily save, view, and share music scores. It is designed for musicians, educators, and students who want to exchange their own work and follow the work of other users.

## Project Overview

This project was created for the Distributed Systems course and implements a microservices architecture with three main services:

- **UserAPI**: Handles user authentication and management
- **MetadataAPI**: Manages metadata for music scores
- **ScoreAPI**: Manages the actual score files (PDFs)

## Features

- User registration and authentication using JWT tokens
- Upload and management of PDF music scores
- Score metadata including title, description, and tags
- Social features such as likes and comments
- File storage using AWS S3
- Metadata storage using AWS DynamoDB

## Architecture

The application is built using a microservices architecture with the following components:

### UserAPI

- Handles user registration and authentication
- Manages user profiles and credentials
- Secures passwords using bcrypt hashing
- Provides JWT tokens for authenticated access

### MetadataAPI

- Stores and manages metadata about music scores
- Handles score categorization with tags
- Manages social interactions (likes, comments)
- Provides search and filtering capabilities

### ScoreAPI

- Manages the upload and retrieval of score files (PDFs)
- Communicates with S3 for file storage
- Interacts with the MetadataAPI to maintain file metadata

## Technologies Used

- **Backend**: FastAPI
- **Database**: AWS DynamoDB
- **File Storage**: AWS S3
- **Authentication**: JWT (JSON Web Tokens)
- **Containerization**: Docker and Docker Compose
- **API Documentation**: Swagger/OpenAPI

## Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Route protection with OAuth2 password bearer
- User-specific access controls

## Getting Started

### Prerequisites

- Docker and Docker Compose
- AWS account with access to DynamoDB and S3
- Python 3.11+ (for local development)

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
SECRET_KEY=your_secret_key
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
AWS_S3_BUCKET_NAME=your_s3_bucket_name
DYNAMODB_TABLE_USERS=your_users_table_name
DYNAMODB_TABLE_METADATA=your_metadata_table_name
```

### Running with Docker Compose

1. Clone the repository
2. Create the `.env` file with required variables
3. Build and start the services:

```bash
docker-compose up -d
```

4. Access the services:
   - UserAPI: http://localhost:8000
   - ScoreAPI: http://localhost:8001
   - MetadataAPI: http://localhost:8002

## API Documentation

Once the services are running, you can access the API documentation at:

- UserAPI: http://localhost:8000/docs
- ScoreAPI: http://localhost:8001/docs
- MetadataAPI: http://localhost:8002/docs

## Development

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running Services Locally

```bash
# UserAPI
cd UserAPI
uvicorn main:app --reload --port 8000

# MetadataAPI
cd MetadataAPI
uvicorn main:app --reload --port 8002

# ScoreAPI
cd ScoreAPI
uvicorn main:app --reload --port 8001
```
