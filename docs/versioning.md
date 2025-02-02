# API Versioning Guide

## Overview

The AudioKit AI Platform follows semantic versioning principles for its API. This document outlines our versioning strategy, breaking changes policy, deprecation process, and provides migration guides for transitioning between versions.

## Versioning Strategy

### 1. URL-Based Versioning

All API endpoints are versioned in the URL path:

```
https://api.audiokit.ai/v1/brain/query
https://api.audiokit.ai/v2/brain/query
```

### 2. Version Format

We follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR** version (v1, v2): Breaking changes
- **MINOR** version (1.1, 1.2): New features, backwards-compatible
- **PATCH** version (1.1.1, 1.1.2): Bug fixes, backwards-compatible

### 3. Version Lifecycle

1. **Active**: Fully supported, receives all updates
2. **Maintenance**: Security fixes only
3. **Deprecated**: No updates, scheduled for removal
4. **Sunset**: Removed from service

Example lifecycle:

```
v1: Maintenance (Security updates only)
v2: Active (Current stable version)
v3: Beta (Next major version)
```

## Breaking Changes Policy

### 1. What Constitutes a Breaking Change

- Removing or renaming endpoints
- Changing request/response formats
- Modifying authentication methods
- Changing error response formats
- Removing fields from responses
- Changing field types
- Modifying rate limits

### 2. Non-Breaking Changes

- Adding new endpoints
- Adding optional request parameters
- Adding response fields
- Adding new error types
- Increasing rate limits
- Adding new authentication methods

### 3. Version Support

- Major versions supported for minimum 12 months
- At least 2 major versions supported simultaneously
- 6 months notice before version sunset
- Security fixes for all supported versions

## Deprecation Process

### 1. Deprecation Notice

```http
GET /v1/brain/query
Deprecation: true
Sunset: Sat, 31 Dec 2024 23:59:59 GMT
Link: <https://api.audiokit.ai/v2/brain/query>; rel="successor-version"
Warning: 299 - "This endpoint will be removed on 2024-12-31"
```

### 2. Documentation Updates

```typescript
/**
 * @deprecated Since version 2.0.0
 * Use `/v2/brain/query` instead
 * Will be removed on 2024-12-31
 */
async function queryKnowledgeBase(query: string): Promise<Response> {
  console.warn('Deprecated: Use v2 endpoint instead');
  return makeRequest('/v1/brain/query', { query });
}
```

### 3. Deprecation Timeline

1. **Announcement Phase** (Month 0)
   - Deprecation notice added
   - Documentation updated
   - Migration guide published

2. **Warning Phase** (Months 1-5)
   - Warning headers included
   - Monitoring of usage
   - Direct communication with active users

3. **Sunset Phase** (Month 6)
   - Endpoint removed
   - Clear error message directing to new version

## Migration Guides

### 1. v1 to v2 Migration

#### Authentication Changes

```typescript
// v1: Token in query parameter
const v1Request = await fetch('/v1/brain/query?token=xyz');

// v2: Bearer token in header
const v2Request = await fetch('/v2/brain/query', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### Request Format Changes

```typescript
// v1: Flat query structure
const v1Query = {
  query: "artist achievements",
  limit: 5
};

// v2: Structured query parameters
const v2Query = {
  query: {
    text: "artist achievements",
    doc_types: ["news", "social"],
    options: {
      limit: 5,
      use_cache: true
    }
  }
};
```

#### Response Format Changes

```typescript
// v1 Response
{
  "results": ["..."],
  "count": 5
}

// v2 Response
{
  "data": {
    "results": ["..."],
    "metadata": {
      "count": 5,
      "query_time_ms": 120,
      "cache_hit": true
    }
  }
}
```

### 2. Version Compatibility

#### Python Client

```python
from audiokit import Client

# v1 Client
client_v1 = Client(version="v1")
result = await client_v1.query_knowledge_base(query="test")

# v2 Client
client_v2 = Client(version="v2")
result = await client_v2.query_knowledge_base(
    query={
        "text": "test",
        "options": {"use_cache": True}
    }
)
```

#### TypeScript Client

```typescript
import { AudioKitClient } from '@audiokit/client';

// v1 Client
const clientV1 = new AudioKitClient({ version: 'v1' });
const result = await clientV1.queryKnowledgeBase('test');

// v2 Client
const clientV2 = new AudioKitClient({ version: 'v2' });
const result = await clientV2.queryKnowledgeBase({
  text: 'test',
  options: { useCache: true }
});
```

## Best Practices

### 1. Version Selection

```typescript
class AudioKitClient {
  constructor(options: ClientOptions) {
    this.version = options.version ?? getLatestStableVersion();
    this.baseUrl = `https://api.audiokit.ai/${this.version}`;
  }

  private getLatestStableVersion(): string {
    // Check for stored preference
    const storedVersion = localStorage.getItem('preferred_api_version');
    if (storedVersion && !isDeprecated(storedVersion)) {
      return storedVersion;
    }
    return 'v2'; // Current stable version
  }

  private isDeprecated(version: string): boolean {
    const deprecatedVersions = ['v1'];
    return deprecatedVersions.includes(version);
  }
}
```

### 2. Version Fallback

```typescript
async function makeRequest(endpoint: string, options: RequestOptions) {
  try {
    return await makeV2Request(endpoint, options);
  } catch (error) {
    if (error.code === 'VERSION_NOT_SUPPORTED') {
      console.warn('Falling back to v1 API');
      return await makeV1Request(endpoint, options);
    }
    throw error;
  }
}
```

### 3. Version Headers

```typescript
const headers = {
  'Accept-Version': 'v2',
  'X-API-Version': 'v2',
  'User-Agent': 'AudioKit-Client/2.0.0'
};
```

## Testing Version Compatibility

### 1. Version Tests

```typescript
describe('API Version Compatibility', () => {
  test('handles v1 requests', async () => {
    const clientV1 = new AudioKitClient({ version: 'v1' });
    const response = await clientV1.query('test');
    expect(response).toHaveProperty('results');
  });

  test('handles v2 requests', async () => {
    const clientV2 = new AudioKitClient({ version: 'v2' });
    const response = await clientV2.query({
      text: 'test',
      options: { useCache: true }
    });
    expect(response).toHaveProperty('data.results');
  });
});
```

### 2. Migration Tests

```typescript
describe('Version Migration', () => {
  test('v1 to v2 response mapping', () => {
    const v1Response = {
      results: ['result1'],
      count: 1
    };

    const v2Response = mapV1ToV2Response(v1Response);
    expect(v2Response).toEqual({
      data: {
        results: ['result1'],
        metadata: {
          count: 1
        }
      }
    });
  });
});
```
