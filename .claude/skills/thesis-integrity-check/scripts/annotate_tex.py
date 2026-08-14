#!/usr/bin/env python3
"""
Write prose-voice findings into LaTeX source as reviewable comment blocks,
strip them again, or check that none were left behind.

Design rule: this NEVER silently changes the author's prose. Suggestions go in
as LaTeX comments (%), which do not compile — the PDF is byte-identical until
the author accepts a suggestion by hand. Accepting means editing the sentence
yourself, which is the point: the resulting words are yours.

Block format inserted above the flagged paragraph:

    % >>> TIC-VOICE V03 | pattern 2+7 | chapters/05-results.tex:142
    % ORIGINAL : the system delivers robust and scalable performance
    % SUGGEST  : With PostgreSQL persistence at 200 req/s the connector held
    %            p95 negotiation latency at 340 ms.
    % WHY      : names backend, arrival rate, and the measured percentile.
    % <<< TIC-VOICE V03

Usage:
    python annotate_tex.py --findings f.json --root ~/thesis --out-dir ~/thesis-annotated
    python annotate_tex.py --findings f.json --root ~/thesis --in-place
    python annotate_tex.py --strip --root ~/thesis-annotated --in-place
    python annotate_tex.py --check --root ~/thesis

Findings JSON:
    {"findings": [{"id": "V03", "file": "chapters/05-results.tex",
                   "line": 142, "pattern": "2+7",
                   "original": "...", "suggest": "...", "why": "..."}]}
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path
from textwrap import wrap

OPEN = re.compile(r"^\s*%\s*>>>\s*TIC-VOICE\b")
CLOSE = re.compile(r"^\s*%\s*<<<\s*TIC-VOICE\b")


def render(f: dict) -> list:
    fid = f.get("id", "V??")
    head = f"% >>> TIC-VOICE {fid} | pattern {f.get('pattern','-')} | {f.get('file','')}:{f.get('line','')}"
    lines = [head]
    for label, key in (("ORIGINAL", "original"), ("SUGGEST", "suggest"), ("WHY", "why")):
        val = (f.get(key) or "").strip()
        if not val:
            continue
        val = re.sub(r"\s+", " ", val)
        pieces = wrap(val, width=72) or [""]
        lines.append(f"% {label:<9}: {pieces[0]}")
        lines.extend(f"% {'':<9}  {p}" for p in pieces[1:])
    lines.append(f"% <<< TIC-VOICE {fid}")
    return lines


def annotate(root: Path, out_root: Path, findings: list, dry: bool) -> int:
    by_file = {}
    for f in findings:
        by_file.setdefault(f["file"], []).append(f)

    written = 0
    for rel, items in sorted(by_file.items()):
        src = root / rel
        if not src.exists():
            print(f"  ! missing, skipped: {rel}", file=sys.stderr)
            continue

        lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
        # Insert bottom-up so earlier line numbers stay valid.
        for f in sorted(items, key=lambda x: int(x["line"]), reverse=True):
            at = max(0, min(int(f["line"]) - 1, len(lines)))
            lines[at:at] = render(f)

        dst = out_root / rel
        print(f"  {rel}: +{len(items)} annotation(s) -> {dst}")
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text("\n".join(lines) + "\n", encoding="utf-8")
        written += len(items)
    return written


def strip(root: Path, out_root: Path, dry: bool) -> int:
    removed = 0
    for src in sorted(root.rglob("*.tex")):
        lines = src.read_text(encoding="utf-8", errors="replace").splitlines()
        kept, inside, n = [], False, 0
        for line in lines:
            if OPEN.match(line):
                inside, n = True, n + 1
                continue
            if inside:
                if CLOSE.match(line):
                    inside = False
                continue
            kept.append(line)
        if inside:
            print(f"  ! unterminated block in {src} — left file untouched", file=sys.stderr)
            continue
        if n:
            rel = src.relative_to(root)
            print(f"  {rel}: -{n} annotation(s)")
            if not dry:
                dst = out_root / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text("\n".join(kept) + "\n", encoding="utf-8")
            removed += n
    return removed


def check(root: Path) -> int:
    found = 0
    for src in sorted(root.rglob("*.tex")):
        for i, line in enumerate(src.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if OPEN.match(line):
                print(f"  {src.relative_to(root)}:{i}")
                found += 1
    return found


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", required=True, help="LaTeX project root")
    ap.add_argument("--findings", help="findings JSON (annotate mode)")
    ap.add_argument("--strip", action="store_true", help="remove all TIC-VOICE blocks")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any annotations remain (run before submitting)")
    ap.add_argument("--out-dir", help="write to this copy instead of the original")
    ap.add_argument("--in-place", action="store_true", help="edit the project directly")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"Not a directory: {root}")

    if args.check:
        n = check(root)
        if n:
            print(f"\n{n} annotation block(s) still present. Strip before submitting.")
            sys.exit(1)
        print("Clean — no TIC-VOICE annotations found.")
        return

    if not args.in_place and not args.out_dir:
        sys.exit("Refusing to guess. Pass --out-dir <copy> (safe) or --in-place.")

    if args.in_place:
        out_root = root
        print("In-place mode. Commit your work to git first — "
              "that history is also your provenance record if anyone ever asks.\n")
    else:
        out_root = Path(args.out_dir).expanduser().resolve()
        if not args.dry_run and out_root != root:
            if out_root.exists():
                shutil.rmtree(out_root)
            shutil.copytree(root, out_root)
        print(f"Working on copy: {out_root}\n")

    if args.strip:
        n = strip(out_root if args.in_place else out_root, out_root, args.dry_run)
        print(f"\nRemoved {n} annotation block(s).")
        return

    if not args.findings:
        sys.exit("Need --findings, --strip, or --check.")

    data = json.loads(Path(args.findings).expanduser().read_text(encoding="utf-8"))
    findings = data.get("findings", data if isinstance(data, list) else [])
    if not findings:
        sys.exit("No findings in file.")

    n = annotate(root, out_root, findings, args.dry_run)
    print(f"\nInserted {n} annotation block(s).")
    print("These are comments — your PDF output is unchanged until you accept one by hand.")
    print("When done: --strip to remove, then --check before submitting.")


if __name__ == "__main__":
    main()
