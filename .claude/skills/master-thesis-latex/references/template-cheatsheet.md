# Template cheatsheet

A package-by-package summary of what the user's `main.tex` already loads, plus the custom commands and environments. Use this as a quick reference when answering "do we have X?" or "should I use Y or Z?".

## Document class

```latex
\documentclass[12pt,a4paper,english,notitlepage]{report}
```

The `report` class gives `\chapter`, `\section`, `\subsection`, `\subsubsection`. `\chapter` starts a new page automatically. The patch with `etoolbox` removes the large vertical space `report` normally adds above each chapter heading.

`\setcounter{secnumdepth}{3}` and `\setcounter{tocdepth}{3}` mean numbered headings and TOC go down to `\subsubsection`.

## Custom title commands (top of `main.tex`)

These are user-fillable metadata commands. They feed both the title page and the PDF metadata via `hyperref`.

| Command | What to fill |
|---|---|
| `\titelthema` | Thesis title |
| `\authorname` | Author full name |
| `\authormail` | Author email |
| `\authoraddress` | Postal address (used on title page) |
| `\matrikelnr` | Student / matriculation number |
| `\abgabedatum` | Submission date |
| `\betreuer` | Supervisor name |
| `\arbeitstyp` | Type of work (Master's Thesis) |
| `\professor` | Examining professor |

The current values include placeholders (`TBD`, the previous student's name and address). The footer also hardcodes `March, 2025` in `\rfoot{}` — update that separately.

## Layout

- **`geometry`** — A4 with custom margins (35mm left for binding, 25mm right, 25mm top, 19mm bottom, `includefoot`).
- **`setspace` + `\onehalfspacing`** — 1.5 line spacing in the body.
- **`microtype`** — subtle typographic improvements (don't disable; it makes the document look notably more professional).
- **`fancyhdr`** — page headers/footers. Right header is page number, left header is the chapter mark, footer holds author/month and the work type. The footer's `March, 2025` is hardcoded — flag for update.
- **`changepage`** — used for title-page-specific margin adjustments.
- **`pdflscape`** — landscape pages with correct headers/footers. Wrap a page in `\begin{landscape}…\end{landscape}` for a wide table or chart.

## Bibliography

- **`natbib` with `[numbers]` option**, style `\bibliographystyle{plainnat}`.
- Citation commands:
  - `\cite{key}` — `[1]`
  - `\citet{key}` — `Author [1]`
  - `\citep{key}` — `(Author, [1])`
  - `\citeauthor{key}`, `\citeyear{key}` — author or year only
  - `\citep[p.~12]{key}` — with page reference
- `references.bib` is the bib file (loaded as `\bibliography{references}` near the end of `main.tex`).
- The bibliography page uses a different link color (`myblue`) than the rest of the document — set in `\hypersetup{}` just before `\bibliography{}` and reset just after.

**Do not switch to `biblatex`** — it would conflict with `natbib` and require restructuring the bibliography setup.

## Cross-references (`cleveref`)

- Loaded **last** among reference-related packages (this matters; if a new package gets added after it, references can break).
- Use `\Cref{label}` (capitalized for sentence start) and `\cref{label}` (lowercase mid-sentence). Do not use `\ref{}` directly.
- `cleveref` adds the type word automatically — write `\Cref{fig:foo}` not `Figure~\ref{fig:foo}`.

Suggested label prefixes for consistency: `chap:`, `sec:`, `subsec:`, `fig:`, `tab:`, `eq:`, `lst:`, `alg:`.

## Figures and graphics

- **`graphicx`** — `\includegraphics[width=.8\textwidth]{figures/foo.pdf}`. Prefer `.pdf` (vector); fall back to `.png`. Forward slashes in paths even on Windows.
- **`caption`** — configured for hanging caption layout, small font, bold label, 10pt left margin.
- **`subcaption`** — for subfigures (`\begin{subfigure}…\end{subfigure}` inside a `figure`).
- **`pdflscape`** — landscape pages.
- **`float`** — provides the `[H]` placement specifier ("here, no float").

## Tables

- **`tabularx`** — tables with `X` columns that auto-fill width. Useful when text wrapping is needed.
- **`booktabs`** — `\toprule`, `\midrule`, `\bottomrule`. **Replaces all uses of `\hline`.**
- **`threeparttable`** — tables with notes attached (footnotes inside the table). Used for benchmark results with units, std. dev., or methodological notes.
- **`longtable`** — multi-page tables (header repeats on each page).
- **`multirow`** — cells spanning multiple rows.
- **`colortbl`** + custom colors `darkgray`, `lightgray` — colored table cells / row banding.
- **`csvsimple`** — import CSV directly into tables.

### Custom table environments

- **`mytighttable`** — a `table` wrapper with `\arraystretch{1.5}` and 8pt cell padding. Prefer for short, dense data tables — keeps visual consistency across the thesis.

## Code listings

- **`listings`** package, configured with:
  - `basicstyle=\small\ttfamily` (small typewriter)
  - `breaklines=true`
  - `frame=single, frameround=tttt` (rounded single border)
  - `columns=fullflexible`
  - `showstringspaces=false`
  - Line numbers (tiny), light gray background
- **`\renewcommand\lstlistingname{Figure}`** — listings are labeled "Figure" in this template, not "Listing". Keep this consistent unless the user wants to change it (and warn them: changing it affects every `\Cref{lst:...}` in the document).

The `listing` package (singular) is also loaded — provides `\listoflistings`-related machinery; the template renames the listing list to "Quelltextverzeichnis" (which is German — flag this for the user since the thesis is in English).

## Math

- **`amsmath`** — the standard math package (loaded twice in the template; harmless but redundant).
- **`amssymb`**, **`amsfonts`** — extended math symbols and fonts.
- **`algorithm`** + **`algpseudocode`** — pseudocode environments (`\begin{algorithm}…\end{algorithm}` with `algorithmic` block inside).

## Charts (`pgfplots`)

- **`pgfplots`** — native LaTeX plotting (axes, plots, 3D).
- Combined with **`csvsimple`**, plots benchmark CSVs directly. This will be the workhorse for results chapters.
- Large CSVs slow compilation — downsample if rows exceed ~10k or pre-render the plot externally.

## Glossary / acronyms

- **`glossaries`** with options `[acronym, toc, nonumberlist, nogroupskip]`.
  - `acronym` — enable acronyms.
  - `toc` — include the glossary in the table of contents.
  - `nonumberlist` — don't list page numbers next to entries.
  - `nogroupskip` — don't add space between alphabetical groups.
- **Define acronyms in `preamble/acronyms.tex`:**
  ```latex
  \newacronym{key}{SHORT}{Long form}
  ```
- **Define glossary entries in `preamble/glossary.tex`:**
  ```latex
  \newglossaryentry{dataspace}{
    name={dataspace},
    description={A federated infrastructure for ...}
  }
  ```
- Use:
  - `\gls{key}` — auto-expand on first use, short form thereafter.
  - `\Gls{key}` — capitalized first letter (sentence start).
  - `\acrshort{key}` — force short form.
  - `\acrlong{key}` — force long form.
  - `\glsreset{key}` — reset so the next `\gls{key}` expands again (useful at the start of a new chapter).
- A custom style `MystyleSymbole` is defined for a symbol-style glossary using a `longtable` layout. Currently not the default; can be activated with `\setglossarystyle{MystyleSymbole}`.

**`makeglossaries`** must run as a separate step (Overleaf does it automatically; locally needs `latexmk -pdf` or explicit calls). If `\gls{...}` shows as `??`, this is the cause.

**Do not switch to the `acronym` package** — it conflicts with `glossaries` and the existing acronym files.

## Hyperref

- Loaded near the end with `colorlinks=true`, all link colors set to black for the body.
- PDF metadata pulled from `\titelthema`, `\arbeitstyp`, `\authorname` (so the metadata is consistent with the title page).
- `bookmarksopen=true`, `bookmarksnumbered=true` for nice PDF outline.
- Link color switches to blue (`myblue` = RGB 0,0,0.6) only inside the bibliography (and switched back after with `\hypersetup{linkcolor=black,…}`).
- `\urlstyle{rm}` — URLs render in roman, not typewriter.

## Misc utilities

- **`etoolbox`** — used to patch `\@makechapterhead` and remove the large pre-chapter spacing.
- **`enumitem`** — list customization.
- **`multicol`** — multi-column layouts.
- **`afterpage`** — defer commands to after the current page break.
- **`comment`** — `\begin{comment}…\end{comment}` to disable a block.
- **`blindtext`** — lorem-ipsum placeholder text (`\blindtext`) for layout testing. **Do not ship `\blindtext` calls in the final document.**
- **`xcolor`**, **`color`** — colors. Custom: `myblue` (`rgb 0,0,0.6`), `darkgray`, `lightgray`.
- **`url`** — `\url{https://...}` for clickable URLs in body text.

### Custom list environment

- **`myitemize`** — a tighter `itemize`: bullet label, no left indent, no separation between items. Use for compact lists.

## What's NOT loaded (and shouldn't be added without thought)

These are commonly suggested but would conflict:

- **`biblatex`** — would conflict with `natbib`.
- **`acronym`** — would conflict with `glossaries`.
- **`minted`** — alternative listings (with syntax highlighting) — `listings` is already configured; switching means rewriting every `lstlisting` block and configuring Pygments on Overleaf.

These are not loaded but the user might want to add them:

- **`siunitx`** — unit-aware numbers in benchmark tables (`\SI{1245}{\req\per\second}`, `S` column type for aligned decimals). Genuinely useful for performance work — flag the addition and confirm before adding.
- **`placeins`** — `\FloatBarrier` to keep floats from migrating across section boundaries. Useful if figures wander in long chapters.
- **`tikz`** is available implicitly via `pgfplots`, but if standalone TikZ diagrams are needed, you can use `\begin{tikzpicture}…\end{tikzpicture}` directly.

## Encoding

- **`inputenc`** with `utf8`. (The Mac variant `applemac` is commented out.)
- **`fontenc`** with `T1` — proper hyphenation for accented characters.
