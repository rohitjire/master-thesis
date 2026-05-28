# Citation hygiene and source traceability

Read this before drafting paragraphs from sources, when introducing a new citation, when the user pastes a source and asks for help, or when handling AI-disclosure questions.

The user is using AI substantively in the writing process. The protection against plagiarism in this workflow is **source traceability** — every factual sentence the skill suggests carries a real, verifiable citation, so the user can verify and the final thesis is properly attributed.

## The contract

- The skill **may draft prose freely** in a CS / engineering researcher voice, including by fetching sources via web search.
- The skill **must** put a citation on every factual sentence it suggests.
- The skill **must never fabricate** a citation, BibTeX entry, or claim about what a source says.
- The user **verifies** each citation against the source, **integrates** the drafted material into their own voice, and **owns** the final text.

## What counts as a "factual sentence" needing a citation

| Claim type | Citation? |
|---|---|
| Specific fact about a system, version, API, or spec ("EDC v0.10.0 uses Vault") | **Yes** — cite the doc/source |
| Architectural claim ("EDC separates control and data plane") | **Yes** — cite the architecture doc |
| Empirical claim from literature ("benchmarks of IDS connectors show...") | **Yes** — cite the benchmark paper |
| Definition of a term ("A dataspace is...") | **Yes** — cite the definition source (IDS-RAM, Gaia-X, etc.) |
| Historical claim ("EDC was developed under the Eclipse Foundation") | **Yes** — cite the project page |
| The user's own measurement or implementation observation | **No external cite** — reference the user's own chapter via `\cref{}` |
| Common knowledge in the field ("data exchange raises trust issues") | **Author's judgment** — flag and let the user decide |
| Original framing or argumentation by the user | **No cite** — flag as the user's own |

## Citation key naming convention

Use `firstauthor-year-shortword` (lowercase, hyphenated). Examples:

- `pohle-2023-edc-spec`
- `ids-ram-2022` (institutional author / well-known doc)
- `eclipse-edc-2024` (organizational author)
- `rfc8037` (RFCs by number)
- `jain-1991-art` (book)
- `fraunhofer-isst-2023-mvd` (institutional report)

When two entries collide, add a discriminator: `pohle-2023-edc-spec-a`, `pohle-2023-edc-spec-b`.

## BibTeX entry types

Use the right entry type — the bibliography style renders differently for each.

```bibtex
@article{author-year-key,
  author    = {Last, First and Other, Author},
  title     = {Title of the article},
  journal   = {Journal Name},
  volume    = {12},
  number    = {3},
  pages     = {100--120},
  year      = {2023},
  doi       = {10.xxxx/yyyy}
}

@inproceedings{author-year-key,
  author    = {Last, First},
  title     = {Title of the paper},
  booktitle = {Proceedings of the X Conference},
  pages     = {1--10},
  year      = {2023},
  publisher = {ACM},
  doi       = {10.xxxx/yyyy}
}

@book{author-year-key,
  author    = {Last, First},
  title     = {Title of the Book},
  publisher = {Publisher},
  year      = {1991},
  edition   = {2nd}
}

@techreport{org-year-key,
  author      = {{International Data Spaces Association}},
  title       = {IDS Reference Architecture Model},
  institution = {International Data Spaces Association},
  number      = {Version 4.0},
  year        = {2022},
  url         = {https://...}
}

@misc{org-year-key,
  author       = {{Eclipse Foundation}},
  title        = {Eclipse Dataspace Components},
  howpublished = {\url{https://projects.eclipse.org/projects/technology.edc}},
  year         = {2024},
  note         = {Accessed: 2025-05-25}
}

@manual{eclipse-edc-2024,
  author       = {{Eclipse Foundation}},
  title        = {EDC Documentation},
  year         = {2024},
  url          = {https://eclipse-edc.github.io/docs/}
}
```

A few notes:
- Wrap institutional authors in double braces: `{{International Data Spaces Association}}` — otherwise BibTeX treats it as "Last, First".
- Always include `url` and `note = {Accessed: YYYY-MM-DD}` for web sources — links rot.
- Use `--` for page ranges (renders as en-dash): `pages = {100--120}`.
- DOIs are nicer than URLs when both are available.

## Marking claim provenance in drafts

When suggesting prose to the user, **tag each suggested sentence's provenance** so they can see what to verify, rewrite, or remove:

```latex
% [FETCHED https://eclipse-edc.github.io/docs/control-plane/]
The EDC control plane handles contract negotiation and policy evaluation \citep{eclipse-edc-2024}.

% [FETCHED RFC 8037]
EdDSA signatures use the JOSE algorithm identifier `EdDSA`, not `Ed25519` \citep{rfc8037}.

% [TRAINING-RECALL — verify before keeping]
The IDS Reference Architecture defines five core layers % TODO: verify count and cite IDS-RAM

% [USER'S OWN WORK]
The patched build is published as `dsp-native-basyx:patched-edDSA` (\cref{sec:implementation-patches}).

% [COMMON KNOWLEDGE — author's judgment]
Data exchange between organizations introduces trust and policy challenges.
```

These comments stay in the user's draft until they verify and remove them — they're scaffolding, not final text.

## Worked examples

### Drafting a paragraph from web-fetched sources

