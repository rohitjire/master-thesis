---
name: thesis-integrity-check
description: >-
  Pre-submission prose-voice and integrity review for a thesis, paper, or
  chapter — from a PDF, from LaTeX source (main.tex, chapters/*.tex), or both.
  Flags prose that reads as generic, templated, hedge-heavy, or ungrounded,
  rewrites it around the author's own data, and can write those suggestions into
  the .tex as reviewable comment blocks. Also cross-checks citations against the
  bibliography, verifies sources are real (catching fabricated or broken
  references), and flags passages needing attribution. Use whenever the user
  wants writing checked for AI-sounding prose, worries their thesis
  will be flagged by an AI detector or Turnitin, wants their writing to sound
  more specific and more their own, or asks for a plagiarism, citation,
  originality, or "is my thesis clean before I submit" review — even if they just
  point at a thesis PDF or LaTeX folder and say "check it". NOT a Turnitin
  replacement; cannot certify text against any detector, and treats AI-text
  "detection" as a prompt for review, never a verdict.
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
- **No pass can be certified.** If the author asks for a guarantee that their text
  will clear Turnitin's AI detector, say plainly that no local tool can promise
  that — the detector is a closed model whose thresholds change without notice.
  Do the prose work, and be honest that it improves the writing and lowers the
  odds, rather than implying a clean bill of health.
- **The bigger risk for many authors is a false positive.** Detectors misfire
  disproportionately on non-native English writers, whose prose tends to be more
  uniform and more formulaic in exactly the ways these tools score on. If the
  author writes English as a second language, raise this — and point them at the
  defence that actually works, which is **provenance, not polish**: a LaTeX repo
  with months of real commits, a `.bib` that grew over time, raw experiment logs
  and dashboards, dated intermediate drafts. That record settles a challenge in a
  meeting; smooth prose does not. Suggest they start keeping it today if they
  aren't.
- **If the author says they used AI to draft or polish, don't help them hide it.**
  Most European programmes now permit AI language assistance *if declared*, and
  disclosure is usually the cheap, safe path where concealment is the expensive
  one. Point them at their examination regulations and their declaration
  (*Eigenständigkeitserklärung*) requirements. Helping ungrounded prose become
  grounded is legitimate work; laundering authorship is not, and the skill should
  say so once, plainly, without moralising further.

## Workflow

Work through these in order. Don't skip the sanity-checks — automated parsing of a
PDF is approximate, and a confident-but-wrong report is worse than a careful one.

### 1. Locate and extract the document

Check `/mnt/user-data/uploads` for what the author actually gave you. There are
two input modes and they serve different purposes — prefer **both** when
available, since each covers the other's blind spot.

**PDF** — what the examiner and any integrity tool will actually see. Use it for
citation/reference integrity and for page-numbered findings:
```bash
python scripts/extract_pdf.py /mnt/user-data/uploads/<file>.pdf -o /home/claude/extracted_text.txt
```

**LaTeX source** (`main.tex`, `chapters/*.tex`, or a zipped project) — what the
author will actually edit. Required for the prose pass and for inline
annotations, because it gives file+line anchors instead of page numbers:
```bash
python scripts/extract_tex.py /path/to/main.tex -o /home/claude/paragraphs.json
```
The extractor follows `\input`/`\include` from a main file, or takes a directory.
It skips code, math, and tabular environments so listings are never mistaken for
prose, and it emits per-paragraph triage signals — groundedness (numbers, units,
versions, `\cite`, `\ref` per 100 words), hedge density, universal claims, filler
openers, sentence-length uniformity — ranked `read-first` / `review` / `ok`.

**The triage ranking is a reading queue, not a judgement.** It tells you which
paragraphs to read first. Every actual flag comes from your own reading of the
paragraph, never from the score alone. Do not report the scores to the author as
if they measured anything about how the text was written — they measure whether a
paragraph is anchored in evidence, which is a different and more useful thing.

If both inputs are present, confirm they correspond (same chapter titles, similar
length). A stale PDF against edited sources produces confusing findings.

Skim the extracted text either way to learn the document's structure and citation
style before flagging anything.

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

### 4. Machine-sounding / ungrounded prose (the main event when the author asks about AI detection)

Read **`references/ai-prose-patterns.md`** for the pattern catalogue and its
false-positive warnings (many flagged words are perfectly normal in technical
writing; what matters is *clusters* and *lack of grounding*, not single words),
then **`references/rewrite-guide.md`** for how to write a rewrite the author can
actually use.

Work in triage order — `read-first` paragraphs, then `review`, and spot-check a
few `ok` ones to confirm the ranking isn't missing anything. For each flag give:
location (file:line for LaTeX, page for PDF), the short quoted phrase, *why* it
reads as generic — name the pattern — and a **concrete grounding fix** tied to the
author's actual work.

Two rules that matter more than the rest:

- **Never invent the author's numbers.** If you don't have the measured value,
  write the fix as a slot ("give the arrival rate and the p95 you measured at it")
  rather than a plausible-looking figure. A fabricated number pasted into a thesis
  is a far worse outcome than a vague sentence.
- **Never conclude or imply a passage was AI-written.** You cannot know, and the
  claim is not needed for any fix you are recommending.

Calibrate to a handful of flags per chapter. Two hundred flags on a thesis means
the pass failed — the author will act on none of them.

### 4b. Inline annotations in the LaTeX source (when source is available)

If the author wants the suggestions in their `.tex` rather than only in a report,
write the findings to JSON and run the annotator:

```bash
python scripts/annotate_tex.py --findings /home/claude/findings.json \
    --root /path/to/thesis --out-dir /path/to/thesis-annotated
```

Findings JSON: `{"findings": [{"id","file","line","pattern","original","suggest","why"}]}`
where `line` is the paragraph's start line from `paragraphs.json`.

How this behaves, and why:

- Suggestions go in as **LaTeX comments** (`% >>> TIC-VOICE ...`), so they don't
  compile and the PDF is unchanged. Nothing the author wrote is altered.
- **The author accepts a suggestion by editing the sentence themselves.** That is
  deliberate, not friction: the resulting words are then theirs, which is the
  whole point of the exercise.
- Default writes to a **copy**; `--in-place` is opt-in. Before in-place, tell the
  author to commit to git first — that history is also their provenance record.
- `--strip` removes all annotation blocks (verified lossless round-trip);
  `--check` exits non-zero if any remain.

**Always end the annotation workflow by telling the author to run `--check` before
submitting or sharing their source.** Annotation comments left in a submitted
`.tex` are exactly the wrong thing for a supervisor to find, and the comments are
invisible in the compiled PDF, so nothing else will catch them.

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
For each: location (file:line or page) · short quote · pattern · concrete
grounding fix. Group by chapter, severity-ordered within each.
If annotations were written: say where the annotated copy is, and remind the
author to run `--check` before submitting.

## 3. Possible unattributed passages
For each: location · short quote · web-check result · recommended attribution.

## 4. Content & structure suggestions
Per section: what's thin/missing, what to add, why it helps.

## Bottom line
Top 3–5 actions, in priority order.
```

## Notes

- **Lead with what the author asked for.** The report template is ordered
  citations-first, which suits a general check. If the author came specifically
  about AI-sounding prose, put §2 first and say so — don't make them scroll past a
  reference table to reach the thing they asked about.
- **Citation style.** The helper targets numeric (natbib). If the document is
  author–year or a mixed style, say so and parse references by reading.
- **Copyright.** Keep every quoted phrase short (well under 15 words) in both web
  searches and the report. Verify existence; do not reproduce source text.
- **Strictness vs. noise.** Flag aggressively, but cluster style nits and never let
  them outweigh a single broken citation in the summary. Precision builds the
  author's trust in the report.
- **Tone.** The author is doing the responsible thing by self-reviewing. Be direct
  and concrete; assume good faith throughout.
