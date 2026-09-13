"""Show actual Week 5 training, failures, merge checks and optional local inference."""

import json
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]


def render():
    st.markdown("### Week 5: specialize a race-question router")
    st.caption(
        "Custom LoRA classification lab. Nebius evaluates answers separately; it does not fine-tune this model."
    )
    report = json.loads((ROOT / "reports/router-evaluation.json").read_text())
    smoke = json.loads((ROOT / "reports/router-smoke.json").read_text())
    st.dataframe(
        [
            {
                "arm": arm,
                "accuracy": values["accuracy"],
                "macro F1": values["macro_f1"],
                "training steps": values["steps"],
            }
            for arm, values in report["results"].items()
        ],
        hide_index=True,
    )
    loss = {
        arm: values.get("loss_by_step", [])
        for arm, values in report["results"].items()
        if values.get("loss_by_step")
    }
    if loss:
        st.line_chart(
            loss, x_label="Optimizer update (zero-indexed)", y_label="Training loss"
        )
    st.caption(
        "Both trained arms use the same data and 96 steps. The untrained arm has a random classifier head; it is not a generative zero-shot model."
    )
    st.write("Five merge/inference smoke examples")
    st.dataframe(smoke["examples"], hide_index=True)
    st.write(
        f"Correct: {smoke.get('correct_count', 'not recorded')}/5 · Largest adapter/merged logit difference: {smoke['merge_max_abs_logit_difference']:.2g}"
    )
    failures = [
        row
        for row in report["predictions"]["lora"]
        if row["expected"] != row["predicted"]
    ]
    with st.expander("Keep the held-out errors visible"):
        st.dataframe(failures, hide_index=True)
        st.caption(
            "One authored synthetic split and one seed. These errors are not hidden by the improved overall score."
        )
    with st.form("week5_router_demo"):
        question = st.text_input(
            "Try the trained router", "Compare those two race sections.", max_chars=1000
        )
        run = st.form_submit_button("Classify locally")
    if run:
        try:
            from racetime.observability import record, span, trace_reference
            from training.predict import predict

            with span(
                "LoRA intent routing demo",
                "chain",
                {"question": question},
                {"scope": "separate_week5_lab"},
            ) as trace:
                result = predict(question)
                record(trace, result)
                reference = trace_reference(trace)
            st.json(result)
            if reference.get("url"):
                st.link_button("Open router trace", reference["url"])
        except (ImportError, ValueError, OSError):
            st.info(
                "For live inference, install training/requirements-lock.txt and reproduce the training and merge steps. Recorded results above remain available."
            )
    st.markdown(
        "[Week 5 demonstration and submission checklist](https://github.com/sivalinb/racetime-copilot/blob/main/docs/week5-demonstration.md)"
    )
