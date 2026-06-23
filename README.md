# Farm360 AI Copilot

## Secure Multi-Role Agricultural Intelligence Platform

Farm360 AI Copilot is a secure, context-aware agricultural intelligence platform that assists Farmers, Consultants, and Administrators through deterministic reasoning, role-based access control, operational memory, and grounded AI responses powered by real agricultural data.

**Engineering Philosophy:** Deterministic execution, role-aware reasoning, zero-trust data access, and grounded responses built on real agricultural data.

---

## 2. Table of Contents

1. [System Architecture](#3-system-architecture)
2. [Role Access Model](#4-role-access-model)
3. [Pipeline Overview](#5-pipeline-overview)
4. [Core Component Registry](#6-core-component-registry)
5. [Tool Registry](#7-tool-registry)
6. [Schema Registry](#8-schema-registry)
7. [Project Structure](#9-project-structure)
8. [Setup and Configuration](#10-setup-and-configuration)
9. [Environment Variables](#11-environment-variables)
10. [Running the System](#12-running-the-system)
11. [API Reference](#13-api-reference)
12. [Evaluation Framework](#14-evaluation-framework)
13. [Pilot Readiness Results](#15-pilot-readiness-results)
14. [Design Philosophy](#16-design-philosophy)
15. [Safety Mechanisms](#17-safety-mechanisms)
16. [Known Limitations](#18-known-limitations)
17. [Remaining Work and Roadmap](#19-remaining-work-and-roadmap)
18. [Not Planned](#20-not-planned-and-why)
19. [Technology Stack](#21-technology-stack)
20. [License](#22-license)

---

## 3. System Architecture

The Farm360 AI Copilot strictly separates "thinking" from "doing". The LLM acts solely as a formatting and synthesis layer at the very end of the data lifecycle. Tool selection, permission enforcement, and reasoning are entirely deterministic.

### High-Level Pipeline

```mermaid
flowchart TD
    A[Raw Query] --> B[Authentication & Context]
    B --> C[Permission Guard]
    C --> D[Intent Router]
    D --> E[Memory Enrichment]
    E --> F[Reasoning DAG Planner]
    F --> G[Execution Engine]
    G --> H[MySQL DB / APIs]
    H --> I[Response Payload]
    I --> J[Groq LLM Formatter]
    J --> K[Final Output]
```

### Security Architecture

```mermaid
flowchart TD
    subgraph Zero-Trust Boundary
    Req[Incoming Request] --> Auth[JWT Validator]
    Auth --> Ctx[Context Builder]
    Ctx --> RBAC{Role Bound?}
    RBAC -- Yes --> TG[Tool Execution Guard]
    RBAC -- No --> Block1[Drop Request]
    TG -- Ownership Valid --> Exec[Backend Data]
    TG -- Ownership Invalid --> Block2[Audit & Deny]
    end
    Exec --> PII[PII Scrubber Middleware]
    PII --> LLM[LLM Formatting]
```

### Data Flow

```mermaid
sequenceDiagram
    participant User
    participant Router
    participant Engine
    participant DB
    participant LLM
    User->>Router: "What crops are active?"
    Router->>Router: Match Intent: GET_CROPS
    Router->>Engine: ExecutionPlan(GET_CROPS)
    Engine->>DB: SELECT crop_name FROM farmer_crop_details
    DB-->>Engine: JSON[{crop: 'Cotton'}]
    Engine->>LLM: ResponsePayload(JSON)
    LLM-->>User: "You are growing Cotton."
```

### Reasoning Flow

```mermaid
flowchart TD
    Query[Multi-Step Request] --> Router[Extract Intents]
    Router --> Plan[Plan Generator]
    Plan --> DAG[DAG Validator]
    DAG --> Step1[Execute Tool 1]
    Step1 --> Vars[Store Variables]
    Vars --> Step2[Execute Tool 2]
    Step2 --> Merge[Synthesize Results]
```

**Key Guarantee:** The LLM is structurally isolated from data access logic; it formats data that has already successfully passed Role-Based Access Control and deterministic database execution.

---

## 4. Role Access Model

### Farmer
- **Can access:** Own profile, own land, own crops, own inventory, own schemes.
- **Cannot access:** Data of any other farmer or platform aggregates.

### Consultant
- **Can access:** Data belonging strictly to assigned farmers within their designated territory.
- **Cannot access:** Unassigned farmers or global aggregate metrics.

### Admin
- **Can access:** Platform analytics, administrative endpoints, and aggregated metrics.
- **Cannot access:** State-mutating capabilities without secondary execution boundaries.

### Access Matrix

| Resource Boundary | Farmer | Consultant | Admin |
|---|---|---|---|
| Own Context | Yes | Yes | Yes |
| Assigned Context | No | Yes | N/A |
| Global Aggregate | No | No | Yes |

---

## 5. Pipeline Overview

| Phase | Module | Purpose | Input | Output |
|---|---|---|---|---|
| 1 | Context Builder | Establish operational state | Request JWT / User ID | `UserContext` |
| 2 | Permission Layer | Enforce authorization | `UserContext` | Allowed Tools |
| 3 | Query Router | Map text to semantic intent | Raw string | `RoutingDecision` |
| 4 | Memory Manager | Inject structural history | `RoutingDecision` | Enriched Intent |
| 5 | Reasoning Planner | Build execution DAG | `RoutingDecision` | `ExecutionPlan` |
| 6 | Execution Engine | Fire backend requests | `ExecutionPlan` | `ExecutionResult` |
| 7 | Response Formatter | Synthesize natural prose | `ExecutionResult` | Final String |

---

## 6. Core Component Registry

| Component | File | Responsibility | LLM Usage | Deterministic Logic |
|---|---|---|---|---|
| ContextBuilder | `app/context/builder.py` | Hydrates user profile | No | Yes |
| PermissionResolver | `app/access/resolver.py` | Computes RBAC allowances | No | Yes |
| QueryRouter | `app/router/router.py` | Intent classification | No | Yes |
| ReasoningPlanner | `app/reasoning/planner.py` | DAG step generation | No | Yes |
| ExecutionEngine | `app/execution/executor.py` | Executes physical tools | No | Yes |
| MemoryManager | `app/memory/manager.py` | Operational entity state | No | Yes |
| ResponseGenerator | `app/llm/generator.py` | Formats output via Groq | Yes | No |
| ToolExecutionGuard | `app/access/guard.py` | Zero-trust execution validation | No | Yes |
| Farm360Orchestrator | `app/execution/orchestrator.py` | Master pipeline controller | No | Yes |

---

## 7. Tool Registry

| Tool | Category | Purpose | Access Restrictions |
|---|---|---|---|
| `GetMyProfileTool` | Database | Retrieve user profile metadata | Farmer, Consultant, Admin |
| `GetMyLandRecordsTool` | Database | Retrieve land acreage | Farmer, Consultant, Admin |
| `GetMyActiveCropsTool` | Database | Retrieve planted crops | Farmer, Consultant, Admin |
| `GetMyInventoryTool` | Database | Retrieve stored harvest | Farmer, Consultant |
| `GetWeatherTool` | API | Retrieve live weather | Farmer, Consultant, Admin |
| `GetMarketPricesTool` | API | Retrieve mandi pricing | Farmer, Consultant, Admin |
| `GetDiseaseInfoTool` | Knowledge | Plant pathology retrieval | Global |
| `SchemeSearchTool` | Database | Eligibility verification | Global |

---

## 8. Schema Registry

**Context**
- `UserContext`
- `FarmerContext`
- `ConsultantContext`
- `AdminContext`

**Execution**
- `ToolResult`
- `ExecutionPlan`
- `ExecutionResult`
- `ExecutionTrace`

**Reasoning**
- `ReasoningResult`
- `RoutingDecision`

**Memory**
- `ConversationState`
- `TrackedEntities`

**Response**
- `ResponsePayload`

**Security**
- `SecurityAuditReport`
- `ReadinessReport`

---

## 9. Project Structure

```text
app/
├── access/         # RBAC, Guards, Auditing
├── context/        # Hydration and State Management
├── core/           # Configuration, Database Engine, Middlewares
├── execution/      # Tool Execution and Pipeline Orchestration
├── llm/            # Groq API Integration and Prompting
├── memory/         # Operational State Tracking
├── reasoning/      # DAG Construction and Validation
├── repositories/   # SQLAlchemy Database Access
├── response/       # Output Formatting Schemas
├── router/         # Semantic Intent Extraction
├── benchmark/      # Red-Teaming and Load Testing Scripts
└── observability/  # Metrics, Tracing, PII Sanitization
docs/               # Architectural Specifications
tests/              # E2E and Unit Verification
verify_infrastructure.py  # Validation Probes
```

---

## 10. Setup and Configuration

```bash
# 1. Clone repository
git clone https://github.com/patareshivraj/AI-for-Indian-Farmers_Chatbot.git

# 2. Initialize environment
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure .env
cp .env.example .env
```

---

## 11. Environment Variables

```env
DATABASE_URL=mysql+pymysql://user:password@host:3306/farm360
GROQ_API_KEY=gsk_...
LOG_LEVEL=INFO
CACHE_TTL=3600
```

---

## 12. Running the System

**Option A: Development**
```bash
python run.py
```

**Option B: API Server**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Option C: Evaluation**
```bash
pytest tests/
```

**Option D: Security Audit**
```bash
python verify_infrastructure.py
```

**Option E: Benchmark Suite**
```bash
python app/benchmark/run.py
```

---

## 13. API Reference

### `POST /chat`
Execute a deterministic query.
**Request JSON**
```json
{
  "user_id": 4,
  "query": "What active crops do I have?"
}
```
**Response JSON**
```json
{
  "success": true,
  "intent": "GET_CROPS",
  "data": { ... },
  "response": "You currently have 4 acres of Cotton planted."
}
```

### Error Codes
- `401 Unauthorized`: JWT Invalid.
- `403 Forbidden`: `ToolExecutionGuard` intercepted cross-tenant access.
- `422 Unprocessable Entity`: Schema malformed.
- `500 Internal Server Error`: Pipeline exception.

---

## 14. Evaluation Framework

The system utilizes an internal benchmarking tool (`app/benchmark`) to evaluate core AI metrics without external dependencies.
- **Security Evaluation**: Adversarial injection runs targeting the LLM Formatter to ensure zero extraction of backend APIs.
- **Reasoning Evaluation**: DAG complexity stress tests checking multi-hop tool execution limits.
- **Memory Evaluation**: State inheritance tests verifying variable passthrough (e.g., matching missing subjects across turns).
- **Performance Evaluation**: End-to-end tracing capturing P50/P95 latencies for Groq formatting.

**Scorecard output example:**
```json
{
  "total_runs": 1000,
  "hallucination_rate": 0.0,
  "permission_violations": 0
}
```

---

## 15. Pilot Readiness Results

Derived from Phase 9.6 Large Scale Benchmarking:

- **Intent Accuracy:** 100.0%
- **Tool Accuracy:** 100.0%
- **Permission Violations:** 0
- **PII Leaks:** 0
- **Hallucination Rate:** 0.0%
- **Pilot Status:** APPROVED

---

## 16. Design Philosophy

- **Deterministic Execution Over Agentic Guessing**: The LLM is unpredictable by design. Placing it in charge of routing and looping introduces unacceptable latency and error rates. The execution path must be hardcoded based on semantic intent.
- **LLMs Never Touch Data Sources**: To prevent prompt injection from executing SQL or REST calls, the LLM is restricted to reading outputs from internal systems that have already executed securely.
- **Memory Stores Context, Not Conversations**: Sending a full chat transcript to an LLM wastes tokens and increases the risk of injection payload delivery. We store explicit operational parameters (e.g. `{"crop": "cotton"}`) instead.
- **Security Before Intelligence**: The `ToolExecutionGuard` validates permissions independently of what the "brain" thinks the user wants to do.
- **Tools Execute, Models Explain**: Repositories pull raw JSON. The LLM translates JSON to natural language prose.

---

## 17. Safety Mechanisms

| Mechanism | Layer | Prevents |
|---|---|---|
| `ToolExecutionGuard` | Execution | Cross-tenant data unauthorized access |
| `ObservabilityMiddleware` | Output | Exposure of Aadhaar/PAN/PII to LLMs/Logs |
| DAG Depth Limiter | Reasoning | Infinite execution loops in composite queries |
| Intent Regex Router | Ingestion | Prompt injection causing unauthorized tool mapping |

---

## 18. Known Limitations

| Limitation | Root Cause | Impact | Mitigation |
|---|---|---|---|
| Out-of-Domain Failure | Strict regex/embedding boundaries for intents | Copilot cannot answer general knowledge queries | Monitor `UNKNOWN` intents to expand tool coverage |
| High Context Latency | Sequential DB operations before Groq call | Responses may take >1 second | Implement `CACHE_TTL` on aggregate metadata requests |
| Static DAGs | `COMPOSITE_TEMPLATES` is hardcoded | Novel multi-step queries will fail | Analyze complex user behaviors to map new static graphs |

---

## 19. Remaining Work and Roadmap

- **Priority 1**: Pilot Deployment & Telemetry Collection. Ensure metrics collector correctly pushes to Grafana. (Effort: 2 Days)
- **Priority 2**: Expansion of Scheme Eligibility Engine. Currently maps static constraints; requires dynamic mapping against new government API endpoints. (Effort: 1 Week)
- **Priority 3**: Edge-case Hindi/Marathi translation benchmarking. Ensure context extraction works perfectly against phonetic nuances. (Effort: 1 Week)

---

## 20. Not Planned (and Why)

- **Agent Swarms**: Unpredictable execution order and high latency make them unsuitable for real-time transactional farmer queries.
- **AutoGPT / Autonomous Actions**: Granting autonomous loop controls to the LLM risks unintended mutations on the underlying Django schemas.
- **Direct Text-to-SQL**: Exposes the database to direct prompt injection attacks and requires complex schema obfuscation.
- **Self-Modifying Prompts**: Eliminates traceability and breaks deterministic reproducibility.

---

## 21. Technology Stack

| Component | Technology |
|---|---|
| Core Language | Python 3.11+ |
| Framework | FastAPI |
| Database | MySQL 8.0.40 |
| ORM | SQLAlchemy |
| Inference Engine | Groq API |
| Model | `llama-3.3-70b-versatile` |
| Serialization | Pydantic V2 |
| Testing | Pytest |

---

## 22. License

MIT
