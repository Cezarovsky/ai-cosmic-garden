#!/usr/bin/env python3
"""Extract clean transcripts from VS Code Copilot chat sessions (incremental JSONL format).

Replays the incremental updates (kind 1/2 records with key-paths) to rebuild
the final session state, then emits only user messages + assistant markdown text.
Tool payloads, file contents and metadata are dropped.

Usage: python3 extract_transcripts_v2.py <chatSessions_dir> <output_dir>
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def get_container(root, keys):
    """Walk to the container at key-path, creating dicts/lists as needed."""
    cur = root
    for i, k in enumerate(keys):
        nxt_is_index = i + 1 < len(keys) and (
            isinstance(keys[i + 1], int) or (isinstance(keys[i + 1], str) and keys[i + 1].isdigit()))
        if isinstance(cur, list):
            k = int(k)
            while len(cur) <= k:
                cur.append(None)
            if not isinstance(cur[k], (dict, list)):
                cur[k] = [] if nxt_is_index else {}
            cur = cur[k]
        else:
            if k not in cur or not isinstance(cur[k], (dict, list)):
                cur[k] = [] if nxt_is_index else {}
            cur = cur[k]
    return cur


def set_path(root, keys, value):
    """kind 1: set value at key-path."""
    parent = get_container(root, keys[:-1])
    last = keys[-1]
    if isinstance(parent, list):
        last = int(last)
        while len(parent) <= last:
            parent.append(None)
        parent[last] = value
    else:
        parent[last] = value


def append_path(root, keys, value):
    """kind 2: append/extend list at key-path."""
    target = get_container(root, keys)
    if not isinstance(target, list):
        # replace non-list with list
        set_path(root, keys, value if isinstance(value, list) else [value])
        return
    if isinstance(value, list):
        target.extend(value)
    else:
        target.append(value)


def rebuild_session(path: Path):
    state = {}
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            kind = rec.get("kind")
            if kind == 0:
                state = rec.get("v", {})
            elif kind == 1:
                keys = rec.get("k", [])
                if keys:
                    try:
                        set_path(state, keys, rec.get("v"))
                    except Exception:
                        pass
            elif kind == 2:
                keys = rec.get("k", [])
                if keys:
                    try:
                        append_path(state, keys, rec.get("v"))
                    except Exception:
                        pass
    return state


def clean_user_message(text):
    if not text:
        return ""
    m = re.findall(r"<userRequest>\s*(.*?)\s*</userRequest>", text, re.DOTALL)
    if m:
        return "\n\n".join(m)
    text = re.sub(r"<context>.*?</context>", "", text, flags=re.DOTALL)
    text = re.sub(r"<reminderInstructions>.*?</reminderInstructions>", "", text, flags=re.DOTALL)
    return text.strip()


def extract_assistant_text(response):
    parts = []
    if isinstance(response, list):
        for part in response:
            if not isinstance(part, dict):
                continue
            kind = part.get("kind", "")
            val = part.get("value")
            if kind in ("markdownContent", "") and isinstance(val, str):
                parts.append(val)
            elif isinstance(val, dict) and isinstance(val.get("value"), str) and kind in ("markdownContent", ""):
                parts.append(val["value"])
    text = "\n".join(p for p in parts if p and p.strip())
    return text.strip()


def process(path: Path, out_dir: Path):
    state = rebuild_session(path)
    title = state.get("customTitle") or path.stem
    created = state.get("creationDate")
    created_dt = datetime.fromtimestamp(created / 1000) if created else None

    turns = []
    for req in state.get("requests", []) or []:
        if not isinstance(req, dict):
            continue
        msg = req.get("message", {})
        user = msg.get("text", "") if isinstance(msg, dict) else str(msg or "")
        user = clean_user_message(user)
        assistant = extract_assistant_text(req.get("response", []))
        ts = req.get("timestamp")
        ts_dt = datetime.fromtimestamp(ts / 1000) if ts else None
        if user or assistant:
            turns.append((ts_dt, user, assistant))

    if not turns:
        return None

    date_str = created_dt.strftime("%Y-%m-%d") if created_dt else "unknown"
    safe = re.sub(r"[^\w\s-]", "", title)[:60].strip().replace(" ", "_") or path.stem
    out = out_dir / f"{date_str}_{safe}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write(f"# {title}\n\n")
        f.write(f"*Session `{path.stem}`*  \n")
        if created_dt:
            f.write(f"*Started {created_dt:%Y-%m-%d %H:%M}*  \n")
        f.write(f"*Extracted {datetime.now():%Y-%m-%d %H:%M}*\n\n---\n\n")
        last_day = None
        for ts_dt, user, assistant in turns:
            if ts_dt and ts_dt.date() != last_day:
                last_day = ts_dt.date()
                f.write(f"\n> **{ts_dt:%A, %d %B %Y}**\n\n")
            if user:
                f.write(f"## Cezar\n\n{user}\n\n")
            if assistant:
                f.write(f"## Fable\n\n{assistant}\n\n")
            f.write("---\n\n")
    return out


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.mkdir(parents=True, exist_ok=True)
    for f in sorted(src.glob("*.jsonl")):
        try:
            out = process(f, dst)
            if out:
                print(f"OK   {f.name} ({f.stat().st_size/1024:.0f}K) -> {out.name} ({out.stat().st_size/1024:.0f}K)")
            else:
                print(f"SKIP {f.name} — no dialogue")
        except Exception as e:
            print(f"ERR  {f.name}: {e}")


if __name__ == "__main__":
    main()
