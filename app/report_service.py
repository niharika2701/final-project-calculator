"""
Pure business logic for computing report statistics.

Separated from the route layer so it can be unit-tested
without a database or HTTP context — just plain Python objects.
"""


def compute_report_stats(calcs: list) -> dict:
    """
    Compute statistics from a list of Calculation ORM objects.

    Each object must have .a, .b, .result, and .type attributes.
    Returns a dict that maps directly to the ReportRead Pydantic schema.
    """
    total = len(calcs)
    if total == 0:
        return {
            "total_calculations": 0,
            "by_operation": {},
            "average_a": 0.0,
            "average_b": 0.0,
            "average_result": 0.0,
        }

    by_operation: dict[str, int] = {}
    for c in calcs:
        by_operation[c.type] = by_operation.get(c.type, 0) + 1

    return {
        "total_calculations": total,
        "by_operation": by_operation,
        "average_a": round(sum(c.a for c in calcs) / total, 4),
        "average_b": round(sum(c.b for c in calcs) / total, 4),
        "average_result": round(sum(c.result for c in calcs) / total, 4),
    }