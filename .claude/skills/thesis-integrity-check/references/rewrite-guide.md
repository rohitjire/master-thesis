# Writing the rewrite

A flag without a usable rewrite is noise. The author will skim it, feel vaguely
bad about the sentence, and change nothing. This guide is about making the
`SUGGEST` line something they can act on in under a minute.

## The core move: replace an adjective with a measurement

Nearly every weak passage in an empirical thesis has the same shape — an
evaluative word standing where evidence should be. *Robust, scalable, efficient,
significant, considerable, effective.* The rewrite finds the number that word was
standing in for and puts it back.

This is why the pass improves the thesis regardless of detectors. An examiner
reading "the system is scalable" has to take it on faith. An examiner reading
"throughput held to 450 req/s before p95 crossed 1 s" can evaluate the claim.
The second sentence is also, incidentally, one that no language model could have
produced without the author's data — but that is a side effect, not the goal.

## Never invent the specifics

**This is the rule that matters most.** The author's numbers are in their logs,
their Grafana dashboards, their notebooks — not in your head. If you don't know
the actual value, write the rewrite as a *slot*, not a fabrication:

- Bad:  "the connector sustained 200 req/s at 340 ms p95"  ← invented, and if the
  author pastes it in, they have put a false number in their thesis
- Good: "give the arrival rate you tested and the p95 you measured at it —
  your Prometheus export has both"

Only use concrete values when they appear in the document you are reviewing or
the author has stated them. When they do appear elsewhere in the thesis, pull
them forward and say where you got them.

## Match the author's voice, not a house style

You are not rewriting the thesis into your own prose. Keep the author's sentence
structure and vocabulary where they work; change only what is hollow. A rewrite
that reads conspicuously smoother than the surrounding text is a bad rewrite —
it creates exactly the register shift the originality pass looks for.

Non-native English phrasing is not a defect. Do not "fix" grammar that is merely
unidiomatic; that is not what this pass is for, and quietly homogenising a
non-native writer's voice is both outside the remit and a disservice.

## Worked examples

**1. Universal claim → measurement**

- Before: "The framework provides a robust and scalable foundation for evaluation."
- After: "The framework sustained the full 30-minute run at each arrival rate
  without dropped samples; §5.3 reports where it saturated."
- Why: "robust" was doing the work of "did not drop samples." Now it is checkable.

**2. Hedge stack → committed claim with a scoped limit**

- Before: "The results may potentially indicate that performance could possibly
  degrade in some cases."
- After: "p95 latency degraded beyond 450 req/s in every run. Whether this holds
  for the in-memory backend was not tested."
- Why: double-hedging usually hides one honest limitation. Name the limitation,
  then commit to what you did measure.

**3. Hollow scaffolding → the actual claim**

- Before: "This section discusses the results of the experiments. Various aspects
  of the evaluation will be considered."
- After: "Contract negotiation, not data transfer, dominates end-to-end latency
  in every configuration tested."
- Why: a topic sentence should state the finding, not announce that a finding is
  coming. This one also gives the section a thesis to defend.

**4. Uncited fact → attributed or owned**

- Before: "Studies have shown that dataspace connectors face significant
  interoperability challenges."
- After (if a source exists): name it — "Reported interoperability gaps between
  connector implementations \cite{...} motivate the compatibility matrix in §3.2."
- After (if it is the author's own observation): "In our deployment, two
  connector versions failed to complete negotiation because of a policy-schema
  mismatch — the case that motivated §3.2."
- Why: "studies have shown" with no citation is the single most examiner-annoying
  construction in academic writing, and it is trivially fixable in both directions.

**5. Filler transition → logical link**

- Before: "Furthermore, the evaluation methodology could be extended."
- After: "Because each run used a single persistence backend, the results do not
  separate connector overhead from database overhead — the obvious extension."
- Why: "Furthermore" asserted a connection. The rewrite states it.

## What not to flag

Do not touch a paragraph just because it is *plain*. Methodology sections are
often flat by necessity — "The VM ran Ubuntu 22.04 with 8 vCPU" is not weak
writing, it is exactly right. Flatness plus specificity is good technical prose.
Flatness plus emptiness is the problem.

Similarly, leave definitions, standard background, and formal statements alone
when they are correctly cited. Not every sentence needs to sparkle.

## Calibration

Aim for the flags an engaged supervisor would raise on a careful read — call it
a handful per chapter. If a 60-page thesis produces 200 flags, the pass has
failed: the author cannot act on 200 items, and burying three real problems in
197 nits means the three go unfixed. Rank by severity and cut the tail.
