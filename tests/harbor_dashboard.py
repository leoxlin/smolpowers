#!/usr/bin/env python3
"""Serve a live HTML dashboard for Harbor job outputs under tests/jobs.

Usage:
    uv run --project tests python tests/harbor_dashboard.py [jobs_dir] [--port 8642]

Reads each job's config.json / result.json plus per-trial result.json,
verifier reward and test stdout tail, and renders tests/harbor_dashboard.html.j2
(Tailwind + DaisyUI via CDN). Jobs are re-scanned on every request, so the
page always shows the latest runs — just refresh.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from jinja2 import Environment, FileSystemLoader, select_autoescape

STDOUT_TAIL_LINES = 60
EXCEPTION_TAIL_CHARS = 1200

SKILL_REF_RE = re.compile(r"skills/([\w.-]+)/SKILL\.md")

PHASES = [
    ("environment_setup", "env setup"),
    ("agent_setup", "agent setup"),
    ("agent_execution", "agent exec"),
    ("verifier", "verifier"),
]
PHASE_COLORS = ["bg-neutral", "bg-info", "bg-primary", "bg-secondary"]

STATUS_CLS = {
    "completed": "badge-success", "finished": "badge-success",
    "errored": "badge-error", "stalled": "badge-error",
    "running": "badge-info", "pending": "badge-ghost",
}


def agent_name(agent_cfg: dict) -> str:
    if agent_cfg.get("name"):
        return agent_cfg["name"]
    import_path = agent_cfg.get("import_path") or ""
    return import_path.split(":")[-1] or "?"


def parse_ts(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.astimezone()


def fmt_ts(dt: datetime | None) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "—"


def fmt_dur(seconds: float | None) -> str:
    if seconds is None:
        return "—"
    seconds = max(0, seconds)
    if seconds < 60:
        return f"{seconds:.0f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def fmt_int(value) -> str:
    return f"{value:,}" if isinstance(value, (int, float)) else "—"


def fmt_cost(value) -> str:
    return f"${value:,.3f}" if isinstance(value, (int, float)) else "—"


def status_cls(status: str) -> str:
    return STATUS_CLS.get(status, "badge-ghost")


def reward_cls(reward) -> str:
    if reward >= 1:
        return "badge-success"
    if reward > 0:
        return "badge-warning"
    return "badge-error"


def tail_lines(path: Path, n: int) -> str:
    try:
        lines = path.read_text(errors="replace").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-n:])


def read_trajectory(trial_dir: Path) -> dict | None:
    """Read a trial's ATIF trajectory (agent/trajectory.json), if present."""
    try:
        data = json.loads((trial_dir / "agent" / "trajectory.json").read_text())
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def trace_overview(trial_dir: Path) -> dict | None:
    """Lightweight trace summary for the jobs list: counts and touched skills."""
    data = read_trajectory(trial_dir)
    if data is None:
        return None
    steps = data.get("steps") or []
    tool_calls = [tc for s in steps for tc in (s.get("tool_calls") or [])]
    skills = sorted(
        {
            match.group(1)
            for tc in tool_calls
            for match in SKILL_REF_RE.finditer(
                json.dumps(tc.get("arguments") or {}, ensure_ascii=False)
            )
        }
    )
    return {
        "steps": len(steps),
        "tool_calls": len(tool_calls),
        "reasoning": sum(1 for s in steps if s.get("reasoning_content")),
        "skills": skills,
    }


def _observation_text(step: dict) -> str:
    results = (step.get("observation") or {}).get("results") or []
    return "\n".join(
        str(r.get("content", "")) for r in results if isinstance(r, dict)
    )


