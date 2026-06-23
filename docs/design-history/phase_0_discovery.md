# Farm360 AI Copilot - Phase 0 Discovery & Architecture Validation

This document provides a comprehensive Phase 0 analysis based on the inferred architectural requirements and business rules for the Farm360 AI Copilot. It establishes the baseline data understanding, security boundaries, and systemic designs required before initiating Phase 1 development.

---

## 1. Schema Overview

Based on the required capabilities (farmers, consultants, crops, inventory, sustainability, schemes), the logical database structure is modeled below.

### Core Users & Profiles
- `users`: Core authentication table (`user_id`, `role_enum`, `hashed_password`, `created_at`).
- `farmer_profiles`: Context data (`farmer_id`, `user_id`, `district`, `state`, `language_preference`, `gender`, `farming_type`).
- `consultant_profiles`: Consultant data (`consultant_id`, `user_id`, `specialization`, `region`).

### Agricultural & Farm Operations
- `land_records`: Land ownership details (`land_id`, `farmer_id`, `parcel_name`, `area_acres`, `soil_type`).
- `crop_records`: Active and past crops (`crop_id`, `farmer_id`, `land_id`, `crop_name`, `season`, `expected_yield`, `status`).
- `crop_analysis`: Granular soil/crop health data (`analysis_id`, `crop_id`, `ph_level`, `moisture`, `nutrient_status`, `analysis_date`).
- `inventory`: Farm supplies (`inventory_id`, `farmer_id`, `item_type`, `quantity`, `unit`).
- `sustainability_metrics`: Environmental tracking (`metric_id`, `farmer_id`, `water_usage_liters`, `carbon_footprint_score`, `date_logged`).

### Consultation Layer
- `consultation_assignments`: Maps consultants to farmers (`assignment_id`, `consultant_id`, `farmer_id`, `status`).
- `consultation_records`: Meeting logs and advice (`record_id`, `assignment_id`, `notes`, `recommendations`, `date`).

### Knowledge & External Data
- `schemes`: Government and private schemes (`scheme_id`, `scheme_name`, `description`, `eligibility_criteria`, `state_applicability`, `target_demographic`).
- `agri_knowledge`: Curated agricultural best practices (`knowledge_id`, `topic`, `category`, `description`, `source_url`).

---

## 2. Table Classification

To streamline AI tool execution, tables are categorized by their logical domain:

*   **Farmer Data:** `farmer_profiles`, `land_records`, `crop_records`, `inventory`, `crop_analysis`, `sustainability_metrics`.
*   **Consultant Data:** `consultant_profiles`, `consultation_assignments`, `consultation_records`.
*   **Admin Data:** `users` (system logs, aggregate views of all operational tables).
*   **Scheme Data:** `schemes`.
*   **Knowledge Data:** `agri_knowledge`.
*   **Communication Data:** `consultation_records`.

---

## 3. Role Access Matrix

Strict data isolation is mandatory. The AI system must respect these boundaries dynamically.

| Table Category | Farmer Access | Consultant Access | Admin Access |
| :--- | :--- | :--- | :--- |
| **Farmer Data** | **Read/Write:** Own records ONLY (`WHERE farmer_id = me`). | **Read:** Assigned farmers ONLY. | **Read:** Aggregated/Anonymized analytics. |
| **Consultant Data** | **Read:** Own consultation records. | **Read/Write:** Own records & assigned farmers. | **Read:** Performance/Aggregate metrics. |
| **Scheme Data** | **Read:** All / filtered by eligibility. | **Read:** All / filtered by assigned farmer. | **Read/Write:** Manage schemes. |
| **Knowledge Data** | **Read:** Full access. | **Read:** Full access. | **Read/Write:** Manage knowledge base. |
| **Admin/User Auth** | **None.** | **None.** | **Read/Write:** Excludes plaintext secrets. |

---

## 4. Context Layer Design

Before the LLM processes any user prompt, the **Context Builder** middleware must silently fetch and inject the following baseline state into the AI's system prompt. This ensures personalized and grounded answers.

