# API Endpoints Documentation

## Knowledge Base Endpoints

### Query Knowledge Base
```http
POST /brain/query
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "What are the artist's recent achievements?",
  "doc_types": ["news", "social_media"],
  "top_k": 5,
  "stream": false,
  "use_cache": true
}
```

Response:
```json
{
  "response": "The artist has achieved several milestones...",
  "source_nodes": [
    {
      "content": "...",
      "metadata": {
        "doc_type": "news",
        "source": "music_blog",
        "timestamp": "2024-02-15T10:00:00Z"
      },
      "score": 0.95
    }
  ]
}
```

### Upload Document
```http
POST /brain/documents
Authorization: Bearer <token>
Content-Type: multipart/form-data

metadata={
  "doc_type": "news",
  "source": "music_blog",
  "language": "en",
  "metadata": {
    "url": "https://example.com/article",
    "author": "John Doe"
  }
}
file=@article.txt
```

Response:
```json
{
  "doc_id": "abc123",
  "message": "Document uploaded successfully"
}
```

### Delete Documents
```http
DELETE /brain/documents
Authorization: Bearer <token>
Content-Type: application/json

{
  "doc_types": ["news"],
  "source": "music_blog"
}
```

Response:
```json
{
  "message": "Documents deleted successfully"
}
```

## Platform Integration Endpoints

### Social Media Integration

#### Connect Platform
```http
POST /platforms/connect
Authorization: Bearer <token>
Content-Type: application/json

{
  "platform": "instagram",
  "credentials": {
    "access_token": "..."
  }
}
```

Response:
```json
{
  "platform_id": "xyz789",
  "status": "connected",
  "scopes": ["read_insights", "read_posts"]
}
```

#### Fetch Analytics
```http
GET /platforms/{platform}/analytics
Authorization: Bearer <token>
```

Response:
```json
{
  "platform": "instagram",
  "metrics": {
    "followers": 10000,
    "engagement_rate": 3.5,
    "growth_rate": 2.1
  },
  "timestamp": "2024-02-15T10:00:00Z"
}
```

## Analytics Endpoints

### Performance Overview
```http
GET /analytics/overview
Authorization: Bearer <token>
```

Response:
```json
{
  "streaming": {
    "total_streams": 1000000,
    "monthly_growth": 15.2,
    "top_tracks": [...]
  },
  "social": {
    "total_followers": 50000,
    "engagement_rate": 4.2,
    "top_posts": [...]
  },
  "revenue": {
    "monthly": 5000.00,
    "growth": 12.5,
    "sources": [...]
  }
}
```

### Growth Analytics
```http
GET /analytics/growth
Authorization: Bearer <token>
Query Parameters:
  - timeframe: "7d" | "30d" | "90d" | "1y"
  - metrics: ["followers", "streams", "revenue"]
```

Response:
```json
{
  "timeframe": "30d",
  "data_points": [
    {
      "date": "2024-02-15",
      "metrics": {
        "followers": 10000,
        "streams": 50000,
        "revenue": 1500.00
      }
    }
  ],
  "growth_rates": {
    "followers": 5.2,
    "streams": 8.1,
    "revenue": 12.5
  }
}
```

## User Management

### Artist Profile
```http
GET /artists/profile
Authorization: Bearer <token>
```

Response:
```json
{
  "id": "artist123",
  "stage_name": "Artist Name",
  "email": "artist@example.com",
  "social_links": {
    "instagram": "https://instagram.com/artist",
    "spotify": "https://spotify.com/artist"
  },
  "settings": {
    "notifications": true,
    "privacy": "public"
  }
}
```

### Team Management
```http
POST /artists/team
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "manager@example.com",
  "role": "manager",
  "permissions": ["read", "write"]
}
```

Response:
```json
{
  "member_id": "team123",
  "status": "invited",
  "expires_at": "2024-02-22T10:00:00Z"
}
```

## System Health

### Status Check
```http
GET /health
```

Response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 1234567,
  "services": {
    "database": "healthy",
    "cache": "healthy",
    "search": "healthy"
  }
}
```

### Performance Metrics
```http
GET /health/metrics
Authorization: Bearer <token>
```

Response:
```json
{
  "response_times": {
    "p50": 120,
    "p95": 350,
    "p99": 500
  },
  "error_rates": {
    "1h": 0.01,
    "24h": 0.005
  },
  "resource_usage": {
    "cpu": 45.2,
    "memory": 72.8,
    "disk": 65.3
  }
}
```

## Error Handling

All endpoints follow a consistent error response format:

```json
{
  "error": {
    "code": 400,
    "message": "Invalid request parameters",
    "type": "validation_error",
    "details": {
      "field": "query",
      "issue": "Required field missing"
    }
  }
}
```

Common error codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## Rate Limiting

All endpoints are subject to rate limiting as described in the authentication documentation. Rate limit headers are included in all responses:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704153660
```

## Pagination

List endpoints support pagination using cursor-based pagination:

```http
GET /endpoint?cursor=abc123&limit=20
```

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "def456",
    "has_more": true
  }
}
```

## Filtering and Sorting

List endpoints support filtering and sorting:

```http
GET /endpoint?filter[field]=value&sort=-created_at
```

- Use `filter[field]=value` for filtering
- Use `sort=field` for ascending sort
- Use `sort=-field` for descending sort

## Request/Response Formats

- All POST/PUT requests should use JSON format
- File uploads should use multipart/form-data
- All responses are in JSON format
- Dates are in ISO 8601 format
- Timestamps are in UTC 