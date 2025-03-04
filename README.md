# VirtuNote

VirtuNote is a comprehensive application for storing and sharing musical notation that enables musicians, educators, and students to easily save, view, and share music scores. It provides a secure, efficient platform for music professionals and enthusiasts to exchange their own compositions, arrangements, and educational materials while discovering and following the work of other users.

## Project Overview

This project was developed for the Distributed Systems course at the Faculty of Informatics in Pula, Croatia. It implements a robust microservices architecture with three primary interconnected services:

- **UserAPI**: Handles user authentication, registration, and profile management
- **MetadataAPI**: Manages comprehensive metadata for music scores including categorization, social interactions, and search functionality
- **ScoreAPI**: Manages the upload, storage, and retrieval of musical score files (PDFs)

The system demonstrates the practical application of distributed systems concepts including microservice communication, data consistency across services, containerization, and cloud-based storage solutions.

## Features

### Core Functionality
- User registration and secure authentication using JWT tokens
- Upload, download, and management of PDF music scores
- Comprehensive score metadata including title, description, tags, and categorization
- Advanced search and filtering capabilities by various criteria

### Social Features
- Like system to show appreciation for others' work
- Commenting system for feedback and discussions
- User profiles to showcase uploaded scores
- Activity tracking for engagement metrics

### Technical Features
- Secure file storage using AWS S3 with unique file identifiers (UUID v4)
- Efficient metadata storage using AWS DynamoDB NoSQL database
- RESTful API architecture with comprehensive endpoint documentation
- Microservices communication with proper error handling and fallbacks
- Data consistency mechanisms across distributed services

## System Architecture

VirtuNote is built on a modern microservices architecture that emphasizes scalability, maintainability, and separation of concerns. Each service is containerized and can be deployed independently, allowing for flexible scaling and updates.

### Microservices Overview

#### UserAPI Service

- Handles user registration and management with unique UUID identifiers  
- Manages user authentication with JWT token-based security  
- Maintains user profiles with creation timestamps  
- Stores and retrieves user information from DynamoDB  
- Provides user lookup by ID and username  
- Supports updating user profile information  
- Implements pagination for retrieving multiple users  

#### MetadataAPI Service

- Stores and manages detailed metadata about music scores  
- Supports basic tagging functionality for score categorization  
- Manages social interactions with likes and comments features  
- Provides search capabilities with filters for user ID, score ID, title, and tags  
- Ensures data consistency with validation and error handling  
- Implements access control to ensure users can only modify their own content  
- Returns standardized response models for consistent API interactions  

#### ScoreAPI Service

- Manages the secure upload and retrieval of PDF score files  
- Validates file types with extension checking  
- Communicates with AWS S3 for file storage and retrieval  
- Generates unique identifiers for each uploaded file  
- Interacts with the MetadataAPI to maintain synchronized file metadata  
- Enforces user-based access controls for file operations  
- Supports direct file downloads with appropriate URL generation  
- Handles proper error responses with detailed logging  


### Communication Patterns

The services communicate using REST APIs with defined contracts, employing:
- HTTP status codes for proper error handling
- JWT token validation for secure service-to-service communication
- Retry mechanisms with exponential backoff for handling temporary failures
- Circuit breakers to prevent cascading failures
- Structured logging for debugging and monitoring

## Technologies Used

### Backend Framework
- **FastAPI**: Modern, high-performance Python web framework with automatic OpenAPI documentation
- **Uvicorn**: ASGI server implementation for running the FastAPI applications
- **Pydantic**: Data validation and settings management using Python type annotations

### Database and Storage
- **AWS DynamoDB**: Fully managed NoSQL database service for consistent, single-digit millisecond latency
- **AWS S3**: Scalable object storage service for storing and retrieving PDF files
- **Boto3**: AWS SDK for Python to interact with Amazon Web Services