def load_trace(trial_dir: Path) -> dict | None:
    """Full trace view-model for one trial's trajectory, for the trace page."""
    data = read_trajectory(trial_dir)
    if data is None:
        return None

    steps = []
    tool_names: Counter[str] = Counter()
    for s in data.get("steps") or []:
        tool_calls = []
        for tc in s.get("tool_calls") or []:
            args = json.dumps(
                tc.get("arguments") or {}, indent=2, ensure_ascii=False
            )
            name = tc.get("function_name", "?")
            tool_names[name] += 1
            tool_calls.append(
                {
                    "name": name,
                    "arguments": args,
                    "skills": sorted(set(SKILL_REF_RE.findall(args))),
                }
            )
        metrics = s.get("metrics") or {}
        started = parse_ts(s.get("timestamp"))
        steps.append(
            {
                "id": s.get("step_id"),
                "time": started.strftime("%H:%M:%S") if started else "—",
                "source": s.get("source", "?"),
                "message": s.get("message") or "",
                "reasoning": s.get("reasoning_content") or "",
                "tool_calls": tool_calls,
                "observation": _observation_text(s),
                "skills": sorted({sk for tc in tool_calls for sk in tc["skills"]}),
                "prompt_tokens": metrics.get("prompt_tokens"),
                "completion_tokens": metrics.get("completion_tokens"),
                "reasoning_tokens": (metrics.get("extra") or {}).get(
                    "reasoning_output_tokens"
                ),
            }
        )

    agent = data.get("agent") or {}
    final = data.get("final_metrics") or {}
    return {
        "session_id": data.get("session_id"),
        "agent_name": agent.get("name", "?"),
        "model_name": agent.get("model_name", "?"),
        "steps": steps,
        "sources": sorted({s["source"] for s in steps}),
        "tools": [
            {"name": name, "n": n} for name, n in tool_names.most_common()
        ],
        "skills": sorted({sk for s in steps for sk in s["skills"]}),
        "n_reasoning": sum(1 for s in steps if s["reasoning"]),
        "final": {
            "prompt_tokens": final.get("total_prompt_tokens"),
            "completion_tokens": final.get("total_completion_tokens"),
            "cached_tokens": final.get("total_cached_tokens"),
            "cost_usd": final.get("total_cost_usd"),
            "reasoning_tokens": (final.get("extra") or {}).get(
                "reasoning_output_tokens"
            ),
        },
    }


def resolve_trial_dir(jobs_dir: Path, job: str, trial: str) -> Path | None:
    """Resolve a /trace/<job>/<trial> request to a trial dir, rejecting escapes."""
    root = jobs_dir.resolve()
    trial_dir = (root / job / trial).resolve()
    if not trial_dir.is_relative_to(root) or trial_dir.parent.parent != root:
        return None
    return trial_dir if trial_dir.is_dir() else None


def load_trial(trial_dir: Path) -> dict:
    try:
        r = json.loads((trial_dir / "result.json").read_text())
    except (OSError, json.JSONDecodeError):
        r = None

    if r is None:
        trial = {
            "name": trial_dir.name, "task": trial_dir.name.split("__")[0],
            "dir": trial_dir.name,
            "agent": "?", "model": "?", "status": "pending", "reward": None,
            "exception": "", "started_label": "—", "duration": None,
            "input_tokens": None, "cache_tokens": None, "output_tokens": None,
            "cost_usd": None, "phases": [], "stdout_tail": "",
            "trace": None,
        }
        try:
            cfg = json.loads((trial_dir / "config.json").read_text())
            agent_cfg = cfg.get("agent") or {}
            trial["agent"] = agent_name(agent_cfg)
            model = agent_cfg.get("model_name") or "?"
            trial["model"] = model.split("/", 1)[-1]
        except (OSError, json.JSONDecodeError):
            pass
        return trial

    exception = r.get("exception_info")
    started = parse_ts(r.get("started_at"))
    finished = parse_ts(r.get("finished_at"))
    model_info = (r.get("agent_info") or {}).get("model_info") or {}
    agent_result = r.get("agent_result") or {}
    rewards = ((r.get("verifier_result") or {}).get("rewards")) or {}

    phases = []
    for key, label in PHASES:
        span = r.get(key) or {}
        p_start, p_end = parse_ts(span.get("started_at")), parse_ts(span.get("finished_at"))
        dur = (p_end - p_start).total_seconds() if p_start and p_end else None
        phases.append({"label": label, "seconds": dur})

    status = "completed"
    if exception:
        status = "errored"
    elif finished is None:
        status = "running"

    exc_text = ""
    if exception:
        msg = str(exception.get("exception_message") or "")
        exc_text = f"{exception.get('exception_type', 'Error')}: {msg}"
        if len(exc_text) > EXCEPTION_TAIL_CHARS:
            exc_text = "…" + exc_text[-EXCEPTION_TAIL_CHARS:]

    return {
        "name": r.get("trial_name", trial_dir.name),
        "dir": trial_dir.name,
        "task": r.get("task_name", "?"),
        "agent": (r.get("agent_info") or {}).get("name", "?"),
        "model": model_info.get("name", "?"),
        "status": status,
        "reward": rewards.get("reward"),
        "exception": exc_text,
        "started_label": fmt_ts(started),
        "duration": (finished - started).total_seconds() if started and finished else None,
        "input_tokens": agent_result.get("n_input_tokens"),
        "cache_tokens": agent_result.get("n_cache_tokens"),
        "output_tokens": agent_result.get("n_output_tokens"),
        "cost_usd": agent_result.get("cost_usd"),
        "phases": phases,
        "stdout_tail": tail_lines(trial_dir / "verifier" / "test-stdout.txt", STDOUT_TAIL_LINES),
        "trace": trace_overview(trial_dir),
    }


