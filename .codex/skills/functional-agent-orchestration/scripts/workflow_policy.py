"""Deterministic workflow dispatch hints; authorization remains with the host/user."""

import json
import sys

MODELS = {
    "orchestrator": ("gpt-5.6-sol", "high"),
    "researcher": ("gpt-6-luna", "high"),
    "planner": ("gpt-5.6-sol", "medium"),
    "analyst": ("gpt-6-luna", "high"),
    "executor": ("gpt-6-luna", "high"),
    "verifier": ("gpt-6-luna", "high"),
    "reviewer": ("gpt-5.6-sol", "high"),
    "wshobson-router": ("gpt-6-luna", "high"),
}


def dispatch(role, *, complexity="normal", impact="low", evidence_conflict=False,
             low_confidence=False, repeated_failure=False, analyst_escalation=0):
    if role not in MODELS:
        raise ValueError(f"Unknown role: {role}")
    model, reasoning = MODELS[role]
    if role == "planner" and (complexity == "complex" or impact == "high"):
        reasoning = "high"
    if role == "analyst" and (evidence_conflict or low_confidence or repeated_failure or impact == "high"):
        if analyst_escalation >= 1:
            model = "gpt-5.6-sol"
            reasoning = "high" if analyst_escalation >= 2 else "medium"
    return {"role": role, "model": model, "reasoning": reasoning}


def failure_destination(role, outcome):
    if role == "executor" and outcome == "FAIL":
        return ["analyst", "planner", "executor"]
    if role == "verifier" and outcome in {"FAIL", "PARTIAL"}:
        return ["analyst", "planner", "executor", "verifier"]
    if role == "reviewer" and outcome == "rework_required":
        return ["planner", "executor", "verifier", "reviewer"]
    return []


if __name__ == "__main__":
    request = json.load(sys.stdin)
    if request.get("operation") == "failure":
        result = {"next_roles": failure_destination(request["role"], request["outcome"])}
    else:
        result = dispatch(**request)
    json.dump(result, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
