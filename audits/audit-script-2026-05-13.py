#!/usr/bin/env python3
"""Mechanical audit of Claude Code sessions for ai-skills plugin issues.

Scans all session JSONL files modified in the last 2 days, extracts:
- ai-skills skill/agent invocations
- tool errors / is_error blocks
- hook failures
- subagent results (RALF kills, contract violations, "RUBRIC_FAILED" markers)
- excessive retries on same tool/file
- token-heavy / time-heavy spawns
"""
import json
import os
import re
import sys
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path.home() / ".claude" / "projects"
CUTOFF = datetime.now(timezone.utc) - timedelta(days=2)

AI_ASSETS_RE = re.compile(r"ai-skills[:/]([a-z0-9\-]+)", re.IGNORECASE)
RUBRIC_FAIL_RE = re.compile(r"RUBRIC_FAILED|FAIL_RALF|G7\s*violation|contract\s*violation", re.IGNORECASE)
ERR_HINT_RE = re.compile(r"error|failed|exception|traceback|denied|timeout|killed", re.IGNORECASE)


def safe_load(line: str):
    try:
        return json.loads(line)
    except Exception:
        return None


def iter_sessions():
    for jsonl in ROOT.rglob("*.jsonl"):
        try:
            mtime = datetime.fromtimestamp(jsonl.stat().st_mtime, tz=timezone.utc)
        except FileNotFoundError:
            continue
        if mtime < CUTOFF:
            continue
        yield jsonl