### Security and Authentication
- **JWT (JSON Web Tokens)**: For secure authentication and authorization
- **Passlib & Bcrypt**: For password hashing and verification
- **Python-jose**: For JWT token generation and validation
- **OAuth2**: Implementation of the OAuth2 specification with password bearer flow

### Containerization and Orchestration
- **Docker**: For creating consistent development and production environments
- **Docker Compose**: For defining and running multi-container Docker applications
- **Health checks**: For ensuring service availability and proper startup order

### Development Tools
- **Python 3.11**: Latest stable Python version for modern language features
- **Git**: Version control system for collaborative development
- **Python-decouple**: For managing environment variables and configurations
- **Httpx**: Fully featured HTTP client for Python for service-to-service communication

### API Documentation
- **Swagger/OpenAPI**: Automatic interactive API documentation
- **ReDoc**: Alternative documentation UI for API exploration

## Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Route protection with OAuth2 password bearer
- User-specific access controls

## Getting Started

### Prerequisites

- Docker and Docker Compose for containerized deployment
- AWS account with access to DynamoDB and S3 services
- Python 3.11+ (for local development without Docker)
- Git for version control
- Basic understanding of REST APIs and microservices architecture

### AWS Setup

1. Create an AWS account if you don't have one
2. Create an S3 bucket for score storage with appropriate CORS configuration
3. Create DynamoDB tables for user data and metadata
4. Create an IAM user with programmatic access and appropriate permissions for S3 and DynamoDB
5. Note your AWS access key, secret key, and region for configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Security
SECRET_KEY=your_secure_random_secret_key_at_least_32_characters
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
AWS_S3_BUCKET_NAME=your_s3_bucket_name

# DynamoDB Tables
DYNAMODB_TABLE_USERS=your_users_table_name
DYNAMODB_TABLE_METADATA=your_metadata_table_name

# Service Configuration
METADATA_API_URL=http://metadataapi:8000/metadata/
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

### Running with Docker Compose

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/virtunote.git
   cd virtunote
   ```

2. Create the `.env` file with required variables as shown above

3. Build and start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the services:
   - UserAPI: http://localhost:8000
   - ScoreAPI: http://localhost:8001
   - MetadataAPI: http://localhost:8002
   
5. Monitor the logs:
   ```bash
   docker-compose logs -f
   ```

6. To stop the services:
   ```bash
   docker-compose down
   ```

### Creating Initial Admin User

After starting the services, you'll need to create an initial admin user:

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"your_secure_password","email":"admin@example.com"}'
```

## API Documentation

Once the services are running, you can access the interactive API documentation at:

- UserAPI: http://localhost:8000/docs or http://localhost:8000/redoc
- ScoreAPI: http://localhost:8001/docs or http://localhost:8001/redoc
- MetadataAPI: http://localhost:8002/docs or http://localhost:8002/redoc

The documentation provides detailed information about:
- Available endpoints
- Request parameters and body schemas
- Response formats and status codes
- Authentication requirements
- Interactive testing interface

## Development

### Project Structure

Each service follows a similar structure:

```
ServiceName/
├── auth/           # Authentication utilities
├── database/       # Database connection and operations
├── models/         # Pydantic models for data validation
├── routes/         # API route definitions
├── utils/          # Utility functions
├── Dockerfile      # Docker configuration
├── main.py         # Application entry point
└── requirements.txt # Dependencies
```

### Installing Dependencies

```bash
pip install -r requirements.txt
```

### Running Services Locally

For development purposes, you can run each service locally:

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

### Testing

Each service includes unit and integration tests:

```bash
# Run tests for a specific service
cd ServiceName
pytest

# Run tests with coverage report
pytest --cov=. --cov-report=term-missing
```

### Contribution Guidelines

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

© Gabriel Beronja, Faculty of Informatics in Pula (Fakultet informatike u Puli), 2025.

This project was developed as part of the Distributed Systems course at the Faculty of Informatics in Pula. All rights reserved.
