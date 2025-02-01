# API Examples

## cURL Examples

### Authentication

```bash
# Get access token
curl -X POST https://api.audiokit.ai/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "artist@example.com",
    "password": "secure_password"
  }'

# Refresh token
curl -X POST https://api.audiokit.ai/auth/refresh \
  -H "Authorization: Bearer <refresh_token>"
```

### Knowledge Base

```bash
# Query knowledge base
curl -X POST https://api.audiokit.ai/brain/query \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the artist'\''s recent achievements?",
    "doc_types": ["news", "social_media"],
    "top_k": 5
  }'

# Upload document
curl -X POST https://api.audiokit.ai/brain/documents \
  -H "Authorization: Bearer <token>" \
  -F "metadata={\"doc_type\":\"news\",\"source\":\"music_blog\"}" \
  -F "file=@article.txt"

# Delete documents
curl -X DELETE https://api.audiokit.ai/brain/documents \
  -H "Authorization: Bearer <token>" \
  -d '{
    "doc_types": ["news"],
    "source": "music_blog"
  }'
```

### Analytics

```bash
# Get performance overview
curl -X GET https://api.audiokit.ai/analytics/overview \
  -H "Authorization: Bearer <token>"

# Get growth metrics
curl -X GET https://api.audiokit.ai/analytics/growth \
  -H "Authorization: Bearer <token>" \
  -G \
  -d "timeframe=30d" \
  -d "metrics[]=followers" \
  -d "metrics[]=streams"
```

## Python Examples

### Client Implementation

```python
from typing import Dict, Any, Optional, List
import httpx
from pydantic import BaseModel

class AudioKitClient:
    def __init__(
        self,
        token: str,
        base_url: str = "https://api.audiokit.ai"
    ):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            },
            timeout=30.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def query_knowledge_base(
        self,
        query: str,
        doc_types: Optional[List[str]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        response = await self.client.post(
            "/brain/query",
            json={
                "query": query,
                "doc_types": doc_types,
                "top_k": top_k
            }
        )
        response.raise_for_status()
        return response.json()
    
    async def upload_document(
        self,
        file_path: str,
        doc_type: str,
        source: str
    ) -> Dict[str, str]:
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "metadata": {
                    "doc_type": doc_type,
                    "source": source
                }
            }
            response = await self.client.post(
                "/brain/documents",
                files=files,
                data=data
            )
            response.raise_for_status()
            return response.json()
    
    async def get_analytics(
        self,
        timeframe: str = "30d",
        metrics: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        params = {"timeframe": timeframe}
        if metrics:
            params["metrics"] = metrics
        
        response = await self.client.get(
            "/analytics/growth",
            params=params
        )
        response.raise_for_status()
        return response.json()
```

### Common Operations

```python
async def main():
    async with AudioKitClient(token="your_token") as client:
        # Query knowledge base
        result = await client.query_knowledge_base(
            query="What are the recent achievements?",
            doc_types=["news", "social_media"]
        )
        print(f"Query result: {result}")
        
        # Upload document
        doc_id = await client.upload_document(
            file_path="article.txt",
            doc_type="news",
            source="music_blog"
        )
        print(f"Uploaded document: {doc_id}")
        
        # Get analytics
        analytics = await client.get_analytics(
            timeframe="30d",
            metrics=["followers", "streams"]
        )
        print(f"Analytics: {analytics}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## TypeScript Examples

### Client Implementation

```typescript
interface QueryParams {
  query: string;
  docTypes?: string[];
  topK?: number;
}

interface AnalyticsParams {
  timeframe?: string;
  metrics?: string[];
}

class AudioKitClient {
  private baseUrl: string;
  private token: string;

  constructor(token: string, baseUrl = 'https://api.audiokit.ai') {
    this.baseUrl = baseUrl;
    this.token = token;
  }