def get_text(content):
    """Flatten content blocks to text for regex scanning."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for blk in content:
            if not isinstance(blk, dict):
                continue
            if blk.get("type") == "text":
                parts.append(blk.get("text", ""))
            elif blk.get("type") == "tool_result":
                parts.append(get_text(blk.get("content", "")))
            elif blk.get("type") == "tool_use":
                parts.append(json.dumps(blk.get("input", {}))[:2000])
        return "\n".join(parts)
    if isinstance(content, dict):
        return json.dumps(content)[:2000]
    return ""


def analyze():
    findings = {
        "ai_skills_invocations": Counter(),
        "tool_errors_per_skill": defaultdict(list),
        "rubric_fails": [],
        "hook_failures": [],
        "subagent_failures": [],
        "agent_excessive_iter": [],
        "denied_tools": [],
        "interrupted": [],
        "session_counts": Counter(),
        "permission_denied": [],
        "sessions_seen": set(),
        "isError_messages": [],
        "subagents_total": 0,
        "subagents_with_errors": 0,
    }

    for jsonl in iter_sessions():
        sess_label = f"{jsonl.parent.name}/{jsonl.name}"
        is_subagent = "subagents" in jsonl.parts
        if is_subagent:
            findings["subagents_total"] += 1
        had_err = False
        seen_ai_skills_in_session = set()
        last_skill_for_session = None
        with open(jsonl, "rb") as f:
            for raw in f:
                try:
                    d = json.loads(raw.decode("utf-8", errors="replace"))
                except Exception:
                    continue
                ttype = d.get("type")
                findings["session_counts"][ttype] += 1

                msg = d.get("message") or {}
                content = msg.get("content")
                # Extract text for scanning
                text = get_text(content) if content else ""

                # Track ai-skills invocations
                # 1) Skill name in content/text
                for m in AI_ASSETS_RE.finditer(text):
                    skill = m.group(1).lower()
                    if skill in ("memory", "rules", "templates"):  # noise
                        continue
                    findings["ai_skills_invocations"][skill] += 1
                    seen_ai_skills_in_session.add(skill)
                    last_skill_for_session = skill

                # 2) tool_use blocks
                if isinstance(content, list):
                    for blk in content:
                        if not isinstance(blk, dict):
                            continue
                        if blk.get("type") == "tool_use":
                            inp = blk.get("input", {}) or {}
                            name = blk.get("name", "")
                            # Skill tool invocation
                            if name == "Skill":
                                sk = (inp.get("skill") or "").lower()
                                if sk.startswith("ai-skills:"):
                                    findings["ai_skills_invocations"][sk.split(":",1)[1]] += 1
                                    seen_ai_skills_in_session.add(sk.split(":",1)[1])
                                    last_skill_for_session = sk.split(":",1)[1]
                            # Agent tool with subagent_type
                            if name == "Agent":
                                stype = (inp.get("subagent_type") or "")
                                if stype.startswith("ai-skills:"):
                                    role = stype.split(":",1)[1]
                                    findings["ai_skills_invocations"][f"AGENT:{role}"] += 1
                                    seen_ai_skills_in_session.add(f"AGENT:{role}")

                        # is_error tool_result
                        if blk.get("type") == "tool_result" and blk.get("is_error"):
                            had_err = True
                            err_text = get_text(blk.get("content"))[:600]
                            findings["isError_messages"].append({
                                "session": sess_label,
                                "skill_context": last_skill_for_session,
                                "snippet": err_text,
                            })
                            if last_skill_for_session:
                                findings["tool_errors_per_skill"][last_skill_for_session].append(err_text[:300])

                # Rubric / contract failures
                if RUBRIC_FAIL_RE.search(text):
                    findings["rubric_fails"].append({
                        "session": sess_label,
                        "skill_context": last_skill_for_session,
                        "snippet": text[:500],
                    })

                # Hook failures: look for "hook" + "fail"/"blocked" combos
                lower = text.lower()
                if "hook" in lower and ("blocked" in lower or "exit code" in lower or "permission-mode" in lower):
                    if "blocked by a hook" in lower or "hook returned" in lower or "hook failure" in lower:
                        findings["hook_failures"].append({
                            "session": sess_label,
                            "snippet": text[:500],
                        })

                # Permission denied
                if "permission denied" in lower or "user denied" in lower or "denied by user" in lower:
                    findings["denied_tools"].append({
                        "session": sess_label,
                        "snippet": text[:300],
                    })

                # Interrupted by user
                if "[request interrupted by user" in lower or "interrupted by user" in lower:
                    findings["interrupted"].append({"session": sess_label, "snippet": text[:200]})

                # Tool result with explicit "error" textual hint and subagent context
                if is_subagent and ttype in ("user", "assistant"):
                    if "RUBRIC_FAILED_3X" in text or "kill-on" in text.lower():
                        findings["agent_excessive_iter"].append({"session": sess_label, "snippet": text[:400]})

        if is_subagent and had_err:
            findings["subagents_with_errors"] += 1
        findings["sessions_seen"].add(sess_label)

    return findings


def main():
    f = analyze()
    f["sessions_seen"] = sorted(f["sessions_seen"])
    # Dedupe big lists
    for k in ("rubric_fails", "hook_failures", "isError_messages", "denied_tools",
              "interrupted", "agent_excessive_iter"):
        seen = set()
        unique = []
        for item in f[k]:
            sig = (item.get("session"), item.get("snippet", "")[:120])
            if sig in seen:
                continue
            seen.add(sig)
            unique.append(item)
        f[k] = unique

    # Print summary
    print("=" * 80)
    print(f"AI-ASSETS PLUGIN AUDIT — last 2 days, cutoff = {CUTOFF.isoformat()}")
    print("=" * 80)
    print(f"\nSessions scanned: {len(f['sessions_seen'])}")
    print(f"Subagent transcripts: {f['subagents_total']} (with at least one tool_result is_error: {f['subagents_with_errors']})")
    print("\n--- ai-skills invocations (skills/agents seen in transcripts) ---")
    for k, v in f["ai_skills_invocations"].most_common():
        print(f"  {v:5d}  {k}")

    print("\n--- tool errors per skill (top) ---")
    for skill, errs in sorted(f["tool_errors_per_skill"].items(), key=lambda x: -len(x[1]))[:15]:
        print(f"  [{skill}] errors={len(errs)}; sample:")
        print(f"    {errs[0][:280].replace(chr(10),' ')}")

    print(f"\n--- rubric/contract violations ({len(f['rubric_fails'])}) ---")
    for x in f["rubric_fails"][:8]:
        print(f"  [{x['skill_context']}] {x['session']}")
        print(f"    {x['snippet'][:280].replace(chr(10),' ')}")

    print(f"\n--- hook failures ({len(f['hook_failures'])}) ---")
    for x in f["hook_failures"][:8]:
        print(f"  {x['session']}")
        print(f"    {x['snippet'][:280].replace(chr(10),' ')}")

    print(f"\n--- isError tool_results ({len(f['isError_messages'])}) ---")
    for x in f["isError_messages"][:25]:
        print(f"  [{x['skill_context']}] {x['session']}")
        print(f"    {x['snippet'][:280].replace(chr(10),' ')}")

    print(f"\n--- user denials of tool calls ({len(f['denied_tools'])}) ---")
    for x in f["denied_tools"][:10]:
        print(f"  {x['session']}: {x['snippet'][:200].replace(chr(10),' ')}")

    print(f"\n--- interruptions ({len(f['interrupted'])}) ---")
    for x in f["interrupted"][:10]:
        print(f"  {x['session']}: {x['snippet'][:200].replace(chr(10),' ')}")

    print(f"\n--- agent excessive iter / RALF kills ({len(f['agent_excessive_iter'])}) ---")
    for x in f["agent_excessive_iter"][:8]:
        print(f"  {x['session']}: {x['snippet'][:280].replace(chr(10),' ')}")

    # Save raw json for follow-up
    out = Path("/tmp/ai_skills_audit_findings.json")
    serializable = {k: (v if not isinstance(v, set) else sorted(v))
                    for k, v in f.items()}
    serializable["ai_skills_invocations"] = dict(f["ai_skills_invocations"])
    serializable["tool_errors_per_skill"] = {k: v for k, v in f["tool_errors_per_skill"].items()}
    serializable["session_counts"] = dict(f["session_counts"])
    out.write_text(json.dumps(serializable, indent=2, default=str))
    print(f"\nRaw findings -> {out}")


if __name__ == "__main__":
    main()
