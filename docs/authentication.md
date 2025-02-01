# Authentication Documentation

## Overview

The AudioKit AI Platform uses JWT (JSON Web Token) based authentication for all API endpoints. This document outlines the authentication flow, token management, rate limiting, and security best practices.

## Authentication Flow

### 1. Token Structure

JWT tokens contain three sections:
- Header: Algorithm and token type
- Payload: Claims (data)
- Signature: Verification signature

Example token structure:
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "artist_id",
    "exp": 1735689600,
    "iat": 1704153600,
    "scope": ["read", "write"]
  }
}
```

### 2. Token Management

#### Obtaining Tokens
```http
POST /auth/token
Content-Type: application/json

{
  "email": "artist@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAi...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### Using Tokens
Include the token in the Authorization header:
```http
GET /api/v1/brain/query
Authorization: Bearer eyJ0eXAi...
```

#### Token Expiration
- Access tokens expire after 1 hour
- Refresh tokens expire after 7 days
- Use the refresh token endpoint to get a new access token

### 3. Rate Limiting

The API implements tiered rate limiting:

| Endpoint Type | Rate Limit | Window |
|--------------|------------|--------|
| Standard     | 100        | 1 min  |
| AI Generation| 20         | 1 min  |
| Batch Ops    | 5          | 1 min  |

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1704153660
```

### 4. Error Handling

#### Authentication Errors
```json
{
  "error": {
    "code": 401,
    "message": "Invalid or expired token",
    "type": "authentication_error"
  }
}
```

#### Rate Limit Errors
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded",
    "type": "rate_limit_error",
    "retry_after": 30
  }
}
```

## Security Best Practices

### 1. Token Storage
- Never store tokens in localStorage
- Use secure HTTP-only cookies
- Clear tokens on logout

### 2. CORS Configuration
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.audiokit.ai"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. Security Headers
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

### 4. Error Handling Best Practices
- Use generic error messages
- Log detailed errors server-side
- Never expose internal error details
- Implement proper rate limiting
- Use secure session management

## Integration Examples

### Python Client
```python
import httpx

async def get_token(email: str, password: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.audiokit.ai/auth/token",
            json={"email": email, "password": password}
        )
        return response.json()

async def query_knowledge_base(token: str, query: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.audiokit.ai/brain/query",
            headers={"Authorization": f"Bearer {token}"},
            json={"query": query}
        )
        return response.json()
```

### TypeScript Client
```typescript
interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
}

async function getToken(email: string, password: string): Promise<TokenResponse> {
  const response = await fetch('https://api.audiokit.ai/auth/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  });
  return response.json();
}

async function queryKnowledgeBase(token: string, query: string): Promise<any> {
  const response = await fetch('https://api.audiokit.ai/brain/query', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ query })
  });
  return response.json();
}
```

## Troubleshooting

### Common Issues

1. Invalid Token
```json
{
  "error": {
    "code": 401,
    "message": "Invalid token format"
  }
}
```
Solution: Ensure token is properly formatted and not expired

2. Rate Limit Exceeded
```json
{
  "error": {
    "code": 429,
    "message": "Rate limit exceeded"
  }
}
```
Solution: Implement exponential backoff and respect rate limits

3. Missing Permissions
```json
{
  "error": {
    "code": 403,
    "message": "Insufficient permissions"
  }
}
```
Solution: Check token scopes and user permissions

### Support

For authentication issues:
1. Check token expiration
2. Verify correct token format
3. Confirm proper header usage
4. Review rate limit status
5. Contact support with request ID 