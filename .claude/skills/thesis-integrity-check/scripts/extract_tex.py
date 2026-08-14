#!/usr/bin/env python3
"""
Extract prose paragraphs from a LaTeX project, with file+line anchors and
triage signals for the prose-voice pass.

The signals here are a TRIAGE AID, not a verdict. They tell you which
paragraphs to read first; the judgement stays with the human reading them.
A low-groundedness score means "this paragraph asserts things without
anchoring them in data" — which is a writing problem worth fixing whether
or not any detector ever sees it.

Usage:
    python extract_tex.py <main.tex | project-dir> -o paragraphs.json
    python extract_tex.py chapters/ -o paragraphs.json --min-words 25
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Environments whose contents are not prose and must never be flagged.
SKIP_ENVS = {
    "equation", "equation*", "align", "align*", "gather", "gather*",
    "multline", "multline*", "eqnarray", "eqnarray*", "array", "displaymath",
    "lstlisting", "verbatim", "Verbatim", "minted", "listing", "code",
    "tabular", "tabularx", "longtable", "tabu", "supertabular",
    "tikzpicture", "pgfplots", "axis", "filecontents", "filecontents*",
    "thebibliography", "comment",
}

HEDGES = re.compile(
    r"\b(may|might|could|possibly|potentially|arguably|generally|typically|"
    r"tends? to|somewhat|relatively|fairly|rather|seems? to|appears? to|"
    r"in some cases|to some extent|it can be argued)\b", re.I)

FILLER_OPENERS = re.compile(
    r"^\s*(Moreover|Furthermore|In addition|Additionally|Overall|"
    r"It is important to note|It is worth noting|As mentioned|As discussed|"
    r"Notably|Consequently|Therefore|Thus|Hence|In conclusion|"
    r"First(ly)?|Second(ly)?|Third(ly)?)\b", re.I)

UNIVERSAL = re.compile(
    r"(?:\b(?:crucial|vital|pivotal|paramount|essential|key|central)\s+role\b)"
    r"|(?:\bwide range of\b)"
    r"|(?:\bvarious\s+(?:approaches|methods|techniques|factors|aspects)\b)"
    r"|(?:\bnumerous\b)"
    r"|(?:\brapidly evolving\b)"
    r"|(?:\bgained significant attention\b)"
    r"|(?:\bof paramount importance\b)"
    r"|(?:\bit is well known\b)"
    r"|(?:\bstudies have shown\b)"
    r"|(?:\bwidely accepted\b)", re.I)

# Concreteness markers: numbers, units, versions, refs, citations, code-ish tokens.
NUMERIC = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|ms|s|m|h|GB|MB|KB|kB|GiB|MiB|"
                     r"req/s|rps|ops/s|MB/s|Gbps|Mbps|cores?|threads?|nodes?|vCPU)?\b")
CITE = re.compile(r"\\(?:cite|citep|citet|citeauthor|citeyear|autocite)\w*\s*[\[{]")
REF = re.compile(r"\\(?:ref|cref|Cref|autoref|eqref|nameref)\s*\{")
CODEISH = re.compile(r"\\(?:texttt|lstinline|verb|emph\{[A-Z])|"
                     r"\b[a-z]+[A-Z][a-zA-Z]*\b|\b[A-Z]{2,}(?:-[A-Z0-9]+)?\b|"
                     r"\bv?\d+\.\d+(?:\.\d+)?\b")


def strip_comments(line: str) -> str:
    """Remove LaTeX comments, respecting escaped percent signs."""
    out, i = [], 0
    while i < len(line):
        c = line[i]
        if c == "\\" and i + 1 < len(line):
            out.append(line[i:i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def clean_for_reading(text: str) -> str:
    """Light de-LaTeX so the paragraph is readable in a report."""
    text = re.sub(r"\\(?:label|index|nocite)\s*\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:cite|citep|citet|autocite)\w*\s*(?:\[[^\]]*\])?\s*\{([^}]*)\}",
                  r"[\1]", text)
    text = re.sub(r"\\(?:ref|cref|Cref|autoref)\s*\{([^}]*)\}", r"(ref:\1)", text)
    text = re.sub(r"\\(?:textbf|textit|emph|texttt|textsc)\s*\{([^}]*)\}", r"\1", text)
    text = re.sub(r"\\[a-zA-Z@]+\s*\*?", " ", text)
    text = re.sub(r"[{}]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def collect_files(target: Path):
    """Return .tex files, following \\input/\\include from a main file."""
    if target.is_dir():
        return sorted(p for p in target.rglob("*.tex") if p.is_file())

    seen, order, queue = set(), [], [target]
    root = target.parent
    while queue:
        f = queue.pop(0)
        rf = f.resolve()
        if rf in seen or not f.exists():
            continue
        seen.add(rf)
        order.append(f)
        try:
            src = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in re.finditer(r"\\(?:input|include|subfile)\s*\{([^}]+)\}", src):
            child = m.group(1).strip()
            cand = root / child
            if not cand.suffix:
                cand = cand.with_suffix(".tex")
            queue.append(cand)
    return order


def score(text: str, raw: str) -> dict:
    words = max(len(text.split()), 1)
    per100 = lambda n: round(n * 100.0 / words, 1)

    sentences = [s for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    lens = [len(s.split()) for s in sentences] or [0]
    mean = sum(lens) / len(lens)
    var = sum((l - mean) ** 2 for l in lens) / len(lens)

    concrete = (len(NUMERIC.findall(text)) + len(CITE.findall(raw))
                + len(REF.findall(raw)) + len(CODEISH.findall(raw)))

    return {
        "words": words,
        "sentences": len(sentences),
        "mean_sentence_len": round(mean, 1),
        "sentence_len_stdev": round(var ** 0.5, 1),
        "groundedness_per_100w": per100(concrete),
        "hedges_per_100w": per100(len(HEDGES.findall(text))),
        "filler_opener": bool(FILLER_OPENERS.match(text)),
        "universal_claims": len(UNIVERSAL.findall(text)),
        "has_citation": bool(CITE.search(raw)),
    }


def triage(sig: dict) -> str:
    """Rank a paragraph for reading order. Never a verdict — a reading queue."""
    if sig["words"] < 25:
        return "skip"
    hits = 0
    if sig["groundedness_per_100w"] < 2.0:
        hits += 2
    elif sig["groundedness_per_100w"] < 5.0:
        hits += 1
    if sig["hedges_per_100w"] > 4.0:
        hits += 1
    if sig["universal_claims"] >= 1:
        hits += 1
    if sig["filler_opener"]:
        hits += 1
    if sig["sentence_len_stdev"] < 4.0 and sig["sentences"] >= 3:
        hits += 1
    if not sig["has_citation"] and sig["words"] > 80:
        hits += 1
    return "read-first" if hits >= 4 else "review" if hits >= 2 else "ok"


def parse_file(path: Path, root: Path, min_words: int):
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as e:
        print(f"  ! cannot read {path}: {e}", file=sys.stderr)
        return []

    paras, buf, start, depth = [], [], None, 0
    section = ""

    def flush():
        nonlocal buf, start
        if buf and start is not None:
            raw = "\n".join(buf)
            text = clean_for_reading(raw)
            if len(text.split()) >= min_words:
                sig = score(text, raw)
                paras.append({
                    "file": str(path.relative_to(root) if root in path.parents
                               or root == path.parent else path),
                    "line_start": start,
                    "line_end": start + len(buf) - 1,
                    "section": section,
                    "text": text,
                    "signals": sig,
                    "triage": triage(sig),
                })
        buf, start = [], None

    for n, raw_line in enumerate(lines, 1):
        line = strip_comments(raw_line)

        begin = re.search(r"\\begin\s*\{([^}]+)\}", line)
        end = re.search(r"\\end\s*\{([^}]+)\}", line)
        if begin and begin.group(1) in SKIP_ENVS:
            flush()
            depth += 1
            continue
        if depth:
            if end and end.group(1) in SKIP_ENVS:
                depth -= 1
            continue

        head = re.search(r"\\(?:sub)*section\s*\*?\s*\{([^}]*)\}", line)
        if head:
            flush()
            section = clean_for_reading(head.group(1))
            continue

        if not line.strip():
            flush()
            continue

        if start is None:
            start = n
        buf.append(line)

    flush()
    return paras


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", help="main.tex, or a directory of .tex files")
    ap.add_argument("-o", "--output", default="paragraphs.json")
    ap.add_argument("--min-words", type=int, default=25,
                    help="ignore paragraphs shorter than this (default 25)")
    args = ap.parse_args()

    target = Path(args.target).expanduser()
    if not target.exists():
        sys.exit(f"Not found: {target}")

    root = target if target.is_dir() else target.parent
    files = collect_files(target)
    if not files:
        sys.exit("No .tex files found.")

    print(f"Scanning {len(files)} file(s) under {root}")
    all_paras = []
    for f in files:
        got = parse_file(f, root, args.min_words)
        all_paras.extend(got)
        print(f"  {f.name}: {len(got)} paragraphs")

    for i, p in enumerate(all_paras, 1):
        p["id"] = f"P{i:03d}"

    counts = {}
    for p in all_paras:
        counts[p["triage"]] = counts.get(p["triage"], 0) + 1

    out = {
        "root": str(root),
        "files": [str(f) for f in files],
        "paragraph_count": len(all_paras),
        "triage_counts": counts,
        "note": ("Triage ranks reading order only. Low groundedness means the "
                 "paragraph asserts without anchoring in data — a writing "
                 "problem worth fixing on its own merits. It is not evidence "
                 "about how the text was produced."),
        "paragraphs": all_paras,
    }
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")

    print(f"\n{len(all_paras)} paragraphs -> {args.output}")
    print("Reading queue: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))


if __name__ == "__main__":
    main()
