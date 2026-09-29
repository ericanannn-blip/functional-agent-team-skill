# Failure handling

Verifier returns PASS, FAIL or PARTIAL and does not fix failures. FAIL or PARTIAL goes to Analyst for diagnosis, then Planner for a bounded retry, then Executor and Verifier. Reviewer rework goes to Planner, Executor, Verifier and Reviewer. Limit retries to the failure's scope; stop when a missing authorization, unavailable dependency or external state blocks meaningful progress. Record verified and unverified outcomes separately.
