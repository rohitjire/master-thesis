---
name: thesis-integrity-check
description: >-
  Strict pre-submission integrity review for a thesis, dissertation, paper, or
  chapter (PDF). Cross-checks every in-text citation against the bibliography and
  verifies cited sources are real (catching fabricated, hallucinated, or broken
  references); flags prose that reads as generic/templated or that an AI-detector
  would penalize, with concrete grounded rewrites; spots passages that may be
  unattributed and need citing; and gives section-by-section content-improvement
  suggestions. Use whenever the user wants to check an academic document for
  plagiarism, AI-generated-content concerns, citation or reference correctness,
  fabricated or missing citations, originality, or a general "is my thesis
  correct/clean before I submit" review — even if they just upload a thesis PDF
  and say "check it". This is NOT a replacement for institutional
  Turnitin/iThenticate, and AI-text "detection" is treated as a heuristic prompt
  for review, never a verdict.
compatibility: "Requires code execution (Python: pdfplumber/pypdf) and web access for reference/originality verification."
---

# Thesis Integrity Check

A strict, pre-submission self-review tool for academic documents. It surfaces the
problems an examiner, a reviewer, or an integrity tool would catch — broken or
fabricated citations, claims with no support, prose that reads as machine-written,
and passages that may need attribution — and tells the author exactly how to fix
each one.

## The honest stance (state this in every report)

Be straight with the user about what this is. Getting this right protects them far
more than inflated confidence would.

- **It is not a Turnitin/iThenticate replacement.** True plagiarism detection
  compares the document against billions of sources. A skill cannot replicate that
  corpus. This tool does *targeted* verification of suspicious passages and full
  verification of the reference list, plus internal consistency — useful, but not
  exhaustive. Tell the user to still run their institution's official check.
- **"AI detection" is not reliable, and this tool does not fake a score.** There is
  no robust way to prove text was machine-written, and the tools that output a
  percentage misfire badly on non-native English writing — they would flag genuine,
  hand-written prose. So this tool never says "this was AI-generated." Instead it
  flags *specific passages that read as generic, templated, or ungrounded* and shows
  how to make them concrete and unmistakably the author's. Those fixes improve the
  thesis regardless of who or what reads it.
- **Flags are prompts for review, not accusations.** Every finding is something for
  the author to look at and decide on.

## Workflow

Work through these in order. Don't skip the sanity-checks — automated parsing of a
PDF is approximate, and a confident-but-wrong report is worse than a careful one.

### 1. Locate and extract the document
Find the uploaded PDF (check `/mnt/user-data/uploads`). Extract text with page
markers so every finding can cite a page:
```bash
python scripts/extract_pdf.py /mnt/user-data/uploads/<file>.pdf -o /home/claude/extracted_text.txt
```
Skim the extracted text to confirm extraction worked (LaTeX PDFs usually extract
cleanly) and to learn the document's structure and citation style.

### 2. Citation & reference integrity (the backbone)
Run the cross-reference helper on the extracted text:
```bash
python scripts/check_citations.py /home/claude/extracted_text.txt --json /home/claude/citations.json
```
It is tuned for **natbib numeric** style (`[1]`, `[2, 5]`, `[3–7]`). Then:

- **Sanity-check its parse before trusting it.** Open the extracted text and confirm
  the detected bibliography boundary is correct and that the bracketed numbers it
  read are really citations (numeric brackets can be math intervals or list labels).
  If the document is author–year style, the helper will report few/no entries — in
  that case parse the references by reading instead.
- **Report orphans and padding.** Orphan citations (cited in text, no bib entry) are
  **Critical**. Entries in the bibliography never cited are **Warnings** (padding, or
  a citation that got dropped).
- **Check formatting consistency** across entries (author order, date placement,
  page/DOI presence) — inconsistency reads as carelessness to examiners.
- **Flag claims that need a citation but have none.** Empirical numbers, definitions
  presented as established fact, "it is well known that…", and direct comparisons to
  prior work should all carry a source. List the specific sentences.

### 3. Verify references actually exist (web)
Fabricated or hallucinated references are the single most damaging integrity finding,
so verify each one. For every bibliography entry, `web_search` the title plus first
author; if a DOI/URL is given, confirm it resolves and points to that work.
Classify each:

