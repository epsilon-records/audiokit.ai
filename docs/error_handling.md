# Error Handling Documentation

## Overview

The AudioKit AI Platform implements a standardized error handling system across all endpoints. This document outlines error response formats, common error codes, handling strategies, and best practices for dealing with errors in different programming languages.

## Error Response Format

All API errors follow a consistent JSON format:

```json
{
  "error": {
    "code": 400,
    "message": "Invalid request parameters",
    "type": "validation_error",
    "details": {
      "field": "query",
      "issue": "Required field missing"
    },
    "request_id": "req_abc123",
    "documentation_url": "https://docs.audiokit.ai/errors#validation_error"
  }
}
```

### Fields Explanation

- `code`: HTTP status code
- `message`: Human-readable error description
- `type`: Machine-readable error type
- `details`: Additional error context (optional)
- `request_id`: Unique identifier for the request
- `documentation_url`: Link to relevant documentation

## Error Types

### 1. Authentication Errors (401)

```json
{
  "error": {
    "code": 401,
    "type": "authentication_error",
    "message": "Invalid or expired token"
  }
}
```

Common authentication errors:
- `token_expired`: JWT token has expired
- `invalid_token`: Malformed or invalid token
- `missing_token`: No authentication token provided
- `insufficient_scope`: Token lacks required permissions

### 2. Authorization Errors (403)

```json
{
  "error": {
    "code": 403,
    "type": "authorization_error",
    "message": "Insufficient permissions for resource"
  }
}
```

Common authorization errors:
- `insufficient_permissions`: User lacks required permissions
- `resource_forbidden`: Access to resource not allowed
- `account_suspended`: User account is suspended

### 3. Validation Errors (400)

```json
{
  "error": {
    "code": 400,
    "type": "validation_error",
    "message": "Invalid request parameters",
    "details": {
      "fields": {
        "email": "Invalid email format",
        "age": "Must be a positive integer"
      }
    }
  }
}
```

Common validation errors:
- `invalid_parameters`: Request parameters are invalid
- `missing_required_field`: Required field is missing
- `invalid_format`: Field format is incorrect
- `value_out_of_range`: Value exceeds allowed range

### 4. Rate Limit Errors (429)

```json
{
  "error": {
    "code": 429,
    "type": "rate_limit_error",
    "message": "Rate limit exceeded",
    "details": {
      "retry_after": 30,
      "limit": 100,
      "remaining": 0,
      "reset_at": "2024-02-15T10:00:00Z"
    }
  }
}
```

### 5. Server Errors (500, 502, 503, 504)

```json
{
  "error": {
    "code": 500,
    "type": "server_error",
    "message": "Internal server error",
    "request_id": "req_xyz789"
  }
}
```

## Error Handling Strategies

### 1. Python Implementation

```python
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel

class APIError(Exception):
    def __init__(
        self,
        message: str,
        code: int,
        type: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ):
        self.message = message
        self.code = code
        self.type = type
        self.details = details
        self.request_id = request_id
        super().__init__(self.message)

class ErrorHandler:
    @staticmethod
    async def handle_request(
        client: httpx.AsyncClient,
        method: str,
        url: str,
        **kwargs
    ) -> Dict[str, Any]:
        try:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_data = e.response.json().get("error", {})
            raise APIError(
                message=error_data.get("message", "Unknown error"),
                code=e.response.status_code,
                type=error_data.get("type", "unknown_error"),
                details=error_data.get("details"),
                request_id=error_data.get("request_id")
            )
        except httpx.RequestError as e:
            raise APIError(
                message=str(e),
                code=500,
                type="network_error"
            )

# Usage Example
async def safe_api_call():
    try:
        result = await ErrorHandler.handle_request(
            client,
            "POST",
            "/brain/query",
            json={"query": "test"}
        )
        return result
    except APIError as e:
        if e.code == 429:
            # Handle rate limiting
            retry_after = e.details.get("retry_after", 30)
            await asyncio.sleep(retry_after)
            return await safe_api_call()
        elif e.code == 401:
            # Handle authentication error
            await refresh_token()
            return await safe_api_call()
        else:
            # Log error and re-raise
            logger.error(
                f"API error: {e.message}",
                extra={
                    "code": e.code,
                    "type": e.type,
                    "request_id": e.request_id
                }
            )
            raise
```

### 2. TypeScript Implementation

