# Farm360 AI Copilot: Engineering Handoff

## 1. System Status
The Farm360 AI Copilot has formally completed its AI Engineering lifecycle and is **LIVE**. All mock stubs, dummy data, and simulated APIs have been replaced with live production connections (MySQL Backend & Groq LLM API). 

## 2. Who Should Read This?
- **Backend Engineers:** To understand how to add new data sources or database tools.
- **Product Managers:** To understand the constraints and limits of the Copilot.
- **DevOps/SRE:** To understand the required environment variables and observability stacks.

## 3. How to Extend the System

### 3.1 Adding a New Tool
1. **Repository:** Add your raw SQL or REST call to the appropriate repository in `app/repositories/`.
2. **Intent Layer:** Add a new `Intent` enum in `app/router/intents.py`.
3. **Execution Engine:** Register the capability in `AgentResolver` and create an Agent class that calls your repository.
4. **RBAC Guard:** Ensure the tool is explicitly allowed for the correct roles in `app/access/permissions.py`.

### 3.2 Updating the Reasoning Workflows
If a user request requires multiple steps (e.g., fetching a profile *then* checking scheme rules), add a composite mapping in `app/reasoning/planner.py` -> `COMPOSITE_TEMPLATES`. Do not expect the LLM to figure this out dynamically.

## 4. Debugging Failures
- **LLM Generates Hallucinations?** Check the raw data passed from the `ExecutionEngine`. If the JSON has the hallucinated fact, the bug is in the DB/Repository. If the JSON does not have it, the LLM prompt in `generator.py` needs stricter grounding instructions.
- **Access Denied Logs?** Check the `ToolExecutionGuard`. Usually, this means the user is trying to access `user_id` data they do not own, or the `Intent` mapped to an Admin tool incorrectly.
- **"I don't understand" Responses?** The `QueryRouter` failed to find a matching regex/semantic pattern. Add the user's phrasing to the training file for that intent.

## 5. Next Steps for Product Team
- Deploy to the staging environment for internal QA.
- Connect to the production React Native or Web frontend via the API Gateway.
- Run a 100-user Pilot, specifically measuring edge-cases in regional languages (Marathi/Hindi).
- Monitor `unknown` intent logs daily to capture missing capabilities.
