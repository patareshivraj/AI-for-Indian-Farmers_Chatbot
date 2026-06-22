# Farm360 AI Copilot - Phase 1: Context Layer Design

This document outlines the architectural blueprint and engineering design for the Context Layer of the Farm360 AI Copilot. The Context Layer acts as the immutable, deterministic, and secure gateway between the application state (MySQL Database) and the AI Agents. 

No LLMs, prompts, or LangGraph components are defined in this phase. The sole purpose is to securely retrieve database state, validate user roles, sanitize data, and construct a strongly typed `Context Object`.

---

## Deliverable 1: Project Structure

The Context Layer will be structured as a modular, scalable Python package. This structure separates data access (repositories) from business logic (resolvers/builders) and data contracts (models).

```text
app/
├── core/
│   ├── config.py             # Environment and DB configuration
│   ├── exceptions.py         # Custom domain exceptions (e.g., UserNotFoundError, AccessDeniedError)
│   └── security.py           # PII masking and sanitization utilities
├── context/
│   ├── models.py             # Pydantic data contracts (Context Objects)
│   ├── builder.py            # ContextBuilder class orchestrating the flow
│   ├── role_resolver.py      # RoleResolver class determining user identity
│   └── permissions.py        # PermissionResolver enforcing feature flags
└── repositories/
    ├── base.py               # Database connection management
    ├── user_repo.py          # Queries against `user_master` and `role`
    ├── farmer_repo.py        # Queries against `farmer_profile`, `farmer_land_records`, `farmer_crop_details`
    └── consultant_repo.py    # Queries against `farmer_consultant_requests`
```

### Justification:
*   **Separation of Concerns:** Repositories only handle SQL. Resolvers only handle logic. Models only handle validation.
*   **Testability:** Database interactions can be easily mocked at the repository layer.
*   **Security:** Masking logic is centralized in `core/security.py` ensuring no developer accidentally passes raw PAN/Aadhaar data.

---

## Deliverable 2: Context Models

The data contracts are defined strictly using Pydantic. No `Any` types are allowed. This ensures that the AI Agents always receive a predictable, validated structure.

```python
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class RoleEnum(str, Enum):
    FARMER = "FARMER"
    CONSULTANT = "CONSULTANT"
    ADMIN = "ADMIN"

class BaseUser(BaseModel):
    user_id: int
    role: RoleEnum
    name: str
    state: Optional[str]
    district: Optional[str]
    language: str = "en"
    # Note: mobile_number, email, password are deliberately excluded

class Permissions(BaseModel):
    can_access_global_knowledge: bool = True
    can_access_market_prices: bool = True
    can_access_all_aggregates: bool = False

class FarmMetrics(BaseModel):
    total_land_area_acres: float = 0.0
    active_crops: List[str] = Field(default_factory=list)
    land_ids: List[int] = Field(default_factory=list)

class FarmerContext(BaseModel):
    user: BaseUser
    farm_metrics: FarmMetrics
    permissions: Permissions

class ConsultantAssignments(BaseModel):
    authorized_farmer_ids: List[int] = Field(default_factory=list)

class ConsultantContext(BaseModel):
    user: BaseUser
    assignments: ConsultantAssignments
    permissions: Permissions

class AdminContext(BaseModel):
    user: BaseUser
    permissions: Permissions
```

### Justification:
*   **BaseUser:** Contains ONLY safe demographic data.
*   **RoleEnum:** Enforces strict role definitions matching `user_master`.
*   **Polymorphic Contexts:** Different roles return entirely different schema objects, making it impossible for a Farmer to accidentally receive an `authorized_farmer_ids` array.

---

## Deliverable 3: Role Resolver Design

**Class:** `RoleResolver`
**Responsibility:** Takes a raw `user_id`, queries the `UserRepository`, and returns a safe `RoleEnum` along with the user's basic record.

### Interface Design
```python
class RoleResolver:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def resolve(self, user_id: int) -> tuple[RoleEnum, dict]:
        """
        Retrieves user record and maps database role ID to standard RoleEnum.
        Raises UserNotFoundError if the user does not exist.
        Raises InvalidRoleError if the role ID is unrecognized.
        """
        pass
```

### Requirements:
*   Must explicitly map database `role_id` (e.g., `2` for Farmer) to `RoleEnum.FARMER`.
*   Must fail securely (deny access by default if mapping fails).

---

## Deliverable 4: Context Builder Design

**Class:** `ContextBuilder`
**Responsibility:** The primary entry point. Orchestrates the flow from ID to validated Context Object.

### Data Flow
1. **Input:** `user_id`
2. **Resolve Role:** `RoleResolver.resolve(user_id)`
3. **Fetch Role-Specific Data:**
    *   If FARMER: `FarmerRepository.get_farm_metrics(user_id)`
    *   If CONSULTANT: `ConsultantRepository.get_authorized_farmers(user_id)`
4. **Resolve Permissions:** `PermissionResolver.get_permissions(role)`
5. **Assemble & Validate:** Pass dictionaries into Pydantic models.
6. **Return:** Validated `FarmerContext`, `ConsultantContext`, or `AdminContext`.