def phase_view(phases: list[dict]) -> tuple[list[dict], str]:
    total = sum(p["seconds"] or 0 for p in phases)
    if total <= 0:
        return [], ""
    segments = []
    for p, color in zip(phases, PHASE_COLORS):
        secs = p["seconds"] or 0
        if secs <= 0:
            continue
        segments.append({
            "cls": color,
            "width": f"{max(2.0, secs / total * 100):.1f}",
            "title": f"{p['label']}: {fmt_dur(secs)}",
        })
    legend = " · ".join(
        f"{p['label']} {fmt_dur(p['seconds'])}" for p in phases if p["seconds"]
    )
    return segments, legend


def load_job(job_dir: Path) -> dict:
    config = {}
    try:
        config = json.loads((job_dir / "config.json").read_text())
    except (OSError, json.JSONDecodeError):
        pass
    result = {}
    try:
        result = json.loads((job_dir / "result.json").read_text())
    except (OSError, json.JSONDecodeError):
        pass

    stats = result.get("stats") or {}
    started = parse_ts(result.get("started_at"))
    finished = parse_ts(result.get("finished_at"))

    trials = [
        load_trial(p)
        for p in sorted(job_dir.iterdir())
        if p.is_dir() and (p / "config.json").exists()
    ]
    for t in trials:
        t["phase_segments"], t["phase_legend"] = phase_view(t.pop("phases"))
        t["trace_href"] = f"/trace/{job_dir.name}/{t['dir']}" if t["trace"] else None

    agents = sorted({t.get("agent", "?") for t in trials} or
                    {agent_name(a) for a in config.get("agents", [])})

    counts = {"completed": 0, "errored": 0, "running": 0, "pending": 0}
    for t in trials:
        counts[t["status"]] = counts.get(t["status"], 0) + 1
    count_badges = [
        {"label": label, "n": counts[key], "cls": cls}
        for key, label, cls in [
            ("completed", "done", "badge-success badge-soft"),
            ("errored", "err", "badge-error badge-soft"),
            ("running", "run", "badge-info badge-soft"),
            ("pending", "pend", "badge-ghost"),
        ] if counts[key]
    ]

    rewards = [t["reward"] for t in trials if isinstance(t.get("reward"), (int, float))]
    mean_reward = sum(rewards) / len(rewards) if rewards else None

    if finished:
        job_status = "finished"
    elif counts["errored"] and not counts["running"]:
        job_status = "stalled"
    else:
        job_status = "running"

    return {
        "name": job_dir.name,
        "status": job_status,
        "started_label": fmt_ts(started),
        "duration": (finished - started).total_seconds() if started and finished else None,
        "agents": agents,
        "tasks": sorted({Path(t.get("path", "?")).name for t in config.get("tasks", [])}),
        "count_badges": count_badges,
        "mean_reward_label": f"{mean_reward:.2f}" if mean_reward is not None else "—",
        "input_tokens": stats.get("n_input_tokens"),
        "output_tokens": stats.get("n_output_tokens"),
        "cost_usd": stats.get("cost_usd"),
        "trials": trials,
    }


