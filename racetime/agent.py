"""Bounded planner with real durable LangGraph human interruption."""

import operator
import re
import sqlite3
from typing import Annotated, TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt

from .config import DATA
from .observability import observed


class State(TypedDict, total=False):
    question: str
    start: float
    end: float
    as_of: float
    media: str
    coverage: list
    gaps: list
    limitations: list
    selected: list
    action: str
    iterations: int
    retrieved: bool
    inspected: bool
    narrative: dict
    review: str
    clarification: str
    trace: Annotated[list, operator.add]


class Agent:
    """Coordinate evidence retrieval, bounded model decisions and durable review."""

    def __init__(self, store, provider, owner, job, inspect, checkpoint_path=None):
        self.store, self.provider, self.owner, self.job, self.inspect = (
            store,
            provider,
            owner,
            job,
            inspect,
        )
        self.connection = sqlite3.connect(
            checkpoint_path or DATA / "checkpoints.sqlite", check_same_thread=False
        )
        self.checkpointer = SqliteSaver(self.connection)
        graph = StateGraph(State)
        for name, node_function in [
            ("plan", self.plan),
            ("retrieve", self.retrieve),
            ("inspect", self.inspect_node),
            ("summarize", self.summarize),
            ("clarify", self.clarify),
            ("review", self.review),
        ]:
            graph.add_node(name, node_function)
        graph.add_edge(START, "plan")
        graph.add_conditional_edges(
            "plan",
            lambda state: state["action"],
            {
                "retrieve": "retrieve",
                "inspect": "inspect",
                "summarize": "summarize",
                "clarify": "clarify",
            },
        )
        graph.add_edge("retrieve", "plan")
        graph.add_edge("inspect", "retrieve")
        graph.add_edge("summarize", "review")
        graph.add_edge("clarify", END)
        graph.add_edge("review", END)
        self.graph = graph.compile(checkpointer=self.checkpointer)

    def plan(self, state):
        """Choose a permitted action within the inspection and iteration limits."""
        if not state.get("retrieved"):
            actions = ["retrieve"]
        else:
            actions = ["clarify"]
            if state.get("selected"):
                actions.append("summarize")
            if (
                not state.get("inspected")
                and state.get("iterations", 0) < 3
                and self.store.media(self.owner, state["media"])["kind"] != "live"
            ):
                actions.append("inspect")
        if (
            state.get("retrieved")
            and not state.get("selected")
            and not state.get("inspected")
            and "inspect" in actions
        ):
            actions = ["inspect"]
        if state.get("iterations", 0) >= 4:
            actions = ["summarize"] if state.get("selected") else ["clarify"]
        if len(actions) == 1:
            decision = {
                "action": actions[0],
                "reason": "Only legal action for the current evidence and budget.",
            }
            mode = "rule"
        else:
            try:
                decision = self.provider.plan(
                    state["question"],
                    actions,
                    state.get("selected", []),
                    context={
                        "start": state["start"],
                        "end": state["end"],
                        "source_available": True,
                    },
                )
                mode = "llm"
            except ValueError as exc:
                decision = {
                    "action": "summarize"
                    if "summarize" in actions
                    else "inspect"
                    if "inspect" in actions
                    else "clarify",
                    "reason": str(exc),
                }
                mode = "fallback"
        return {
            "action": decision["action"],
            "iterations": state.get("iterations", 0) + 1,
            "trace": [{"step": "plan", "mode": mode, **decision}],
        }

    @observed("Retrieve interval evidence", "retriever", ("state",))
    def retrieve(self, state):
        """Rank eligible observations and retain related conflicting claims."""
        pool = [
            (observation, vector)
            for observation, vector in self.store.observations(
                self.owner, state["media"]
            )
            if state["start"]
            <= observation["start"]
            < observation["end"]
            <= state["end"]
            and observation.get("availableAt", observation["end"]) <= state["as_of"]
            and not re.search(
                r"ignore (?:all |previous |prior )?instructions|system prompt|reveal.*secret",
                observation["text"],
                re.I,
            )
        ]
        if pool:
            question_vector = self.provider.embed([state["question"]], query=True)[0]
            scored = sorted(
                pool,
                key=lambda candidate: sum(
                    a * b for a, b in zip(question_vector, candidate[1], strict=True)
                ),
                reverse=True,
            )
            selected = [observation for observation, _ in scored[:30]]
            keys = {
                observation.get("claimKey")
                for observation in selected
                if observation.get("claimKey")
            }
            selected.extend(
                observation
                for observation, _ in pool
                if observation.get("claimKey") in keys and observation not in selected
            )
            selected.sort(key=lambda observation: observation["start"])
        else:
            selected = []
        return {
            **self.store.coverage(
                self.owner, state["media"], state["start"], state["end"]
            ),
            "selected": selected,
            "retrieved": True,
            "trace": [{"step": "retrieve", "mode": "semantic", "count": len(selected)}],
        }

    def inspect_node(self, state):
        """Inspect the requested interval before retrieving the new evidence."""
        self.inspect(state["media"], state["start"], state["end"])
        return {
            "inspected": True,
            "trace": [
                {"step": "inspect", "start": state["start"], "end": state["end"]}
            ],
        }

    def summarize(self, state):
        """Generate a grounded recap, falling back to labeled evidence extracts."""
        try:
            narrative = self.provider.summarize(state["question"], state["selected"])
            mode = "generated_verified"
        except ValueError as exc:
            narrative = {
                "sentences": [
                    {"text": observation["text"], "evidence_ids": [observation["id"]]}
                    for observation in state["selected"][:6]
                ],
                "warning": str(exc),
            }
            mode = "extractive_fallback"
        return {"narrative": narrative, "trace": [{"step": "summarize", "mode": mode}]}

    def clarify(self, state):
        return {
            "clarification": "There is not enough usable evidence for this question. Choose another interval, make the question more specific, or inspect the video first.",
            "trace": [{"step": "clarify", "mode": "rule"}],
        }

    def review(self, state):
        """Pause the graph until a reviewer explicitly approves or rejects."""
        decision = interrupt(
            {
                "question": "Review the recap and timestamped evidence before approving.",
                "narrative": state["narrative"],
            }
        )
        if decision not in ["approved", "rejected"]:
            raise ValueError("Choose approved or rejected.")
        return {
            "review": decision,
            "trace": [{"step": "human_review", "decision": decision}],
        }

    def run(self, payload=None, resume=None):
        """Start or resume this owner's job and report whether review is pending."""
        config = {
            "configurable": {"thread_id": self.owner + ":" + self.job},
            "recursion_limit": 24,
            "run_name": "racetime-video-agent",
            "metadata": {
                "job_id": self.job,
                "media_id": (payload or {}).get("media", ""),
            },
        }
        result = self.graph.invoke(
            Command(resume=resume) if resume else payload, config
        )
        result.pop("__interrupt__", None)
        waiting = bool(self.graph.get_state(config).next)
        return result, waiting

    def close(self):
        self.connection.close()
