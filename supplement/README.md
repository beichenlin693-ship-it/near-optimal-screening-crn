# Supplementary machine-readable evidence

Complete aggregate matrices are in `../results/machine_readable/`:

- `formal/`: all formal WNBA and Gaussian cells, preservation, selected-policy
  distributions, recommendation contrasts, CRN diagnostics and finite-reference
  summaries/uncertainty diagnostics.
- `robustness/`: tolerance sets/metrics, structural references/performance/CPC
  diagnostics, non-Gaussian metrics and the reused Gaussian comparator.
- `external/`: all direct comparator summaries, recommendation extensions and
  independently estimated contrast intervals.
- `main_table_rows/`: exact display strings for the five main tables. These
  rounded editorial rows supplement rather than replace full-precision results.

CSV identifiers `CPC-v2` and `epsilon-CPC-SH` identify the adaptive CPC method;
`CPC-v1` identifies the bounded-confidence comparator displayed as “Bounded CPC”.
These strings are unchanged record keys, not claims of novelty. ON/OFF is encoded
as true/false in `crn`. `M` or `macro_replications` counts selections per cell;
reference-path counts are separate. WNBA success/loss quantities are plug-in
finite-reference metrics. Gaussian means are known by construction.

PGS concerns the final choice; preservation concerns the whole near-optimal set.
EOC is expected opportunity cost, and normalized EOC uses the specified calibration
scale. Wilson intervals describe selection proportions; Student intervals describe
mean losses; exact binomial bounds also accompany removal errors. Pair-specific
variance-reduction intervals and external mean intervals use their original
bootstrap conventions. No stored bootstrap is rerun by this release.

NA/empty cells remain missing or unidentified; they must not be treated as zero.
The two external Gaussian CPC incomplete removal records remain in denominators
and yield identification bounds. B1/B2 marginal intervals do not describe a
paired between-method contrast. Shared/reused baseline cells are not pooled as
new independent evidence. See `reproducibility/traceability.csv` for display links.

Unpublished paper PDFs, the narrative supplement, copied publisher papers and
working-history directories are intentionally absent.
