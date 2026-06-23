# Farm360 AI Copilot: API Contract

## Core Endpoints

### 1. Execute AI Query
**POST** `/api/v1/copilot/chat`

Processes a natural language query and returns an actionable AI response grounded strictly in database facts.

#### Headers
- `Authorization`: Bearer `<JWT_TOKEN>` (Mandatory)
- `X-Correlation-ID`: `<UUID>` (Optional, generated if missing)

#### Request Payload
```json
{
  "query": "What are the latest schemes for soybean in Maharashtra?",
  "session_id": "sess_abc123", 
  "location": {
    "lat": 18.5204,
    "lon": 73.8567
  }
}
```

#### Success Response (200 OK)
```json
{
  "success": true,
  "request_id": "req_f842a9b1",
  "intent_resolved": "SCHEME_QUERY",
  "response": "The Maharashtra government has introduced the Krishi Vikas Scheme for soybean. The subsidy is 50% for high-yield seeds.",
  "metadata": {
    "tools_executed": ["SEARCH_SCHEMES"],
    "execution_time_ms": 345,
    "language": "en"
  }
}
```

#### Error Response (403 Forbidden)
```json
{
  "success": false,
  "request_id": "req_x912b4z",
  "error_code": "PERMISSION_DENIED",
  "message": "You do not have access to view administrative statistics."
}
```

---

### 2. System Readiness
**GET** `/api/v1/observability/ready`

Used by Kubernetes/DevOps to verify if the AI Engine has successfully booted and connected to all dependencies.

#### Success Response (200 OK)
```json
{
  "status": "UP",
  "components": {
    "database": "UP",
    "memory_store": "UP",
    "llm_provider": "UP",
    "reasoning_engine": "UP",
    "tool_registry": "UP"
  }
}
```

---

### 3. Production Dashboard Stats
**GET** `/api/v1/observability/dashboard`

Used to view real-time platform metrics.

#### Success Response (200 OK)
```json
{
  "traffic": {
    "total_requests": 14050,
    "error_rate_percentage": 0.2
  },
  "performance": {
    "latency_p50_ms": 145.2,
    "latency_p95_ms": 380.5,
    "latency_p99_ms": 610.1
  },
  "ai_metrics": {
    "MARKET_QUERY": 5400,
    "WEATHER_QUERY": 8000
  },
  "security": {
    "denied_requests": 12,
    "blocked_pii": 0
  }
}
```

## Session Handling & Rate Limits
- **Sessions**: The `session_id` string controls contextual memory lookup. A session expires automatically after 30 minutes of inactivity.
- **Rate Limits**: 
  - Farmers: 20 requests per minute
  - Consultants: 50 requests per minute
  - Admins: 100 requests per minute
