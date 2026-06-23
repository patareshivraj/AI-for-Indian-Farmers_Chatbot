# Farm360 AI Copilot - Phase 0B: Real Schema Intelligence Mapping

This document provides a definitive architectural mapping derived strictly from the provided `farm360.sql` schema dump. It contains zero assumed tables and serves as the literal foundation for Phase 1 API and AI tool generation.

---

## Task 1: Complete Table Inventory

### Django & Auth Tables (System / Non-AI)
*Excluded from AI tool registry.*
* `auth_group`, `auth_group_permissions`, `auth_permission`, `auth_user`, `auth_user_groups`, `auth_user_user_permissions`
* `django_admin_log`, `django_content_type`, `django_migrations`, `django_session`
* `password_reset_otp`, `ea_sync_log`, `role`

### Farmer Operations & Profile
| Table Name | Purpose | Keys & Foreign Keys | Important Columns | Role Owner | AI Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `user_master` | Core identity | PK: `user_id`, FK: `role_id`, `state_id`, `district_id` | `full_name`, `mobile_number`, `role_id` | User | High (Identity) |
| `farmer_profile` | Farmer metrics | PK: `id`, FK: `user_id` -> `user_master` | `preferred_language`, `total_land_area` | Farmer | High (Context) |
| `farmer_land_records` | Land assets | PK: `id`, FK: `farmer_id` | `area`, `survey_number`, `adhar_no`, `pan_no` | Farmer | High (DB Agent) |
| `land_boundaries` | GIS data | PK: `id`, FK: `farmer_id`, `land_id` | `geojson`, `calculated_area_acres` | Farmer | Low (UI Heavy) |
| `farmer_crop_details` | Current crops | PK: `id`, FK: `farmer_id`, `land_id` | `crop_name`, `harvesting_area`, `plantation_date` | Farmer | High (DB Agent) |
| `farmer_instock` | Inventory | PK: `id`, FK: `farmer_id` | `crop_name`, `instock_qty` | Farmer | High (DB Agent) |
| `export_crop_listings`| Marketplace | PK: `id`, FK: `farmer_id` | `crop_name`, `quantity`, `rate`, `status` | Farmer | High (DB Agent) |

### Consultant & Communication
| Table Name | Purpose | Keys & Foreign Keys | Important Columns | Role Owner | AI Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `farmer_consultant_requests`| Assignment | PK: `id`, FK: `farmer_id`, `consultant_id` | `status`, `request_message` | Both | High (Auth Routing)|
| `farmer_consultant_chat` | Messaging | PK: `id`, FK: `farmer_id`, `consultant_id` | `message_type`, `message` | Both | Low (UI Only) |

### AI & Crop Intelligence
| Table Name | Purpose | Keys & Foreign Keys | Important Columns | Role Owner | AI Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `crop_analysis` | Disease detection | PK: `id` (No FK to farmer!) | `crop_name`, `disease_name`, `health_score` | System | High (Context/KB) |
| `satellite_snapshot` | Satellite health | PK: `id`, FK: `farm_id` (*Missing parent*) | `ndvi`, `vegetation_health_score` | System | High (Context) |
| `weather_snapshots` | Weather history| PK: `id`, FK: `farmer_id`, `land_id` | `temperature`, `rainfall`, `weather_score` | System | High (Context) |

### Market & Schemes
| Table Name | Purpose | Keys & Foreign Keys | Important Columns | Role Owner | AI Relevance |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `schemes_master` | Gov Schemes | PK: `scheme_id` | `scheme_name`, `crop_name`, `benefit` | Admin | High (Scheme Agent)|
| `market_master` | Mandi locations | PK: `id` | `market_name`, `state`, `district` | Admin | Medium |
| `commodity_price` | Mandi prices | PK: `id`, FK: `market_id` | `commodity`, `modal_price`, `price_date` | Admin | High (DB Agent) |
| `market_prices` | Gen Market trend | PK: `id` | `crop`, `market`, `price_per_quintal` | Admin | High (DB Agent) |

