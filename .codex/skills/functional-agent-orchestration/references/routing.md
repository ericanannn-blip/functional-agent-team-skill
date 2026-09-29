# Specialist routing

Input fields: `functional_role`, `task`, `context`, `constraints`, `desired_output`.

Output fields: `domain`, `primary_specialist`, `secondary_specialists`, `recommended_skills`, `confidence`, `reason`.

Use the compact catalog through `../wshobson-router/scripts/router.py`. Select at most one primary, two secondary specialists and three skills. Treat lexical scores as candidates; use model judgment to resolve ties, low-confidence domain classification and explicit specialist exclusions in `constraints`. The script does not use negative constraints as positive routing cues. If catalog metadata cannot support a match, return no specialist and explain why. Load only the selected specialist source after routing; never read the whole marketplace into context.