- **Verified** — found, and author/year/venue match.
- **Mismatch (Warning)** — found, but details are wrong (e.g. wrong year, wrong
  authors, wrong venue, DOI points elsewhere). Often an honest citation error; still
  needs fixing.
- **Not found (Critical)** — no trace of the work anywhere. Treat as a possible
  fabrication and tell the user to re-check the source in their own library.

Volume note: a full thesis may have 80–150 references — verifying all of them can
exceed ~30 searches. For a single chapter this is fine. For a whole thesis, verify
every entry that looks suspicious (no DOI, odd venue, too-perfect title, unfamiliar
author) plus a sample of the rest, say so explicitly in the report, and offer an
exhaustive pass on request. Only confirm existence — never reproduce source content.

### 4. Machine-sounding / ungrounded prose
Read `references/ai-prose-patterns.md` first — it is the catalogue of patterns and,
crucially, the false-positive warnings (many flagged words are perfectly normal in
technical writing; what matters is *clusters* and *lack of grounding*, not single
words). Then scan the body and flag specific passages. For each flag give: the short
quoted phrase, its location, *why* it reads as generic, and a **concrete grounding
fix** tied to the author's actual work (their measured numbers, tool versions, config
values, named components). Never conclude or imply the passage was AI-written.

### 5. Originality / possible unattributed passages
Look for register shifts (a paragraph suddenly more polished or textbook-like than
its surroundings) and boilerplate definitions that read as lifted. For each
candidate, take one **short, distinctive phrase** (a handful of words — never a large
block) and `web_search` it to see whether it traces to a source the author should be
citing or quoting. If it matches: recommend attribution or quotation. If not: leave
it. Keep all quotes in the report short (copyright). Repeat that this pass is not
exhaustive and not a substitute for the institutional check.

### 6. Content & structure improvements
Section by section, note what is thin or missing and exactly what to add — e.g. a
methodology missing its experimental configuration table, a results section with no
threats-to-validity discussion, a claim that needs a figure. Be specific and
actionable, not generic ("expand this"); say what content and why it strengthens the
argument.

### 7. Assemble and deliver the report
Build the markdown report (template below) and save it to
`/mnt/user-data/outputs/`, then present it. Lead with the honesty block and a
severity summary so the author can triage.

## Severity tiers

Keep hard problems visually separate from polish so "strict" doesn't bury the author.

- **🔴 Critical** — orphan/broken citation, a reference that can't be found (possible
  fabrication), a central claim with no support, a passage that appears copied without
  attribution. These can fail an integrity review; fix before submission.
- **🟡 Warning** — uncited padding, mismatched reference details, formatting
  inconsistency, prose generic enough to undermine credibility.
- **🔵 Suggestion** — specificity, structure, and polish that would strengthen the
  thesis but isn't a defect.

## Report structure

ALWAYS use this template:

```markdown
# Integrity Review — <document title>
*Scope: <whole thesis / chapter N>. Reference verification: <full / prioritized>.*

> **Read this first.** This is a pre-submission self-review, not a Turnitin
> replacement, and it does not "detect AI" — it flags ungrounded prose and
> verifies your references. Treat every item as a prompt to check, not a verdict.
> Still run your institution's official integrity check.

## Summary
🔴 Critical: N  🟡 Warning: N  🔵 Suggestion: N
<two or three sentences on the overall state>

## 1. Citations & references
### Orphan / broken citations 🔴
### Uncited / padding 🟡
### Reference verification (web)
| # | Reference (short) | Status | Note |
### Claims needing a citation
### Formatting consistency

## 2. Machine-sounding / ungrounded prose
For each: location · short quote · why flagged · concrete grounding fix.

## 3. Possible unattributed passages
For each: location · short quote · web-check result · recommended attribution.

## 4. Content & structure suggestions
Per section: what's thin/missing, what to add, why it helps.

## Bottom line
Top 3–5 actions, in priority order.
```

## Notes

- **Citation style.** The helper targets numeric (natbib). If the document is
  author–year or a mixed style, say so and parse references by reading.
- **Copyright.** Keep every quoted phrase short (well under 15 words) in both web
  searches and the report. Verify existence; do not reproduce source text.
- **Strictness vs. noise.** Flag aggressively, but cluster style nits and never let
  them outweigh a single broken citation in the summary. Precision builds the
  author's trust in the report.
- **Tone.** The author is doing the responsible thing by self-reviewing. Be direct
  and concrete; assume good faith throughout.