### Knowledge Base Tables (Admin Managed, Public Read)
*   `agriculture_news` (`title`, `full_content`, `news_category`)
*   `crop_calendar` (`current_season`, `recommended_activity`)
*   `daily_farming_tips` (`tip_text`, `crop_name`)
*   `disease_awareness` (`disease_name`, `symptoms`, `treatment`)
*   `pest_awareness` (`pest_name`, `control_methods`)
*   `fertilizer_awareness` (`fertilizer_name`, `dosage_info`)
*   `soil_health_awareness` (`category`, `content`)
*   `weather_awareness` (`farming_impact`, `advisory`)
*   `educational_content`, `learning_videos`, `farming_quiz`

---

## Task 2: Relationship Map

> [!WARNING]
> **Schema Inconsistencies Found:**
> 1. `farmer_crop_details` defines `farmer_id` and `land_id` as `varchar(45)` but `user_master` and `farmer_land_records` use `int`/`bigint`. This requires type casting in joins.
> 2. `satellite_snapshot` contains a strict foreign key `FOREIGN KEY (farm_id) REFERENCES farm (id)`. **However, the `farm` table DOES NOT EXIST in the schema dump.**
> 3. `crop_analysis` lacks a `farmer_id` or `user_id` mapping. It is completely isolated.

**Actual Join Paths:**
*   `user_master.user_id` ➔ `farmer_profile.user_id`
*   `user_master.user_id` ➔ `farmer_land_records.farmer_id`
*   `user_master.user_id` ➔ `farmer_instock.farmer_id`
*   `user_master.user_id` ➔ `farmer_consultant_requests.farmer_id` AND `consultant_id`
*   `farmer_land_records.id` ➔ `land_boundaries.land_id`
*   `farmer_land_records.id` ➔ `weather_snapshots.land_id`
*   `market_master.id` ➔ `commodity_price.market_id`

---

## Task 3: Role Access Matrix

| Table Domain | Farmer | Consultant | Admin |
| :--- | :--- | :--- | :--- |
| **Personal Profile** (`farmer_profile`, `user_master`) | **Read/Write** (Self) | **Read** (Assigned) | **Read/Write** (All) |
| **Farm Assets** (`farmer_land_records`, `farmer_crop_details`, `farmer_instock`) | **Read/Write** (Self) | **Read** (Assigned) | **Read** (Aggregated) |
| **Consultation** (`farmer_consultant_requests`) | **Read/Write** (Self) | **Read/Write** (Self) | **Read** (System) |
| **Knowledge / Awareness** (All `*_awareness`, `_news`) | **Read** (All) | **Read** (All) | **Read/Write** (All) |
| **Schemes** (`schemes_master`) | **Read** (All) | **Read** (All) | **Read/Write** (All) |
| **Prices** (`commodity_price`, `market_prices`) | **Read** (All) | **Read** (All) | **Write** (Update) |

---

## Task 4: Context Layer Mapping

The following logic defines exactly what the API must fetch before calling the LLM.

### Farmer Context Payload
*   **Source:** `user_master`
    *   *Required:* `full_name`, `state_id`, `district_id` (joined with `state`/`district` tables).
*   **Source:** `farmer_profile`
    *   *Required:* `preferred_language`, `total_land_area`.
*   **Source:** `farmer_crop_details`
    *   *Required:* List of active `crop_name` and `plantation_date` (where `is_crop_planted = 1`).

### Consultant Context Payload
*   **Source:** `user_master`
    *   *Required:* `full_name`
*   **Source:** `farmer_consultant_requests`
    *   *Required:* Array of `farmer_id` where `status = 'ACCEPTED'`. *(The AI tool router MUST block queries for any ID not in this array).*

---

## Task 5: Tool Registry (Grounded in Actual Schema)

1.  **`get_my_land_records(user_id)`**
    *   *Tables:* `farmer_land_records`
    *   *Output:* `area`, `survey_number`, `gat_number`, `farm_name`.
    *   *Rules:* Strips `adhar_no` and `pan_no` before returning to LLM.