User: *"Help me write a paragraph introducing the Dataspace Protocol in chapter 2."*

A good skill response is to first fetch the actual DSP spec page, then draft with citations:

> *[After web-fetching the Eclipse DSP specification page and the IDS-RAM document]*
>
> Here's a draft. Each sentence cites the actual source I read — verify each against the cited page before keeping. Rewrite in your own voice as the final step.
>
> ```latex
> % [FETCHED https://eclipse-dataspace-protocol-base.github.io/DataspaceProtocol/]
> The Dataspace Protocol (DSP) is an open specification for dataspace participants
> to exchange data and metadata under contractually negotiated policies
> \citep{eclipse-dsp-2024}.
>
> % [FETCHED IDS-RAM 4.0]
> DSP evolves from the IDS Connector communication patterns and aligns the message
> formats with W3C DCAT and ODRL vocabularies \citep{ids-ram-2022, eclipse-dsp-2024}.
>
> % [FETCHED https://eclipse-edc.github.io/docs/]
> The Eclipse Dataspace Components (EDC) provide a reference implementation of DSP,
> structured into a control plane (negotiation, policy evaluation) and a data plane
> (data transfer) \citep{eclipse-edc-2024}.
> ```
>
> Suggested BibTeX entries to add to `bibliography/references.bib`:
>
> ```bibtex
> @misc{eclipse-dsp-2024,
>   author       = {{Eclipse Foundation}},
>   title        = {Dataspace Protocol Specification},
>   howpublished = {\url{https://eclipse-dataspace-protocol-base.github.io/DataspaceProtocol/}},
>   year         = {2024},
>   note         = {Accessed: 2026-05-25}
> }
>
> @techreport{ids-ram-2022,
>   author      = {{International Data Spaces Association}},
>   title       = {IDS Reference Architecture Model},
>   institution = {International Data Spaces Association},
>   number      = {Version 4.0},
>   year        = {2022},
>   url         = {https://docs.internationaldataspaces.org/ids-knowledgebase/v/ids-ram-4}
> }
> ```

The user reads each citation, verifies the claim matches the source, rephrases in their own voice (keeping citations), and pastes the BibTeX into `references.bib`.

### When the user pastes a paragraph from a source

User: *[pastes a paragraph from the EDC documentation]* *"Help me use this in my background section."*

The skill should not rephrase the source verbatim. Instead, it should:

> "Two paths:
>
> 1. **Direct quote** — keep the original wording exactly, wrap it in quotation marks, and cite with a page or URL anchor:
>    ```latex
>    The EDC documentation describes the control plane as ``...the orchestration component
>    that handles contract negotiation, policy evaluation, and asset cataloging''
>    \citep{eclipse-edc-2024}.
>    ```
>    Use this when the original phrasing matters or you want to anchor an authoritative definition.
>
> 2. **Read, close the source, paraphrase from understanding.** This gives you prose in your own structure. Tell me what *you* think the key claim is — what does the control plane actually do, in your understanding? — and I'll help you sharpen it, with the same citation.
>
> Which fits your section better?"

### When the skill is asked to cite something it can't actually source

User: *"Add a citation for 'EDC has been adopted by major automotive OEMs'."*

If the skill doesn't have a real source for this:

> "I don't have a verified source for that adoption claim. Two options:
>
> 1. Tell me where you heard it — a Catena-X announcement, a Fraunhofer report, a press release — and I'll fetch it and write the proper citation.
> 2. Soften the claim to something defensible without a hard source: *'EDC is a reference implementation associated with several automotive dataspace initiatives, notably Catena-X.'* Catena-X's own page is citable; the adoption-by-OEMs framing is harder without a survey.
>
> I'd rather flag the gap than fabricate a citation."

## Verifying citations — the user's job

The skill drafts; the user verifies. A good verification check before any cited claim is finalized:

1. **Does the source actually contain this claim?** Open it. Search for the keyword. Read the paragraph. Confirm.
2. **Is the source authoritative for this claim?** A blog post for an architectural definition is weak; the official spec is strong.
3. **Is the page number / section correct?** If the citation includes `[p.~12]`, page 12 must contain the claim.
4. **Are co-cited sources actually compatible?** When two papers are cited together (`\citep{a, b}`), both must support the synthesized claim.

If a citation fails verification, the user removes it (and the claim it supports, or the claim gets a different source).

## AI disclosure

Many German universities and Fraunhofer-affiliated programs require disclosure of AI tool use. The user should check Fraunhofer ISST / TU Dortmund's current policy with their supervisor.

A reasonable disclosure for this workflow:

> *AI tools were used to assist with literature gathering, paragraph drafting, and LaTeX support. Every cited claim was independently verified by the author against the cited source. The final text, structure, arguments, and contributions are the author's own.*

For this disclosure to be true, the user needs to actually:
- Verify each citation against the source.
- Rewrite drafted prose in their own voice (don't drop AI prose in verbatim).
- Make the structural and argumentative decisions themselves.

If the user hasn't asked their supervisor about disclosure expectations, prompt them to. Some programs require:
- Declaring which AI tools were used.
- Declaring the purposes (literature gathering, drafting, debugging, etc.).
- Keeping a log of significant prompts and outputs.

The conservative move is to disclose more rather than less.
