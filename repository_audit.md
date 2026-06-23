# Repository Audit
- UserRepository: Uses SQLAlchemy `_execute` without mock data.
- FarmerRepository: Uses real `text()` SQL execution against `farmer_profile`, `farmer_land_records`, and `farmer_crop_details`.
- ConsultantRepository: Standard SQL queries without hardcoded dictionaries.
- SchemeRepository: Standard SQL queries.

Verdict: No `MockSession`, `FakeRepository`, or `Hardcoded JSON` found in standard production paths.
