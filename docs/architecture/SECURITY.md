# Farm360 AI Copilot: Security Architecture

## 1. Zero-Trust Access Model
Every request processed by the Farm360 AI Copilot is assumed untrusted. The system enforces a strict Role-Based Access Control (RBAC) model at the deterministic execution layer, fundamentally neutralizing LLM-based role escalation attacks.

### 1.1 Role Definitions
- **FARMER**: Restricted to accessing only data associated with their own `user_id`. Cannot access aggregate analytics.
- **CONSULTANT**: Restricted to accessing data for farmers assigned to their `district_id` or `taluka_id`.
- **ADMIN**: Permitted to access cross-tenant analytical tools but restricted from initiating state-mutating actions (e.g., executing transactions).

## 2. Protection Against LLM Attacks

### 2.1 Prompt Injection Protection
- **No Direct Execution**: The LLM is strictly positioned at the end of the data pipeline. It formats data already fetched by deterministic tools. It has zero capability to trigger backend logic.
- **Deterministic Routing**: The user's query is resolved to an Intent via a classical regex/embedding matcher, completely bypassing LLM decision-making for tool selection.

### 2.2 Memory Poisoning Mitigation
- **Entity Storage, Not Chat Logs**: The system stores structural metadata (e.g., `crop="soybean"`) instead of raw conversational context. The LLM cannot access past prompts, ensuring malicious payloads injected in turn 1 cannot influence turn 2.

### 2.3 Cross-Tenant Data Leaks
- **ToolExecutionGuard**: Before any tool executes, the `Guard` validates the target resource ID against the `UserContext`. Even if a user successfully bypasses the intent layer (e.g., "Get profile for user 99"), the Guard explicitly blocks execution if `99` is outside their ownership bounds.

## 3. PII Scrubbing
All logs, metrics, and memory dumps pass through the `ObservabilityMiddleware`, which applies RegEx filters to obfuscate:
- Aadhaar Numbers
- PAN Cards
- Passwords
- JWT Tokens
- Personal Phone Numbers

## 4. API Secrets
- All keys (e.g., `DATABASE_URL`, `GROQ_API_KEY`) are managed strictly via `.env` files ingested by `pydantic_settings`. 
- Secrets are explicitly `.gitignore`'d.

## 5. Audit Logging
Every tool execution attempt (successful or denied) is logged in `app/access/audit.py`, containing:
- `user_id`
- `role`
- `tool_name`
- `target_resource`
- `timestamp`
- `allowed (True/False)`
