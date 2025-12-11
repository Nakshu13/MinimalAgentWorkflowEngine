from typing import Dict, Any, List
from statistics import mean

from app.core.registry import tool_registry
from app.core.engine import NEXT_NODE_KEY


@tool_registry.register("profile_data")
def profile_data(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 1: Profile data.
    Compute basic stats per column: min, max, mean, missing_ratio.
    Expect state["data"] as a list of dict rows.
    """
    data: List[Dict[str, Any]] = state.get("data", [])
    if not data:
        return {"profile": {}, "row_count": 0}

    row_count = len(data)
    columns = data[0].keys()
    profile: Dict[str, Any] = {}

    for col in columns:
        values = [row.get(col) for row in data]
        missing_count = sum(1 for v in values if v is None)
        present_values = [v for v in values if isinstance(v, (int, float))]

        col_profile: Dict[str, Any] = {
            "missing_count": missing_count,
            "missing_ratio": missing_count / row_count if row_count > 0 else 0.0,
        }

        if present_values:
            col_profile.update(
                {
                    "min": min(present_values),
                    "max": max(present_values),
                    "mean": mean(present_values),
                }
            )

        profile[col] = col_profile

    return {"profile": profile, "row_count": row_count}


@tool_registry.register("identify_anomalies")
def identify_anomalies(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 2: Identify anomalies using simple rules:
    - Missing values
    - Numeric values < min or > max (from profile)
    """
    data: List[Dict[str, Any]] = state.get("data", [])
    profile: Dict[str, Any] = state.get("profile", {})

    anomaly_rows: List[int] = []
    anomaly_details: List[Dict[str, Any]] = []

    for idx, row in enumerate(data):
        row_issues: Dict[str, str] = {}
        for col, value in row.items():
            col_profile = profile.get(col, {})
            if value is None:
                row_issues[col] = "MISSING"
                continue

            if isinstance(value, (int, float)):
                col_min = col_profile.get("min")
                col_max = col_profile.get("max")
                if col_min is not None and value < col_min:
                    row_issues[col] = f"BELOW_MIN({col_min})"
                elif col_max is not None and value > col_max:
                    row_issues[col] = f"ABOVE_MAX({col_max})"

        if row_issues:
            anomaly_rows.append(idx)
            anomaly_details.append({"row_index": idx, "issues": row_issues})

    anomaly_info = {
        "count": len(anomaly_rows),
        "rows": anomaly_rows,
        "details": anomaly_details,
    }
    return {"anomalies": anomaly_info, "anomaly_count": anomaly_info["count"]}


@tool_registry.register("generate_rules")
def generate_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 3: Generate simple validation rules from the profile.
    Example: each numeric column must stay within observed [min, max].
    """
    profile: Dict[str, Any] = state.get("profile", {})
    rules: List[Dict[str, Any]] = []

    for col, stats in profile.items():
        constraints: List[Dict[str, Any]] = []
        if "min" in stats and "max" in stats:
            constraints.append(
                {
                    "type": "range",
                    "min": stats["min"],
                    "max": stats["max"],
                }
            )
        if "missing_ratio" in stats:
            constraints.append(
                {
                    "type": "missing_ratio",
                    "max_missing_ratio": stats["missing_ratio"],
                }
            )

        rules.append({"column": col, "constraints": constraints})

    return {"rules": rules}


@tool_registry.register("apply_rules")
def apply_rules(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 4: Apply generated rules and recompute anomalies.
    """
    data: List[Dict[str, Any]] = state.get("data", [])
    rules: List[Dict[str, Any]] = state.get("rules", [])

    rules_by_col = {r["column"]: r["constraints"] for r in rules}

    anomaly_rows: List[int] = []
    anomaly_details: List[Dict[str, Any]] = []

    for idx, row in enumerate(data):
        row_issues: Dict[str, str] = {}

        for col, value in row.items():
            constraints = rules_by_col.get(col, [])
            for c in constraints:
                if c["type"] == "range" and isinstance(value, (int, float)):
                    if value < c["min"] or value > c["max"]:
                        row_issues[col] = "RANGE_VIOLATION"
                if c["type"] == "missing_ratio":
                    if value is None:
                        row_issues[col] = "MISSING_VALUE"

        if row_issues:
            anomaly_rows.append(idx)
            anomaly_details.append({"row_index": idx, "issues": row_issues})

    anomaly_info = {
        "count": len(anomaly_rows),
        "rows": anomaly_rows,
        "details": anomaly_details,
    }
    return {
        "anomalies": anomaly_info,
        "anomaly_count": anomaly_info["count"],
        "rules_applied": True,
    }


@tool_registry.register("decide_next_step")
def decide_next_step(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Step 5: Decide whether to loop back or stop.
    If anomaly_count > anomaly_threshold → loop back to 'profile' node.
    Else stop.
    """
    anomaly_count = state.get("anomaly_count", 0)
    threshold = state.get("anomaly_threshold", 0)

    if anomaly_count > threshold:
        # loop: go back to the profiling node
        state[NEXT_NODE_KEY] = "profile"
        decision = f"Looping again: {anomaly_count} > {threshold}"
    else:
        decision = f"Stopping: {anomaly_count} <= {threshold}"

    return {"loop_decision": decision}