```typescript
interface ErrorDetails {
  [key: string]: any;
}

interface APIErrorResponse {
  error: {
    code: number;
    message: string;
    type: string;
    details?: ErrorDetails;
    request_id?: string;
  };
}

class APIError extends Error {
  constructor(
    public code: number,
    public type: string,
    message: string,
    public details?: ErrorDetails,
    public requestId?: string
  ) {
    super(message);
    this.name = 'APIError';
  }
}

class ErrorHandler {
  static async handleRequest<T>(
    method: string,
    url: string,
    options?: RequestInit
  ): Promise<T> {
    try {
      const response = await fetch(url, {
        method,
        ...options,
      });

      if (!response.ok) {
        const errorData: APIErrorResponse = await response.json();
        throw new APIError(
          errorData.error.code,
          errorData.error.type,
          errorData.error.message,
          errorData.error.details,
          errorData.error.request_id
        );
      }

      return response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError(
        500,
        'network_error',
        'Network request failed',
        { original_error: error.message }
      );
    }
  }
}

// React Hook Example
function useAPIRequest<T>() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<APIError | null>(null);

  const execute = async (
    method: string,
    url: string,
    options?: RequestInit
  ): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await ErrorHandler.handleRequest<T>(
        method,
        url,
        options
      );
      return result;
    } catch (err) {
      if (err instanceof APIError) {
        setError(err);
        if (err.code === 401) {
          // Handle authentication error
          await refreshToken();
          return execute(method, url, options);
        }
        if (err.code === 429) {
          // Handle rate limiting
          const retryAfter = err.details?.retry_after ?? 30;
          await new Promise(resolve => 
            setTimeout(resolve, retryAfter * 1000)
          );
          return execute(method, url, options);
        }
      }
      return null;
    } finally {
      setLoading(false);
    }
  };

  return { execute, loading, error };
}
```

### 3. Svelte Store Implementation

```typescript
import { writable } from 'svelte/store';

interface ErrorState {
  loading: boolean;
  error: APIError | null;
}

function createErrorStore() {
  const { subscribe, set, update } = writable<ErrorState>({
    loading: false,
    error: null
  });

  return {
    subscribe,
    execute: async <T>(
      method: string,
      url: string,
      options?: RequestInit
    ): Promise<T | null> => {
      update(s => ({ ...s, loading: true, error: null }));

      try {
        const result = await ErrorHandler.handleRequest<T>(
          method,
          url,
          options
        );
        return result;
      } catch (err) {
        if (err instanceof APIError) {
          update(s => ({ ...s, error: err }));
        }
        return null;
      } finally {
        update(s => ({ ...s, loading: false }));
      }
    }
  };
}
```

## Best Practices

### 1. Error Logging

```typescript
function logError(error: APIError) {
  console.error({
    message: error.message,
    code: error.code,
    type: error.type,
    request_id: error.requestId,
    timestamp: new Date().toISOString(),
    details: error.details
  });
}
```

### 2. Retry Strategies

```typescript
async function retryWithExponentialBackoff<T>(
  operation: () => Promise<T>,
  maxRetries: number = 3,
  baseDelay: number = 1000
): Promise<T> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      return await operation();
    } catch (error) {
      if (
        error instanceof APIError &&
        error.code === 429 &&
        attempt < maxRetries - 1
      ) {
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
        continue;
      }
      throw error;
    }
  }
  throw new Error('Max retries exceeded');
}
```

### 3. Error Recovery

```typescript
class ErrorRecovery {
  static async handleAuthError(error: APIError): Promise<void> {
    if (error.code === 401) {
      await refreshToken();
    }
  }

  static async handleRateLimitError(error: APIError): Promise<void> {
    if (error.code === 429) {
      const retryAfter = error.details?.retry_after ?? 30;
      await new Promise(resolve => 
        setTimeout(resolve, retryAfter * 1000)
      );
    }
  }
}
```

### 4. User-Friendly Error Messages

```typescript
const errorMessages = {
  authentication_error: 'Please log in again to continue',
  rate_limit_error: 'Too many requests. Please try again later',
  validation_error: 'Please check your input and try again',
  server_error: 'Something went wrong. Please try again later'
};

function getUserFriendlyMessage(error: APIError): string {
  return errorMessages[error.type] ?? 'An unexpected error occurred';
}
```

## Testing Error Handling

### 1. Unit Tests

```typescript
describe('ErrorHandler', () => {
  test('handles rate limit error', async () => {
    const mockResponse = {
      ok: false,
      status: 429,
      json: async () => ({
        error: {
          code: 429,
          type: 'rate_limit_error',
          message: 'Rate limit exceeded',
          details: { retry_after: 30 }
        }
      })
    };

    global.fetch = jest.fn().mockResolvedValue(mockResponse);

    try {
      await ErrorHandler.handleRequest('GET', '/test');
    } catch (error) {
      expect(error).toBeInstanceOf(APIError);
      expect(error.code).toBe(429);
      expect(error.details.retry_after).toBe(30);
    }
  });
});
```

### 2. Integration Tests

```typescript
describe('API Integration', () => {
  test('retries on rate limit', async () => {
    const result = await retryWithExponentialBackoff(
      async () => {
        const response = await fetch('/api/test');
        if (!response.ok) {
          throw new APIError(
            429,
            'rate_limit_error',
            'Rate limit exceeded'
          );
        }
        return response.json();
      }
    );

    expect(result).toBeDefined();
  });
});
``` 