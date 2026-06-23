# Farm360 AI Copilot - Phase 0 Implementation Plan

## Goal Description
Perform Phase 0 Discovery, Architecture Validation, and Data Understanding for the Farm360 AI Copilot. This phase establishes the foundation for the context layer, access control, and database interactions before any code is built.

## Open Questions

> [!WARNING]
> **Missing Database Schema:** The prompt mentions that the "Farm360 MySQL database" and "Database export/schema" are available, but the `d:/FARM360 AI_CHATBOT` workspace directory is currently empty. 
> 
> **Question:** Would you like to provide the MySQL schema export (e.g., a `.sql` file) for me to analyze, or should I proceed by designing a comprehensive logical schema based on the entities mentioned in your prompt (Farmers, Consultants, Crops, Land, Schemes, Consultations, etc.) and perform the analysis on that proposed schema?

## Proposed Approach (Assuming Inferred Schema)

If you would like me to proceed without an existing SQL dump, I will infer and design the following database architecture for the analysis:

1. **User Management & Roles**
   - `users` (Admin, Farmer, Consultant)
   - `farmer_profiles` (Context: District, State, Language)
   - `consultant_profiles`

2. **Agricultural Data (Farmer Owned)**
   - `land_records` (Land ownership context)
   - `crop_records` (Crop inventory, Crop analysis)
   - `inventory` (Equipment, seeds, fertilizers)

3. **Consultation & Sustainability**
   - `consultations` (Mapping Consultants to Farmers)
   - `sustainability_reports`

4. **External/Knowledge Data**
   - `schemes` (Government schemes, PM Kisan, subsidies)
   - `agri_knowledge` (Pest management, irrigation, soil health)

### Deliverables to be Generated
Once approved or once the schema is provided, I will create a comprehensive markdown artifact (`phase_0_discovery.md`) containing:
1. **Schema Overview:** Tables, keys, and relationships.
2. **Table Classification:** Categorizing tables (Farmer Data, Admin Data, Market Data, etc.).
3. **Role Access Matrix:** Strict boundaries for Farmer, Consultant, and Admin.
4. **Context Layer Design:** Which tables to query to build the prompt context.
5. **AI Relevant Data Map:** Which tables feed the Database Agent, Scheme Agent, and Knowledge Agent.
6. **Security Analysis & Risks:** Identifying hallucination, data leak, and permission risks.
7. **Recommended AI Architecture:** High-level interaction flow for the Copilot.

## User Review Required
Please confirm if I should proceed with the inferred schema, or if you will be uploading the database schema file to the workspace.