  private async request<T>(
    method: string,
    path: string,
    data?: any
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: {
        'Authorization': `Bearer ${this.token}`,
        'Content-Type': 'application/json'
      },
      body: data ? JSON.stringify(data) : undefined
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  async queryKnowledgeBase(params: QueryParams) {
    return this.request('POST', '/brain/query', params);
  }

  async uploadDocument(file: File, metadata: any) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));

    const response = await fetch(`${this.baseUrl}/brain/documents`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`
      },
      body: formData
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  }

  async getAnalytics(params: AnalyticsParams) {
    const queryParams = new URLSearchParams();
    if (params.timeframe) {
      queryParams.set('timeframe', params.timeframe);
    }
    if (params.metrics) {
      params.metrics.forEach(metric => {
        queryParams.append('metrics[]', metric);
      });
    }

    return this.request(
      'GET',
      `/analytics/growth?${queryParams.toString()}`
    );
  }
}
```

### React Hooks

```typescript
import { useState, useCallback } from 'react';
import { AudioKitClient } from './client';

export function useKnowledgeBase(client: AudioKitClient) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const query = useCallback(async (params: QueryParams) => {
    setLoading(true);
    setError(null);
    try {
      const result = await client.queryKnowledgeBase(params);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [client]);

  return { query, loading, error };
}

export function useAnalytics(client: AudioKitClient) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const getGrowth = useCallback(async (params: AnalyticsParams) => {
    setLoading(true);
    setError(null);
    try {
      const result = await client.getAnalytics(params);
      return result;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [client]);

  return { getGrowth, loading, error };
}
```

### Svelte Stores

```typescript
import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';
import { AudioKitClient } from './client';

interface KnowledgeBaseStore {
  loading: boolean;
  error: Error | null;
  data: any | null;
}

export function createKnowledgeBaseStore(client: AudioKitClient) {
  const store: Writable<KnowledgeBaseStore> = writable({
    loading: false,
    error: null,
    data: null
  });

  async function query(params: QueryParams) {
    store.update(s => ({ ...s, loading: true, error: null }));
    try {
      const result = await client.queryKnowledgeBase(params);
      store.update(s => ({
        ...s,
        loading: false,
        data: result
      }));
      return result;
    } catch (err) {
      store.update(s => ({
        ...s,
        loading: false,
        error: err as Error
      }));
      throw err;
    }
  }

  return {
    subscribe: store.subscribe,
    query
  };
}
```

## Postman Collection

```json
{
  "info": {
    "name": "AudioKit AI API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Get Token",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Content-Type",
                "value": "application/json"
              }
            ],
            "url": "{{baseUrl}}/auth/token",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"email\": \"{{email}}\",\n  \"password\": \"{{password}}\"\n}"
            }
          }
        }
      ]
    },
    {
      "name": "Knowledge Base",
      "item": [
        {
          "name": "Query",
          "request": {
            "method": "POST",
            "header": [
              {
                "key": "Authorization",
                "value": "Bearer {{token}}"
              }
            ],
            "url": "{{baseUrl}}/brain/query",
            "body": {
              "mode": "raw",
              "raw": "{\n  \"query\": \"{{query}}\",\n  \"doc_types\": [\"news\"],\n  \"top_k\": 5\n}"
            }
          }
        }
      ]
    }
  ],
  "event": [
    {
      "listen": "prerequest",
      "script": {
        "type": "text/javascript",
        "exec": [
          "// Add pre-request scripts here"
        ]
      }
    },
    {
      "listen": "test",
      "script": {
        "type": "text/javascript",
        "exec": [
          "pm.test(\"Status code is 200\", function () {",
          "    pm.response.to.have.status(200);",
          "});"
        ]
      }
    }
  ],
  "variable": [
    {
      "key": "baseUrl",
      "value": "https://api.audiokit.ai"
    }
  ]
}
```

### Environment Setup

```json
{
  "id": "env_audiokit",
  "name": "AudioKit API Environment",
  "values": [
    {
      "key": "baseUrl",
      "value": "https://api.audiokit.ai",
      "enabled": true
    },
    {
      "key": "email",
      "value": "your_email",
      "enabled": true
    },
    {
      "key": "password",
      "value": "your_password",
      "enabled": true
    },
    {
      "key": "token",
      "value": "your_token",
      "enabled": true
    }
  ]
} 