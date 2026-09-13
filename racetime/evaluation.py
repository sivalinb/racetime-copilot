"""Human evaluation summaries; unknown quality is never converted to a pass."""

from collections import Counter
from math import isfinite

ANSWERABILITY = {"answerable", "partial", "unanswerable"}
RESPONSES = {"answer", "partial", "abstain"}


def validate_annotation(case):
    """Require explicit labels, including a reason for empty expected facts."""
    if case.get("answerability") not in ANSWERABILITY:
        raise ValueError("Choose answerable, partial or unanswerable.")
    if case.get("response_type") not in RESPONSES:
        raise ValueError("Choose answer, partial or abstain for the actual response.")
    if not case.get("reviewer") or not case.get("independently_reviewed"):
        raise ValueError("A named reviewer must inspect the source.")
    facts = case.get("expected_facts")
    if not isinstance(facts, list) or any(
        not isinstance(fact, str) or not fact.strip() for fact in facts
    ):
        raise ValueError("Expected facts must be a list of nonempty strings.")
    if not facts and case["answerability"] != "unanswerable":
        raise ValueError(
            "Answerable and partial cases need timestamped expected facts."
        )
    if not str(case.get("label_reason", "")).strip():
        raise ValueError(
            "Explain the source evidence or why the answer is unavailable."
        )
    for key, maximum in (
        ("supported_percent", 100),
        ("missed_events", None),
        ("spoiler_leaks", None),
        ("max_timestamp_error_s", None),
        ("unsupported_claims", None),
    ):
        value = case.get(key)
        if key == "supported_percent" and case["response_type"] == "abstain":
            if value is not None:
                raise ValueError("Abstentions have no supported-sentence percentage.")
            continue
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not isfinite(value)
            or value < 0
            or (maximum is not None and value > maximum)
        ):
            raise ValueError(f"Invalid {key}.")
    return case


def summarize_annotations(records):
    valid, excluded = [], []
    for index, record in enumerate(records):
        try:
            valid.append(validate_annotation(record))
        except ValueError as exc:
            excluded.append({"index": index, "reason": str(exc)})
    supported = [
        c["supported_percent"] for c in valid if c["supported_percent"] is not None
    ]
    answerable = [c for c in valid if c["answerability"] == "answerable"]
    unanswerable = [c for c in valid if c["answerability"] == "unanswerable"]
    return {
        "count": len(valid),
        "excluded": excluded,
        "answerability_counts": dict(Counter(c["answerability"] for c in valid)),
        "response_counts": dict(Counter(c["response_type"] for c in valid)),
        "mean_supported_percent": sum(supported) / len(supported)
        if supported
        else None,
        "supported_percent_case_count": len(supported),
        "unnecessary_abstentions": sum(
            c["response_type"] == "abstain" for c in answerable
        ),
        "answerable_case_count": len(answerable),
        "answers_on_unanswerable": sum(
            c["response_type"] != "abstain" for c in unanswerable
        ),
        "unanswerable_case_count": len(unanswerable),
        "unsupported_claims": sum(c["unsupported_claims"] for c in valid),
        "missed_events": sum(c["missed_events"] for c in valid),
        "spoiler_leaks": sum(c["spoiler_leaks"] for c in valid),
        "largest_timestamp_error_seconds": max(
            (c["max_timestamp_error_s"] for c in valid), default=None
        ),
        "reviewer_count": len({c["reviewer"] for c in valid}),
        "labels_prepared_blind": sum(
            c.get("labels_prepared_blind") is True for c in valid
        ),
        "release_status": "not_established",
        "source": "Human annotations; reviewer attestations are not independently certified. Repeated annotations are not unique benchmark cases.",
    }


def calibrate_judge(rows):
    """Compare frozen human and judge binary decisions; never infer missing labels."""
    matrix = {"true_accept": 0, "false_accept": 0, "false_reject": 0, "true_reject": 0}
    ids = set()
    for row in rows:
        if not row.get("id") or row["id"] in ids:
            raise ValueError("Judge calibration IDs must be unique and nonempty.")
        ids.add(row["id"])
        if (
            type(row.get("human_accept")) is not bool
            or type(row.get("judge_accept")) is not bool
        ):
            raise ValueError("Calibration requires explicit human and judge booleans.")
        human, judge = row["human_accept"], row["judge_accept"]
        key = (
            ("true_accept" if judge else "false_reject")
            if human
            else ("false_accept" if judge else "true_reject")
        )
        matrix[key] += 1
    negative = matrix["false_accept"] + matrix["true_reject"]
    return {
        "count": len(rows),
        "confusion_matrix": matrix,
        "agreement": (matrix["true_accept"] + matrix["true_reject"]) / len(rows)
        if rows
        else None,
        "false_accept_rate": matrix["false_accept"] / negative if negative else None,
        "disagreement_ids": [
            r["id"] for r in rows if r["human_accept"] != r["judge_accept"]
        ],
        "both_label_classes_present": bool(negative and len(rows) > negative),
    }


def interaction_report(rows):
    """Analyze paired 2x2 runs. Scores are reviewed case passes, not model confidence."""
    cells = {
        (r, p): {} for r in ("current", "candidate") for p in ("current", "candidate")
    }
    for row in rows:
        cell = (row.get("retrieval"), row.get("policy"))
        if cell not in cells or type(row.get("passed")) is not bool:
            raise ValueError(
                "Each run needs current/candidate factors and a reviewed boolean pass."
            )
        if (
            not row.get("case_id")
            or type(row.get("repeat")) is not int
            or row["repeat"] < 1
        ):
            raise ValueError("Each run needs a case ID and positive repeat number.")
        pair = (row["case_id"], row["repeat"])
        if pair in cells[cell]:
            raise ValueError("Duplicate case/repeat in an experiment cell.")
        cells[cell][pair] = row["passed"]
    pairs = [set(cell) for cell in cells.values()]
    balanced = bool(pairs[0]) and all(p == pairs[0] for p in pairs)
    rates = {
        f"{r}_retrieval__{p}_policy": sum(cell.values()) / len(cell) if cell else None
        for (r, p), cell in cells.items()
    }
    effect = None
    if balanced:
        a, b, c, d = rates.values()
        effect = d - c - b + a
    return {
        "paired_complete": balanced,
        "cell_counts": {
            f"{r}_retrieval__{p}_policy": len(v) for (r, p), v in cells.items()
        },
        "pass_rates": rates,
        "interaction_difference": effect,
        "interpretation": "Descriptive difference of differences; not statistical significance or a causal conclusion. Hold source snapshots, model, prompt and budgets fixed outside the tested factors.",
    }