### Interface Design
```python
class ContextBuilder:
    def __init__(self, role_resolver, farmer_repo, consultant_repo, perm_resolver):
        # Dependencies injected for testability
        pass

    def build_context(self, user_id: int) -> BaseModel:
        """
        Returns FarmerContext, ConsultantContext, or AdminContext.
        Implements short-lived caching (e.g., Redis or in-memory TTL) for performance.
        """
        pass
```

---

## Deliverable 5: Permission Resolver Design

**Class:** `PermissionResolver`
**Responsibility:** Centralizes access control logic. Determines boolean feature flags based on the user's role.

### Interface Design
```python
class PermissionResolver:
    def get_permissions(self, role: RoleEnum) -> Permissions:
        """
        Generates deterministic permission flags based solely on RoleEnum.
        No hardcoded User IDs allowed.
        """
        pass
```

---

## Deliverable 6: Repository Layer Design

Repositories are the **ONLY** files permitted to contain SQL or database driver code. They must return basic Python dictionaries or Data Classes (not Pydantic Context models).

### 1. `UserRepository`
*   **Methods:** `get_user_by_id(user_id: int) -> dict`
*   **Tables:** `user_master` joined with `state` and `district`.

### 2. `FarmerRepository`
*   **Methods:** `get_farm_metrics(farmer_id: int) -> dict`
*   **Tables:** `farmer_profile` (for `total_land_area`), `farmer_land_records` (for `land_ids`), `farmer_crop_details` (for `active_crops` where `is_crop_planted = 1`).

### 3. `ConsultantRepository`
*   **Methods:** `get_authorized_farmers(consultant_id: int) -> list[int]`
*   **Tables:** `farmer_consultant_requests` (where `status = 'ACCEPTED'`).

---

## Deliverable 7: Security & PII Design

### Field-by-Field Policy
| Table | Field | Classification | Policy | Implementation |
| :--- | :--- | :--- | :--- | :--- |
| `user_master` | `password` | **CRITICAL** | Never Expose | Excluded from `SELECT` in `UserRepository` |
| `user_master` | `email` | **PII** | Never Expose | Excluded from `SELECT` in `UserRepository` |
| `user_master` | `mobile_number` | **PII** | Mask | Replace middle digits (e.g., `98XXXXX123`) in `security.py` |
| `farmer_land_records` | `adhar_no` | **CRITICAL PII** | Never Expose | Excluded from `SELECT` in `FarmerRepository` |
| `farmer_land_records` | `pan_no` | **CRITICAL PII** | Never Expose | Excluded from `SELECT` in `FarmerRepository` |
| `farmer_land_records` | `property_uid`| **SENSITIVE** | Mask/Internal | Use integer `id` for internal routing, do not expose UID string to AI |

**Validation Strategy:** The Context Builder relies on Pydantic `BaseUser`. Because `password`, `adhar_no`, and `pan_no` are entirely missing from the Pydantic definition, any accidental inclusion by a repository will be silently ignored (or throw a validation error depending on `extra="forbid"` configuration), creating an impenetrable PII firewall.

---

## Deliverable 8: Testing Strategy

Testing must mock the repositories to validate the Context Builder logic without a live database.

**Unit Test Cases:**
1.  **Farmer Success:** Given a valid farmer ID, asserts `FarmerContext` is returned with populated `active_crops`.
2.  **Consultant Success:** Given a valid consultant ID, asserts `ConsultantContext` is returned with an array of `authorized_farmer_ids`.
3.  **Admin Success:** Given a valid admin ID, asserts `AdminContext` is returned with `can_access_all_aggregates = True`.
4.  **Missing User:** Given a non-existent ID, asserts `UserNotFoundError` is raised.
5.  **Invalid Role:** Given an ID linked to an unknown role ID in DB, asserts `InvalidRoleError` is raised.
6.  **Missing Profile:** Given a valid Farmer ID but missing `farmer_profile` record, asserts graceful fallback (e.g., area defaults to 0) rather than application crash.
7.  **Consultant with No Assignments:** Asserts `ConsultantContext` returns an empty `authorized_farmer_ids` list without failing.
8.  **Database Failure:** Asserts that an underlying DB connection failure raises a standard `ContextLayerSystemError`.

---

## Deliverable 9: Phase 1 Acceptance Criteria

Before transitioning to Phase 1A (Implementation), the following criteria must be met and agreed upon:

1.  **Role Resolution:** The system can accurately and deterministically map any `user_id` to `FARMER`, `CONSULTANT`, or `ADMIN`.
2.  **Context Construction:** The system outputs the exact Pydantic `FarmerContext`, `ConsultantContext`, or `AdminContext` objects.
3.  **Permissions Enforced:** A Consultant cannot ever be assigned `FarmerContext` features; permissions are strictly isolated by role.
4.  **PII Filtered:** A security review confirms that `password`, `adhar_no`, and `pan_no` are completely stripped from repository outputs and absent from Pydantic models.
5.  **Validation Coverage:** Pydantic models strictly type-check inputs, preventing strings where ints are expected, or None where required.
6.  **No AI Leakage:** The layer executes 100% deterministically using Python code with zero LLM/Prompt inference involved.
