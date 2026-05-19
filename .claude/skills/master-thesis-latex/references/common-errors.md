# Common LaTeX errors in this template

Triage by symptom. Always start by asking for the relevant lines from `main.log` — the actually-useful line is usually 1–10 lines after a line starting with `! `.

## `\gls{...}` shows as `??` in the PDF, or the glossary page is empty

**Cause:** `makeglossaries` (or `makeindex`) hasn't been run on `main.glo` / `main.acn`.

**Fix:**
- **Overleaf:** usually does this automatically. If not, in Overleaf: Menu → Settings → Compiler → set to `pdfLaTeX` with `latexmk` (default). Force a recompile from scratch (Menu → Recompile from scratch / clear cache).
- **Locally:** run `pdflatex main && makeglossaries main && pdflatex main && pdflatex main`, or simpler: `latexmk -pdf main`. The `latexmkrc` should be aware of glossaries — if not, add:
  ```
  add_cus_dep('glo', 'gls', 0, 'makeglossaries');
  add_cus_dep('acn', 'acr', 0, 'makeglossaries');
  sub makeglossaries { system("makeglossaries \"$_[0]\""); }
  ```

## Citations show as `[?]`

**Cause:** `bibtex` pass hasn't run after the first `pdflatex`, or the bib file isn't found.

**Fix:**
- Run the right pass sequence: `pdflatex → bibtex → pdflatex → pdflatex`. `latexmk -pdf main` does this for you.
- On Overleaf, this is automatic — if it's still failing, look at `main.blg` for BibTeX errors.

## "Citation `Smith2020` undefined"

**Cause:** the key isn't in `references.bib`, or `references.bib` isn't on a path the bibliography command can find.

**Fix:**
- Check the call: `\bibliography{references}` in `main.tex`. If `references.bib` is in `bibliography/`, change to `\bibliography{bibliography/references}` — or move the file to repo root.
- Check the key in the `.bib` file — typos and case sensitivity bite here (`Smith2020` vs `smith2020`).
- A clean rebuild (delete `main.bbl` and recompile) sometimes fixes stale state.

## "Undefined control sequence \\Cref"

**Cause:** `cleveref` was loaded too early (before `hyperref`), or another package was loaded after it that breaks reference handling.

**Fix:** in this template `cleveref` is already loaded last among reference-related packages. If a new package was added after it, move that addition to before `cleveref` — or move `cleveref` back to the bottom.

## Figure not showing / "File `figures/foo' not found"

**Cause:** missing extension, wrong path, or wrong slash direction.

**Fix:**
- Prefer `.pdf` for vector figures, then `.png` for raster. The path in `\includegraphics` can omit the extension if the file format is supported.
- Use forward slashes even on Windows: `figures/foo.pdf` not `figures\foo.pdf`.
- Check the file actually exists at that path. Case sensitivity matters on Linux/Overleaf even if Windows let you slide.

## "Float too large for page"

**Cause:** a figure or table is taller than the text area.

**Fix:**
- Scale the figure: `\includegraphics[width=.8\textwidth, keepaspectratio]{...}` or `[height=.8\textheight]`.
- For tables: use `\small` or `\footnotesize`, or switch to `longtable` for genuinely long tables.
- For wide tables/figures: use `\begin{landscape}…\end{landscape}` from `pdflscape`.

## Document compiles but new chapter doesn't appear

**Cause:** chapter not `\input`ed in `main.tex`.

**Fix:** add the line `\input{chapters/09_my_new_chapter}` (no `.tex` extension) at the right place in the chapter list at the bottom of `main.tex`.

## Float placement / pagination weirdness near figures and tables

**Cause:** float placement is fighting `\onehalfspacing` and chapter boundaries.

**Fix:**
- Add `[H]` (force here, requires `float` — already loaded) or `[!htbp]` to figure/table specs to give LaTeX more flexibility.
- For figures that wander into the next chapter, add `\FloatBarrier` (from `placeins`, not currently loaded — confirm with the user before adding) before the chapter end.
- Consider using `\afterpage{\clearpage}` to defer a clear-page until after the current page break.

## Build hangs or runs forever in Overleaf

**Cause:** often `pgfplots` parsing a large CSV.

**Fix:**
- If a CSV has more than ~10k rows, downsample before plotting. Aggregate per-second-bucket or per-percentile rather than plotting raw points.
- Pre-render the chart externally (Python + matplotlib, R, etc.) and `\includegraphics` the result.
- `pgfplots` with `mark=none` and reasonable point density compiles much faster than dense scatter plots.

## "TeX capacity exceeded"

**Cause:** usually a runaway macro or a missing `\end{...}`.

**Fix:** check `main.log` for the last successful line. The error usually points one or two `\end`s away from the actual issue — work backward through the most recent `\begin{...}` to find a missing `\end`.

## `! Misplaced alignment tab character &.`

**Cause:** an `&` outside a tabular/array/eqnarray context, or one too many `&` inside a row.

**Fix:** count the `&`s in each row; for a 3-column table, each row should have exactly 2 `&`s (separating 3 columns) and end with `\\`. Escape literal ampersands in body text as `\&`.

## `! Missing $ inserted.`

**Cause:** math symbol used outside math mode (e.g., `_` or `^` in body text).

**Fix:** wrap with `$...$` or escape: `\_`, `\^{}`. Especially common with file paths and code-like content in prose.

## `Overfull \hbox` warnings

**Cause:** a line is too long to break naturally — usually a long URL, a long unhyphenated word, or a wide inline math expression.

**Fix:**
- For URLs: wrap in `\url{...}` (already loaded).
- For long words: add manual hyphenation hints with `\-` (e.g., `Bench\-marking`).
- For wide math: break into multiple lines with `align` from `amsmath`.
- These are warnings, not errors — small overflow (< 5pt) is often safe to ignore.

## Diff between Overleaf and local builds

**Cause:** different LaTeX distributions, package versions, or pass order.

**Fix:**
- Match Overleaf's TeX Live version locally (Overleaf shows it in Settings).
- Use `latexmk` everywhere to standardize the pass order.
- If still diverging, share both `main.log` files for comparison — the warnings section often reveals which pass is misbehaving.

## How to read `main.log` quickly

1. Search for `! ` (exclamation + space). That's a fatal error.
2. Look at the next 1–10 lines — the actual cause is usually quoted there.
3. The line `l.123` near an error means line 123 of whichever file is "current" — often a chapter file under `chapters/`, not `main.tex` itself. The log also names the file just above `l.123`.
4. Warnings (`Overfull \hbox`, `Underfull \hbox`, `Package … Warning`) are non-fatal but worth fixing once content is stable.
5. The very end of the log shows package totals and final compile stats — useful for spotting unusually long compile times.