### For a Farmer Request:
1.  **Identity Context:** Fetch `user_id`, `role`, and `name`.
2.  **Profile Context:** Fetch `state`, `district`, `language_preference`, and `gender` (vital for scheme eligibility, e.g., "Women farmer schemes").
3.  **Operational Context:** Fetch an aggregate summary: `Total Land Area`, `Active Crops`, `Recent Crop Analysis Status`.
*Example Injection:* "You are talking to Rajesh, a Farmer in Maharashtra. He speaks Marathi. He currently grows Sugarcane on 5 acres."

### For a Consultant Request:
1.  **Identity Context:** Fetch `specialization` and `region`.
2.  **Assignment Context:** Fetch a list of actively assigned `farmer_ids` and their names. The AI must be instructed to *only* answer questions regarding these specific IDs.

---

## 5. AI-Relevant Data Map

The AI System relies on three primary capabilities. Here is how the database feeds them:

### Capability 1: Database Agent
*   **Purpose:** Answer operational questions (e.g., "What is my inventory?").
*   **Relevant Tables:** `land_records`, `crop_records`, `inventory`, `crop_analysis`, `sustainability_metrics`.
*   **Mechanism:** Text-to-SQL or bounded API tools with strict Row-Level Security (RLS) enforcement.

### Capability 2: Scheme Discovery Agent
*   **Purpose:** Recommend subsidies and loans.
*   **Relevant Tables:** `schemes` + `farmer_profiles` (for dynamic demographic matching).
*   **Mechanism:** Uses the existing scheme AI layer, enhanced by passing the `farmer_profile` context as search parameters (e.g., State=Punjab, Gender=Female).

### Capability 3: Agriculture Knowledge Agent
*   **Purpose:** Provide pest management and crop planning advice.
*   **Relevant Tables:** `agri_knowledge` + `crop_records`.
*   **Mechanism:** Uses `crop_records` from the context layer to proactively tailor advice (e.g., if a user asks "How do I fix yellow leaves?", the AI knows they grow Cotton and filters knowledge accordingly).

---

## 6. Security Analysis & Risks

> [!CAUTION]
> **Data Leakage Risk (Text-to-SQL):** 
> If the Database Agent uses raw Text-to-SQL, the LLM might generate queries like `SELECT * FROM crop_records` without the `WHERE farmer_id = 101` clause, leaking the entire database to the user.
> **Mitigation:** Never allow the LLM direct database access. Provide bounded API tools (e.g., `get_my_crops()`) where the backend API automatically infers the `farmer_id` from the secure JWT token, completely bypassing AI query generation for access control.

> [!WARNING]
> **Hallucination Risk (Agriculture Knowledge):**
> Farmers rely on precise data for chemical usage or pest control. Hallucinated dosages can destroy crops.
> **Mitigation:** Implement strict prompt grounding. The system prompt must state: *"Answer ONLY based on the provided retrieved knowledge base. If the exact dosage or chemical is not listed, you MUST say 'I do not have this information, please consult an expert.' Do not guess."*

> [!IMPORTANT]
> **Consultant Scope Creep:**
> A consultant might try to ask the AI about a farmer they are not assigned to.
> **Mitigation:** The AI middleware must intercept queries, extract the requested entity, and validate it against the `consultation_assignments` table before invoking the LLM.

---

## 7. Recommended Architecture

To achieve the requirements safely, the following architecture is recommended for the AI Layer:

1.  **API Gateway / Auth Middleware:** Receives the user request and validates the JWT. Extracts `user_id` and `role`.
2.  **Context Builder:** Quickly queries MySQL to build the user's localized context string (State, Crops, Assignments).
3.  **Semantic Router / Orchestrator:** Analyzes the prompt and routes it to one of three sub-agents:
    *   *Route A (Database):* Triggers bounded tools (e.g., `fetch_inventory_API()`) rather than SQL execution.
    *   *Route B (Schemes):* Calls the existing Scheme AI, passing the user context parameters.
    *   *Route C (Knowledge):* Uses RAG on the `agri_knowledge` repository.
4.  **Ensemble Engine:** Formats the retrieved data logically.
5.  **Grounded Generation:** Final LLM prompt enforces context, security constraints, and language preference to generate the final response.

---
*End of Phase 0 Analysis.*
