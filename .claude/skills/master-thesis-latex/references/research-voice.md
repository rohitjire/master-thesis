# Research voice and tone for the thesis

The user wants the thesis to read like CS / engineering research writing — not like an undergraduate essay, not like marketing copy, not like default LLM academic register. This file is the voice reference. Read it before drafting any paragraph of prose.

## What CS / engineering research voice sounds like

A few principles:

1. **Claim, evidence, implication.** State what's true, cite the support, note what follows.
2. **Specific over vague.** Versions, named components, concrete configs. "EDC v0.10.0 uses HashiCorp Vault for credential storage" not "modern connectors use secure storage".
3. **Verbs that mean something.** "Implements", "validates", "measures", "extends" — not "leverages", "utilizes", "facilitates", "enables" (unless they're literally accurate).
4. **Active where the actor matters, passive where it doesn't.**
    - Active: "The control plane validates the token." (Who does it matters.)
    - Passive: "Throughput was measured over a 60-second window." (Who measured is less important than what was measured.)
5. **Hedge with purpose, not by reflex.** "Suggests", "is consistent with", "may indicate" when results are noisy or interpretation is uncertain. Don't stack hedges. *"Perhaps possibly might suggest"* is noise.
6. **Acknowledge limitations.** Strong research voice owns its constraints. "This measurement does not isolate network from connector processing latency; see \cref{sec:limitations} for threats to validity."
7. **Use precise technical vocabulary.** DSP, MVD, Identity Hub, Catalog Server — these have specific meanings. Define on first use via `\gls{}`, then use the short form.
8. **Numbers come with units, ranges with context.** "Mean throughput 1245 req/s (p99: 38ms, n=10, 60s window)" not "throughput was high".

## What to strip — LLM-default tells

These phrases signal LLM-default academic register. Cut them on sight:

- "It is important to note that..."
- "In today's rapidly evolving / digital / data-driven world..."
- "Leveraging cutting-edge technologies..."
- "Paradigm-shifting / paradigm shift / new paradigm"
- "Robust and scalable solutions"
- "Empowering organizations to..."
- "Seamless integration"
- "Holistic approach"
- "Plays a crucial / pivotal / key role"
- "A multitude of"
- "Delve into"
- "It goes without saying..."
- "Furthermore" and "moreover" stacked at the start of consecutive sentences

When you catch yourself drafting any of these, rewrite the sentence with concrete content. "EDC plays a pivotal role in dataspace adoption" → "EDC is the most widely deployed reference implementation of the Dataspace Protocol \citep{...}." (And cite a real adoption survey or remove the claim.)

## Worked examples

### Background section

**✅ Good:**

> The Eclipse Dataspace Components (EDC) provide a reference implementation of the Dataspace Protocol \citep{eclipse-edc-2024, eclipse-dsp-2024}. EDC separates the control plane, which handles contract negotiation and policy evaluation, from the data plane, which performs the actual data transfer \citep{eclipse-edc-2024}. This separation enables independent scaling of negotiation and transfer workloads — relevant for performance analysis, as the two paths have distinct latency and throughput characteristics (\cref{sec:methodology}).

Why this works: each claim cited, specific (named components, named protocols), the implication ("relevant for performance analysis") is the user's framing and points to their own methodology.

**❌ Bad:**

> EDC is a powerful and flexible framework that plays a pivotal role in the modern data economy. By leveraging cutting-edge technologies, it empowers organizations to seamlessly share data in a paradigm-shifting way that is reshaping how enterprises think about data sovereignty.

Why this fails: no citations, no concrete claims, every phrase is filler register.

### Methodology section

**✅ Good:**

> Throughput was measured under a constant request rate of 100 req/s for 60 seconds, with a 30-second warmup phase discarded before measurement \citep{jain-1991-art}. Each configuration was run five times in randomized order to mitigate ordering effects (\cref{tab:throughput-results}). The 60-second window was chosen to balance measurement stability against total experiment runtime; preliminary runs showed steady-state behavior emerging within 20 seconds of warmup (\cref{fig:warmup-profile}).

Why this works: specific (numbers, duration, repetitions), cites a methodology source, explains design choices, references the user's own results.

**❌ Bad:**

> A series of comprehensive benchmarks were conducted to robustly evaluate the performance characteristics of the connector, ensuring statistical significance through careful experimental design.

Why this fails: no concrete details, "comprehensive" and "robustly" are claims with no support, no methodology source, no parameters.

### Results section

**✅ Good:**

> The patched build (`dsp-native-basyx:patched-edDSA`, \cref{sec:nimbus-patch}) successfully validated EDC-issued tokens in 100% of 500 trials, compared to a 0% success rate on the unpatched baseline (\cref{tab:patch-validation}). Mean validation latency increased from 4.2 ms (baseline, failed validations) to 7.8 ms (patched, successful validations), reflecting the additional BouncyCastle code path.

Why this works: specific numbers, references the user's own implementation and tables, the implication follows from the data.

**❌ Bad:**

> The patch significantly improved validation performance and enabled successful token validation in the dataspace environment, demonstrating the effectiveness of the proposed approach.

Why this fails: "significantly", "successfully", "effectiveness" are unquantified; "demonstrating" overstates what one experiment shows.

## Conventions for measurement reporting

When the thesis reports performance measurements (this will be most of it), follow these conventions:

- **State the metric, the conditions, the sample size, and the variability.** "Mean throughput 1245 req/s (sd 38, n=10, 60s window)".
- **Use percentiles for latency, not just mean.** p50, p95, p99 — heavy-tailed distributions are common. "p99 latency 184 ms" tells a different story than "mean latency 38 ms".
- **Always include units.** `req/s`, `ms`, `MB/s`, `cores`, `GiB`. Consider `siunitx` for typographically consistent units (would be a new package — confirm before adding).
- **Distinguish nominal from measured.** "Nominal 100 req/s" — what was requested. "Measured 97.2 req/s" — what actually happened.
- **State the test environment.** Hardware (CPU model, cores, RAM), software (kind version, EDC version, JVM version), workload (request pattern, payload size). Once at the start of the chapter, then refer back.
- **Plots before tables for trends; tables before plots for exact values.** A reader scans a plot and looks up specific numbers in a table.

## Conventions for describing the user's own implementation

The user has built substantial implementation work. When describing it:

- **Use past tense for what was done, present tense for what is.** "We patched `MvdValidationService` to fall back to BouncyCastle" (past, the action) vs. "The patched validator uses BouncyCastle for EdDSA verification" (present, the resulting system).
- **First person plural ("we") or impersonal — match the supervisor's preference.** German theses often use impersonal ("the author", "this work"); English CS theses often use "we". Ask the supervisor; pick one; be consistent.
- **Reference code by file path and class/method.** "`MvdValidationService.validateToken()` in `dataspace-protocol-lib`" — specific enough that a reader could find it.
- **Be honest about scope.** "This work patches the validator for `EdDSA`; the underlying Nimbus library issue persists upstream and is reported as [issue link]." Don't overclaim.

## When to break the rules

Voice conventions exist to serve communication. Break them when needed:

- A topic sentence that opens a chapter doesn't need a citation if it's framing the user's own argument.
- "We" can step out of impersonal voice when describing decisions the author made (research design, scope, prioritization).
- A short, punchy sentence can land harder than a measured one. Use sparingly.

But the defaults are: specific, cited, hedged with purpose, technical, honest about limits.
