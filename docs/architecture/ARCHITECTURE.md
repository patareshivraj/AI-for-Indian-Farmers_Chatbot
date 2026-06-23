# Farm360 AI Copilot: Architecture Overview

## 1. System Overview
Farm360 AI Copilot is an enterprise-grade, deterministic AI platform designed for the Indian agricultural sector. It shifts away from unpredictable "agentic swarms" and brittle conversational memory, instead utilizing a strict pipeline where the Large Language Model (LLM) is strictly a formatter and synthesizer—never a decision-maker or database operator.

The architecture ensures that every query passes through a sequence of deterministic validations, role-based access checks, and explicit tool mappings before execution.

## 2. Core Data Flow
The system processes every incoming user request linearly:

1. **Query Ingestion**: Raw text is received and tagged with a unique request ID.
2. **Context Layer**: A structured `UserContext` object is built mapping the user's ID, Role (FARMER, CONSULTANT, ADMIN), State, District, and Language.
3. **Permission Layer**: Role-Based Access Control (RBAC) verifies if the user is authorized to perform generic actions.
4. **Query Router (Deterministic)**: The text is mapped to a strict semantic `Intent` (e.g., `MARKET_QUERY`, `SCHEME_ELIGIBILITY_QUERY`) using predefined patterns and embeddings.
5. **Tool Registry**: The extracted `Intent` maps 1:1 with an explicit `ToolName`.
6. **Reasoning Engine (DAG)**: If the intent requires multiple steps (composite), a Directed Acyclic Graph (DAG) sequences the tools, passing variables linearly between them.
7. **Execution Engine**: The system executes the mapped tools against the backend APIs/Database.
8. **Response Layer**: The raw execution data (JSON) is passed to the LLM along with strict grounding instructions.
9. **LLM Formatter**: The LLM formats the final response strictly using the provided execution data in the user's native language.

## 3. Security Model & RBAC
- **Strict Isolation**: Farmers can only access their own profile data. Consultants can access data for farmers assigned to their district. Admins have broad analytical access.
- **Fail-Closed**: Any failure in the Context Layer or Permission Layer results in immediate denial of service.
- **PII Scrubbing**: An `ObservabilityMiddleware` strips Aadhaar, PAN, passwords, and JWTs from logs and memory streams.

## 4. Memory Model
We explicitly reject "Conversation History" concatenation (which leads to prompt injection and hallucinations). Instead, we use **Operational Memory**:
- Only strict semantic entities (e.g., `crop="soybean"`, `district="Pune"`) are extracted and persisted in a structured schema.
- Follow-up queries inherit these missing entities deterministically (e.g., "What about Nashik?" inherits `crop="soybean"`).

## 5. Reasoning Model
Instead of relying on LLM-driven loops (like ReAct or LangGraph), reasoning is handled via static templates and DAG validation:
- Composite queries map to a static plan (e.g., `[GET_FARMER_PROFILE] -> [EVALUATE_SCHEME_RULES]`).
- A `PlanValidator` ensures there are no circular dependencies and limits plans to a maximum of 5 deterministic execution steps.

## 6. Observability Design
- **Tracing**: Every layer executes within an OpenTelemetry-compatible span.
- **Metrics**: A Prometheus-ready collector tracks p50/p95 latency and AI intent accuracy.
- **Logging**: JSON structured logging enforces strict PII sanitization before writing to output.
