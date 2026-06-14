#!/usr/bin/env python3
"""
check_citations.py - Cross-reference in-text citations against the bibliography
of a thesis. Tuned for natbib NUMERIC style, e.g. [1], [2, 5], [3-7].

Usage:
    python check_citations.py <extracted_text.txt> [--json out.json]

Reports:
  - orphan citations   (cited in text, but NO bibliography entry)  -> Critical
  - uncited entries     (in the bibliography, but never cited)      -> Warning
  - duplicate bib numbers                                           -> Critical
  - the parsed bibliography entries, so the analyzer can web-verify each one

This is a HELPER, not an oracle. Numeric brackets can be ambiguous (math
intervals, list labels) and PDF extraction can split lines. ALWAYS sanity-check
the detected bibliography boundary and the parse against the actual document
before trusting the numbers.
"""
import re
import sys
import json
import argparse

BIB_HEADING = re.compile(
    r"(?im)^\s*(?:\d+\.?\s+|chapter\s+\d+\s+)?"
    r"(references|bibliography|literaturverzeichnis|literatur|bibliografie|works\s+cited)"
    r"\s*$"
)

# numeric in-text citations: [1], [1, 2], [1,2,5], [3-7], [3–7]
INTEXT = re.compile(r"\[\s*(\d+(?:\s*[,\-–—]\s*\d+)*)\s*\]")

# Bibliography entry-start markers, matched at the start of a line within the bib
# region. Bracket form is the strong default (natbib numeric, IEEE, ACM, etc. all
# render as [n]); the "n." / "n)" form is a fallback, guarded against year-like
# numbers so a wrapped line such as "2022." is never read as a new entry.
BIB_MARKER_BRACKET = re.compile(r"(?m)^[ \t]*\[(\d+)\][ \t]*")
BIB_MARKER_DOT = re.compile(r"(?m)^[ \t]*(\d+)[.\)][ \t]+")


def split_body_and_bib(text):
    matches = list(BIB_HEADING.finditer(text))
    if not matches:
        return text, "", None
    m = matches[-1]  # the last heading is the start of the bibliography
    return text[:m.start()], text[m.end():], m.group(0).strip()


def expand(group):
    nums = set()
    for part in group.split(","):
        part = part.strip()
        rng = re.match(r"^(\d+)\s*[\-–—]\s*(\d+)$", part)
        if rng:
            a, b = int(rng.group(1)), int(rng.group(2))
            if a <= b and b - a < 500:
                nums.update(range(a, b + 1))
        elif part.isdigit():
            nums.add(int(part))
    return nums


def parse_intext(body):
    cited = {}
    for m in INTEXT.finditer(body):
        for n in expand(m.group(1)):
            cited[n] = cited.get(n, 0) + 1
    return cited


def parse_bib(bib):
    """Split the bibliography into full (possibly multi-line) entries by marker.

    Capturing from each marker to the next means a wrapped continuation line
    (e.g. a lone "2022." ending the previous entry) is folded into that entry's
    text rather than mistaken for a new entry.
    """
    entries, dup = {}, []
    markers = list(BIB_MARKER_BRACKET.finditer(bib))
    fmt = "bracket [n]"
    if len(markers) < 2:
        markers = [m for m in BIB_MARKER_DOT.finditer(bib) if int(m.group(1)) < 1000]
        fmt = "numbered n." if markers else "none detected"
    for i, m in enumerate(markers):
        num = int(m.group(1))
        start = m.end()
        end = markers[i + 1].start() if i + 1 < len(markers) else len(bib)
        text = " ".join(bib[start:end].split())  # join wrapped lines
        if num in entries:
            dup.append(num)
        else:
            entries[num] = text
    return entries, dup, fmt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("textfile")
    ap.add_argument("--json")
    args = ap.parse_args()

    with open(args.textfile, encoding="utf-8", errors="replace") as f:
        text = f.read()

    body, bib, heading = split_body_and_bib(text)
    cited = parse_intext(body)
    entries, dup, fmt = parse_bib(bib)

    cited_nums, defined_nums = set(cited), set(entries)
    orphans = sorted(cited_nums - defined_nums)
    uncited = sorted(defined_nums - cited_nums)

    print("=" * 64)
    print("CITATION INTEGRITY  (numeric style)")
    print("=" * 64)
    print(f"Bibliography heading detected: {heading!r}")
    print(f"Bibliography entry format:     {fmt}")
    rng = f"  (numbers {min(defined_nums)}-{max(defined_nums)})" if defined_nums else ""
    print(f"Bibliography entries parsed:   {len(entries)}{rng}")
    print(f"Distinct in-text citations:    {len(cited_nums)}")
    print()
    if not entries:
        print("!! No numbered bibliography entries parsed. The references may use")
        print("   author-year style, or the heading was not found. Inspect the")
        print("   extracted text manually before trusting these results.")
        print()
    print(f"[CRITICAL] Orphans (cited, NO bib entry): {orphans or 'none'}")
    print(f"[WARNING ] Uncited (in bib, never cited): {uncited or 'none'}")
    print(f"[CRITICAL] Duplicate bib numbers:         {sorted(set(dup)) or 'none'}")
    print()

    if entries:
        print("Bibliography entries (first line each) - web-verify each one exists:")
        for n in sorted(entries):
            mark = "" if n in cited_nums else "   [uncited]"
            print(f"  [{n}] {entries[n][:150]}{mark}")

    if args.json:
        with open(args.json, "w", encoding="utf-8") as jf:
            json.dump({
                "heading": heading,
                "format": fmt,
                "num_entries": len(entries),
                "num_intext": len(cited_nums),
                "orphans": orphans,
                "uncited": uncited,
                "duplicates": sorted(set(dup)),
                "entries": {str(k): v for k, v in entries.items()},
                "citation_counts": {str(k): v for k, v in cited.items()},
            }, jf, indent=2, ensure_ascii=False)
        print(f"\nWrote JSON: {args.json}")


if __name__ == "__main__":
    main()
