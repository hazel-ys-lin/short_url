# Short URL Service

A RESTful API service for URL shortening that converts long URLs into short, manageable links with automatic redirection. This service includes input validation, error handling, rate limiting, and automatic expiration mechanisms.

## Features

- URL shortening with automatic redirection
- URL validation (max 2048 characters)
- Rate limiting (5 requests per minute)
- 30-day automatic expiration
- Automatic cleanup of expired URLs
- Health check endpoint
- Comprehensive error handling
- PostgreSQL database storage

## Prerequisites

- Docker
- Docker Compose

## Quick Start

1. Clone the repository:
```bash
git clone https://github.com/hazel-ys-lin/short_url.git
cd short_url
```

2. Create `.env` file in the root directory:
```env
DB_USERNAME=postgres
DB_PASSWORD=postgres
DB_NAME=short_url
DB_HOST=db
BASE_URL=http://localhost:8000
RATE_LIMIT_PER_MINUTE=5
DOCKER_USERNAME=hazellin134340
```

3. Start the services:
```bash
docker-compose up
```

The service will be available at `http://localhost:8000`

## API Documentation
1. Create Short URL
### Request:
- Method: `POST`
- Endpoint: `/shorted`
- Content-Type: `application/json`

### Request Body:
```json
{
    "original_url": "https://example.com/very/long/url"
}
```

### Success Response:
```json
{
    "short_url": "http://localhost:8000/abc123",
    "expiration_date": "2024-01-27T12:00:00",
    "success": true
}
```

### Error Response:
```json
{
    "short_url": "",
    "expiration_date": null,
    "success": false,
    "reason": "URL too long"
}
```


2. Access Short URL
### Request:
- Method: `GET`
- Endpoint: `/{short_code}`

### Response:
- Success: `302: Redirect to original URL`
- Error: Appropriate error status code and message

3. Health Check
### Request:
- Method: `GET`
- Endpoint: `/health`

### Response:
```json
{
    "status": "healthy"
}
```

## Error Codes
| Status Code | Description           | Situation               |
| ----------- | --------------------- | ----------------------- |
| 404         | Not Found             | Short URL doesn't exist |
| 410         | Gone                  | Short URL has expired   |
| 429         | Too Many Requests     | Rate limit exceeded     |
| 500         | Internal Server Error | System error            |

## Project Structure
```
.
├── Dockerfile                # Main service Dockerfile
├── app/
│   ├── __init__.py
│   ├── config.py            # Configuration
│   ├── db.py               # Database connection
│   ├── main.py             # Main application
│   ├── models.py           # Data models
│   └── schemas.py          # Request/Response schemas
├── cleaner/
│   ├── Dockerfile          # Cleaner service Dockerfile
│   ├── __init__.py
│   ├── cleaner.py          # Expired URL cleanup
│   └── pyproject.toml
├── docker-compose.yml
├── poetry.lock
└── pyproject.toml
```

## Development
1. Testing the API:
```bash
# Create a short URL
curl -X POST -H "Content-Type: application/json" \
     -d '{"original_url":"http://example.com"}' \
     http://localhost:8000/shorten

# Use short URL (replace {short_code})
curl -L http://localhost:8000/{short_code}

# Health check
curl http://localhost:8000/health
```

## Environment Variables
| Variable              | Description             | Default               |
| --------------------- | ----------------------- | --------------------- |
| DB_USERNAME           | Database username       | postgres              |
| DB_PASSWORD           | Database password       | postgres              |
| DB_NAME               | Database name           | short_url             |
| DB_HOST               | Database host           | db                    |
| BASE_URL              | Base URL for short URLs | http://localhost:8000 |
| RATE_LIMIT_PER_MINUTE | Rate limit per minute   | 5                     |

## Docker Hub Images
The Docker images are available on Docker Hub:
- Main application: hazellin134340/short_url-app
- Cleaner service: hazellin134340/short_url-cleaner