2.  **`get_my_active_crops(user_id)`**
    *   *Tables:* `farmer_crop_details`
    *   *Output:* `crop_name`, `harvesting_area`, `plantation_date`.
3.  **`get_my_inventory(user_id)`**
    *   *Tables:* `farmer_instock`, `export_crop_listings`
    *   *Output:* `crop_name`, `instock_qty`, `status`.
4.  **`search_schemes(crop_name, is_general)`**
    *   *Tables:* `schemes_master`
    *   *Output:* `scheme_name`, `benefit`, `apply_link`.
5.  **`get_knowledge_base(topic, category)`**
    *   *Tables:* Union of `disease_awareness`, `pest_awareness`, `fertilizer_awareness`, `soil_health_awareness`.
    *   *Output:* `symptoms`, `treatment`, `control_methods`, `dosage_info`.
6.  **`get_market_prices(crop_name)`**
    *   *Tables:* `market_prices`, `commodity_price` joined with `market_master`.
    *   *Output:* `market_name`, `modal_price`/`price_per_quintal`, `trend`.

---

## Task 6: Query Routing Map

| Example Question | Target Agent | Primary Tables Accessed |
| :--- | :--- | :--- |
| *"How much wheat do I have in stock?"* | **Database Agent** | `farmer_instock` |
| *"What is the survey number of my farm?"* | **Database Agent** | `farmer_land_records` |
| *"Is there a scheme for tractors?"* | **Scheme Agent** | `schemes_master` |
| *"What is the current mandi rate for onions?"*| **Database Agent** | `market_prices`, `commodity_price`|
| *"Leaves on my tomato crop are turning yellow."*| **Knowledge Agent**| `disease_awareness`, `pest_awareness`|
| *"When should I apply DAP fertilizer?"* | **Knowledge Agent**| `fertilizer_awareness`, `crop_calendar` |

---

## Task 7: Security Audit

> [!CAUTION]
> **CRITICAL PII EXPOSURE DETECTED IN SCHEMA**

**Table:** `user_master`
*   `password`: **NEVER EXPOSE.** Ensure backend API strips this before Context Layer building.
*   `mobile_number`: **MASK** (e.g., `XXXXXX1234`). Only expose if strictly requested by the owner.

**Table:** `farmer_land_records`
*   `adhar_no`: **NEVER EXPOSE.** A massive regulatory risk. Do not load this into the LLM context window.
*   `pan_no`: **NEVER EXPOSE.**
*   `property_uid` / `e_7_12_pdf`: **MASK/RESTRICT.** Provide only internal reference IDs to the LLM.

**Security Recommendations for Phase 1:**
1.  **LLM Tool Output Sanitization:** The API wrapper executing the SQL queries for the AI MUST select specific columns (e.g., `SELECT area, farm_name FROM farmer_land_records`). Never use `SELECT *`.
2.  **No Raw SQL Execution:** The database schema implies a highly structured environment. The LLM must not generate SQL. It must output JSON arguments mapped to strict Python/Node API tools.

---

## Task 8: AI-Relevant Data Map Categorization

*   **Farmer Context:** `farmer_profile`, `farmer_land_records`, `farmer_crop_details`, `farmer_instock`
*   **Consultant Context:** `farmer_consultant_requests`
*   **Admin Analytics:** None specifically optimized for AI in schema, rely on aggregates of farmer tables.
*   **Weather:** `weather_awareness`, `weather_snapshots`
*   **Market:** `market_master`, `commodity_price`, `market_prices`, `export_crop_listings`
*   **Schemes:** `schemes_master`
*   **Knowledge:** `agriculture_news`, `crop_calendar`, `daily_farming_tips`, `disease_awareness`, `educational_content`, `fertilizer_awareness`, `pest_awareness`, `soil_health_awareness`
*   **Communications:** `farmer_consultant_chat` (Currently unsafe for AI processing without PII filters).
*   **Crop Intelligence:** `crop_analysis`, `satellite_snapshot`.
