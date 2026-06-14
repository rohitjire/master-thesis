# Machine-sounding / ungrounded prose — pattern catalogue

Use this to flag passages that read as generic, templated, or ungrounded. The point
is not to "catch AI" — that can't be done reliably, and pretending otherwise would
flag genuine writing. The point is that grounded, specific, citation-backed prose is
both better scholarship *and* far less likely to trip an AI-detector or raise an
examiner's eyebrow. Every flag should come with a concrete fix that makes the
sentence more specific and more clearly the author's own.

## Read this before flagging: avoid false positives

The biggest risk is over-flagging. Most of the "tells" below are also perfectly
normal in academic and technical writing. So:

- **Flag clusters, not single words.** One "robust" or "leverage" is nothing — a
  paragraph that is *all* connective filler and zero specifics is the signal.
- **Grounding beats vocabulary.** The real question for any passage is: does it say
  something concrete and verifiable, or could it have been written about any topic by
  someone who knew nothing? A sentence packed with the author's actual numbers, tool
  versions, and component names is fine no matter which words it uses.
- **Respect the genre.** "Robust," "leverage," "framework," "significant,"
  "implement," "architecture" are core CS vocabulary. Don't flag them as such.
- **Respect the author's English.** Non-native phrasing is not an AI tell. Never flag
  something merely because it sounds slightly formal or non-idiomatic.

When in doubt, don't flag it. A short, precise list of real problems is worth far
more than a long list the author will dismiss.

## Patterns

### 1. Connective filler doing no work
Transitions used as scaffolding rather than logic: *Moreover, Furthermore, In
addition, Additionally, Overall, It is important to note that, It is worth noting
that, As mentioned previously.* A little is fine; back-to-back paragraphs that all
open this way, or sentences whose only content is the transition, are the tell.
**Fix:** cut the transition or replace it with the actual logical link ("because
X, Y" / "this fails when Z").

### 2. Universal claims with no specifics
*Plays a crucial/vital/pivotal/key role; in today's rapidly evolving landscape; a
wide range of; various; numerous; significant (with no number); has gained
significant attention; is of paramount importance.* These could be written about
anything. **Fix:** replace the vague claim with the specific fact — the measured
value, the named system, the actual count.

### 3. Hedge stacking
*May potentially, could possibly, it can be argued that, generally tends to, in some
cases may.* Double-hedging signals the writer isn't standing behind a claim. **Fix:**
commit to what the evidence shows, or cite the source of the uncertainty.

### 4. Hollow scaffolding sentences
Topic sentences that only announce ("This section discusses…"), and summary
sentences that only restate ("In conclusion, as discussed above…"), with no content
in between. **Fix:** make the topic sentence state the section's actual claim;
make the summary state the actual finding.

### 5. Thin parallelism / list padding
*Firstly… Secondly… Thirdly…* or a tricolon ("efficient, scalable, and reliable")
where each item is asserted but never substantiated. Real enumeration is good; empty
enumeration is filler. **Fix:** give each item a concrete basis, or collapse the list.

### 6. Over-explaining the obvious / restating the prompt
Defining common terms the audience knows, or restating the question before answering
it. **Fix:** delete; trust the reader.

### 7. Uniform, detail-free rhythm
Paragraphs of near-identical length and cadence, every claim general, *no* concrete
detail anywhere — no numbers, units, version strings, configuration values, dataset
sizes, component or method names. This is the strongest signal. **Fix:** inject the
specifics the author actually has. In an empirical thesis these belong on nearly
every page (measured latencies and percentiles, request/arrival rates, sample sizes,
hardware, software versions, exact component and state names, parameter values).

### 8. Claims presented as fact without a citation
"It is well known that…", "Studies have shown…", "It is widely accepted that…" with
no reference. **Fix:** add the specific source, or soften to the author's own
observation. (Overlaps with the citation-integrity pass — list these there too.)

### 9. LLM-favored vocabulary (only as a weak, secondary signal)
Words that *cluster* in machine output: *delve, tapestry, boasts, underscore,
showcase, realm, seamless, holistic, multifaceted, intricate, pivotal, testament,
landscape (figurative), navigate (figurative), foster, garner, paramount.* Treat a
dense cluster of these — especially alongside patterns 1, 2, and 7 — as worth a look.
A single one in otherwise grounded prose is **not** worth flagging.

## How to write each flag

For every flagged passage, give exactly:
1. **Location** (page / section).
2. **Short quote** (a few words — never a large block).
3. **Why** it reads as generic — name the pattern.
4. **Concrete grounding fix** — what specific content of the author's would replace
   or anchor it. This is the most valuable part; make it actionable, not "be more
   specific."

Example flag:

- **§4.2, p.31** — "the system delivers robust and scalable performance across a wide
  range of conditions." *Pattern 2 + 7: universal claim, no specifics.* Anchor it to
  the data: which conditions (which persistence backend, which arrival rate), and the
  measured numbers (e.g. p95 latency, throughput) that justify "robust" and
  "scalable." As written it could describe any system; with the numbers it becomes a
  finding.