def agent_rollup(jobs: list[dict]) -> list[dict]:
    rollup: dict[tuple[str, str], dict] = {}
    for job in jobs:
        for t in job["trials"]:
            key = (t.get("agent", "?"), t.get("model", "?"))
            bucket = rollup.setdefault(key, {
                "agent": key[0], "model": key[1], "trials": 0, "errored": 0,
                "rewards": [], "input": 0, "output": 0, "cost": 0.0, "has_cost": False,
            })
            bucket["trials"] += 1
            bucket["errored"] += 1 if t["status"] == "errored" else 0
            if isinstance(t.get("reward"), (int, float)):
                bucket["rewards"].append(t["reward"])
            bucket["input"] += t.get("input_tokens") or 0
            bucket["output"] += t.get("output_tokens") or 0
            if isinstance(t.get("cost_usd"), (int, float)):
                bucket["cost"] += t["cost_usd"]
                bucket["has_cost"] = True
    rows = sorted(rollup.values(), key=lambda b: (b["agent"], b["model"]))
    for b in rows:
        b["mean_reward"] = sum(b["rewards"]) / len(b["rewards"]) if b["rewards"] else None
    return rows


def page_stats(jobs: list[dict]) -> dict:
    rewards = [t["reward"] for j in jobs for t in j["trials"]
               if isinstance(t.get("reward"), (int, float))]
    total_in = sum(j["input_tokens"] or 0 for j in jobs)
    total_out = sum(j["output_tokens"] or 0 for j in jobs)
    return {
        "jobs": len(jobs),
        "trials": sum(len(j["trials"]) for j in jobs),
        "errored": sum(1 for j in jobs for t in j["trials"] if t["status"] == "errored"),
        "mean_reward": f"{sum(rewards) / len(rewards):.2f}" if rewards else "—",
        "n_verified": len(rewards),
        "tokens_total": fmt_int(total_in + total_out),
        "tokens_in": fmt_int(total_in),
        "tokens_out": fmt_int(total_out),
        "cost": fmt_cost(sum(j["cost_usd"] or 0 for j in jobs)),
    }


def make_env(template_dir: Path) -> Environment:
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(["html", "j2"]),
    )
    env.filters["fmt_dur"] = fmt_dur
    env.filters["fmt_int"] = fmt_int
    env.filters["fmt_cost"] = fmt_cost
    env.filters["status_cls"] = status_cls
    env.filters["reward_cls"] = reward_cls
    return env


def render(jobs: list[dict], template_dir: Path) -> str:
    template = make_env(template_dir).get_template("harbor_dashboard.html.j2")
    return template.render(
        stats=page_stats(jobs),
        rollup=agent_rollup(jobs),
        agents=sorted({a for j in jobs for a in j["agents"]}),
        jobs=jobs,
    )


def render_trace(trace: dict, template_dir: Path, job: str, trial: str) -> str:
    template = make_env(template_dir).get_template("harbor_trace.html.j2")
    return template.render(trace=trace, job=job, trial=trial)


def load_jobs(jobs_dir: Path) -> list[dict]:
    job_dirs = sorted(
        (p for p in jobs_dir.iterdir() if p.is_dir() and (p / "result.json").exists()),
        reverse=True,
    )
    return [load_job(d) for d in job_dirs]


def make_handler(jobs_dir: Path, template_dir: Path) -> type[BaseHTTPRequestHandler]:
    class DashboardHandler(BaseHTTPRequestHandler):
        def _send_html(self, body: str) -> None:
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            path = urlparse(self.path).path
            if path in ("/", "/index.html"):
                self._send_html(render(load_jobs(jobs_dir), template_dir))
                return
            parts = [unquote(p) for p in path.strip("/").split("/")]
            if len(parts) == 3 and parts[0] == "trace":
                trial_dir = resolve_trial_dir(jobs_dir, parts[1], parts[2])
                trace = load_trace(trial_dir) if trial_dir else None
                if trace is not None:
                    self._send_html(
                        render_trace(trace, template_dir, parts[1], parts[2])
                    )
                    return
            self.send_error(404)

        def log_message(self, format: str, *args) -> None:
            pass

    return DashboardHandler


def main() -> None:
    script_dir = Path(__file__).parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs_dir", nargs="?", default=str(script_dir / "jobs"))
    parser.add_argument("--port", type=int, default=8642)
    args = parser.parse_args()

    server = ThreadingHTTPServer(
        ("127.0.0.1", args.port),
        make_handler(Path(args.jobs_dir), script_dir),
    )
    print(f"serving dashboard at http://127.0.0.1:{args.port}/ (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
