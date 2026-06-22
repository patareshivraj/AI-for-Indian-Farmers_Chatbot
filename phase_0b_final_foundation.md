# Farm360 AI Copilot - Phase 0B: Final Foundation

This document serves as the final sign-off for Phase 0 (Architecture & Discovery). It locks down the structural decisions required before beginning any engineering work in Phase 1 (Context Layer).

---

## 1. Context Object Specification

This JSON structure is the strict contract between the API Gateway and the AI Agent Layer. Every request to the Copilot MUST inject this context before prompt evaluation.

### Farmer Context
```json
{
  "user": {
    "user_id": 101,
    "role": "FARMER",
    "name": "Rajesh Kumar",
    "state": "Maharashtra",
    "district": "Pune",
    "language": "mr"
  },
  "farm_metrics": {
    "total_land_area_acres": 12.5,
    "active_crops": ["Wheat", "Sugarcane"],
    "land_ids": [402, 403]
  },
  "permissions": {
    "can_access_global_knowledge": true,
    "can_access_market_prices": true
  }
}
```

### Consultant Context
```json
{
  "user": {
    "user_id": 205,
    "role": "CONSULTANT",
    "name": "Dr. Sharma",
    "state": "Maharashtra",
    "district": "Pune",
    "language": "en"
  },
  "assignments": {
    "authorized_farmer_ids": [101, 145, 189]
  },
  "permissions": {
    "can_access_global_knowledge": true,
    "can_access_market_prices": true
  }
}
```

### Admin Context
```json
{
  "user": {
    "user_id": 1,
    "role": "ADMIN",
    "name": "System Admin",
    "language": "en"
  },
  "permissions": {
    "can_access_all_aggregates": true
  }
}
```

---

## 2. Router Specification

The semantic router steers the user query to the correct Agent pipeline based on intent.

| Intent Category | Target Route | Allowed Tools |
| :--- | :--- | :--- |
| **My Farm / My Crops** <br>*(e.g., "What crops am I growing?", "Show my inventory")* | **Database Agent** | `get_my_active_crops`, `get_my_inventory`, `get_my_land_records` |
| **Market Data** <br>*(e.g., "What is the price of Onion in Pune?")* | **Database Agent** | `get_market_prices` |
| **Schemes & Subsidies** <br>*(e.g., "Are there subsidies for tractors?")* | **Scheme Agent** | `search_schemes` |
| **Agronomy & Knowledge** <br>*(e.g., "How to treat yellow leaves on tomatoes?")* | **Knowledge Agent**| `get_knowledge_base` |
| **Weather** <br>*(e.g., "Is it going to rain tomorrow?")* | **Knowledge Agent**| `get_weather_advisory` |

---

## 3. Role Execution Flows

These execution graphs define the strict sequence of operations for each role.

### Farmer Journey
```text
User Query
   ↓
Middleware: Fetch user_master, farmer_profile, farmer_crop_details
   ↓
Build Context Object
   ↓
Semantic Router
   ↓
Agent (DB / Scheme / Knowledge)
   ↓
Execute Tool (Bounded by Context user_id)
   ↓
Grounded Response
```

### Consultant Journey
```text
User Query (e.g., "Show me Rajesh's crops")
   ↓
Middleware: Fetch user_master, farmer_consultant_requests
   ↓
Build Context Object (Inject authorized_farmer_ids)
   ↓
Authorization Check: Is target Farmer ID in authorized_farmer_ids?
   ├─ No → Terminate (Access Denied)
   └─ Yes → Proceed
   ↓
Agent (DB / Scheme / Knowledge)
   ↓
Execute Tool (Bounded by target Farmer ID)
   ↓
Grounded Response
```

### Admin Journey
```text
User Query
   ↓
Middleware: Fetch user_master (Role=ADMIN)
   ↓
Build Context Object
   ↓
Admin Analytics Router
   ↓
Execute Global Aggregate Tool
   ↓
Response
```

---

## 4. Crop Analysis Architectural Decision

**Finding:** The `crop_analysis` table currently lacks a `farmer_id` or `user_id` foreign key. It is isolated from the role-based access structure.

**Decision for Phase 1:**
*   Treat `crop_analysis` as **Global Knowledge / RAG Context**.
*   We cannot safely answer questions like *"Show my latest crop analysis"* because the database does not link analyses to specific farmers.
*   **Action Required:** Raise ticket with backend engineering team to clarify linkage. Until then, the Copilot will only use `crop_analysis` as an anonymous source of agricultural insight.

---
**Status:** PHASE 0B COMPLETE. READY FOR PHASE 1.
