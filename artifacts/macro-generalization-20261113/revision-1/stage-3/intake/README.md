# Request intake and fixture mapping

No teammate request was provided. Empty forms are not authored requests. The schema records exposure rather than
manufacturing independence. See intake_requests.py for validation, exact-text preservation, cell matching and logs.
Each mapping needs case_ref, replaces_case_ref, skill_id, template_group, author_confirmed_group and fixture_overrides.
Only fixture fields may be overridden: kind, fault, world_configuration, expected_status, expected_dispatches.
Every mapping and field change is logged; request_text is never rewritten. An unmapped or incompatible request
stops intake. Proposed groups require author confirmation. The original AI draft file remains unchanged.
